# /usr/bin/python3

from ipaddress import ip_address
import logging
import os
import string
import libvirt
from libvirt import *
from xml.etree import ElementTree as ET
from ezinfra.cloudinit import cloudinit_metadata, cloudinit_networkconfig, cloudinit_userdata
from ezinfra.sshkeys import get_privatekey_from_string, get_ssh_pubkey_from_privatekey
from ezinfra.remote import sftp_copy_file, wait_for_ssh
from ezlab.utils import create_ci_iso, ezapp

logger = logging.getLogger("ezinfra.kvm")


def connect(host: str, username: str):
    try:
        if host in ["localhost", "127.0.0.1"]:
            target = "qemu:///session"

        else:
            where = "session" if host == "localhost" else "system"
            target = f"qemu+ssh://{username}@{host}/{where}"

        conn = open(target)
    except libvirt.libvirtError as e:
        print(f"ERROR IN CONNECT: {e}")
        return e

    return conn


def vms():
    domainIDs = ezapp.connection.listDomainsID()
    if domainIDs == None or len(domainIDs) == 0:
        return list()
    else:
        for domainID in domainIDs:
            yield domainID


def bridges():
    return [n.bridgeName() for n in [ezapp.connection.networkLookupByName(net) for net in ezapp.connection.listNetworks()]]


def pools():
    pools = ezapp.connection.listAllStoragePools()
    if not pools:
        return list()
        # raise SystemExit("Failed to locate any StoragePool objects.")

    # return pools
    return [pool for pool in pools if pool.isActive() == True]


def volumes(pool):
    if pool is None:
        return list()

    sp = ezapp.connection.storagePoolLookupByName(pool)

    if sp is None:
        return list()
    else:
        return [vol for vol in sp.listVolumes() if ".qcow2" in vol or ".img" in vol]


def sp_basepath(sp):
    raw_xml = sp.XMLDesc(0)
    tree = ET.ElementTree(ET.fromstring(raw_xml))

    return tree.find("target").find("path").text


def get_storagepool(poolname):
    return ezapp.connection.storagePoolLookupByName(poolname)


def clone(
    resources: set,
    settings: dict,
    # vm_number: int,
    vm_count: int,
    dryrun=True,
):
    """
    Clone VM
    """

    response = {}
    response["settings"] = settings

    dom = None

    # Parse inputs
    (pool, baseimg, bridge, eznode, hostname, first_ip) = resources

    privatekey: str = settings["privatekey"]
    ssh_keyfile: str = settings["privatekeyfile"]

    pk = get_privatekey_from_string(privatekey)
    publickey = get_ssh_pubkey_from_privatekey(pk)
    # kvm_host = ezapp.connection.getHostname()
    _, host = ezapp.connection.getURI().split("://")
    kvm_username, kvm_target = host.split("@")
    kvm_host, _ = kvm_target.split("/")

    sp = get_storagepool(pool)
    # host path for storage pool
    sp_path = sp_basepath(sp)
    baseimgPath = sp.storageVolLookupByName(baseimg).path()

    for vm_number in range(vm_count):

        multivm = vm_count > 1
        vm_name = hostname + str(vm_number if multivm else "")
        vm_domain = settings["domain"]
        vm_ip = str(ip_address(first_ip) + vm_number if multivm else ip_address(first_ip))  # adjust for single VM
        vm_gateway = settings["gateway"]
        vm_network_bits = settings["cidr"].split("/")[1]

        if dryrun:
            logger.info("Would clone %s from %s", vm_name, baseimg)
        else:
            logger.info("[ %s ] cloning...", vm_name)

        # Cloud-init files
        cloudinit_files = {
            # meta-data
            "meta-data": cloudinit_metadata(hostname=vm_name),
            # user-data
            "user-data": cloudinit_userdata(
                hostname=vm_name,
                fqdn=f"{vm_name}.{vm_domain}",
                ssh_username=settings["username"],
                ssh_password=settings["password"],
                ssh_pubkey=publickey,
                swap_disk="/dev/vdb",
            ),
            # network-config
            "network-config": cloudinit_networkconfig(
                interface="ens1" if "ubuntu" in baseimg.lower() else "eth0",
                ip_address=vm_ip,
                network_bits=vm_network_bits,
                gateway=vm_gateway,
                nameserver=settings["nameserver"],
                searchdomain=vm_domain,
            ),
        }

        response[
            "task"
        ] += f"""
        Clone {vm_name}:
            OS Disk: {eznode["os_disk_size"]}G
            Swap Disk: {eznode['swap_disk_size']}G
            Data Disks (qty: {eznode["no_of_disks"]}): {eznode['data_disk_size'] if 'data_disk_size' in eznode else 0}G
            Disk Location {kvm_host}:{sp_path}/{vm_name}/
            """
        response["files"] = cloudinit_files

        # copy cloudinit files
        if not dryrun:
            logger.info("[ %s ] uploading cloud-init files...", vm_name)

            # need absolute path for filename
            isofile = os.path.abspath(f"{vm_name}-ci.iso")

            try:
                create_ci_iso(files=cloudinit_files, destfile=isofile)

                sftp_copy_file(
                    host=kvm_host,
                    username=kvm_username,
                    keyfile=ssh_keyfile,
                    source=isofile,
                    destfile=f"{sp_path}/{vm_name}-ci.iso",
                )

            except Exception as error:
                logger.warning("Failed to copy cloudinit %s", error)
                return False

            finally:
                try:
                    os.remove(isofile)
                except OSError:
                    pass

            logger.info("[ %s ] creating disks...", vm_name)

            # OS disk, backed by image
            create_osvol(
                sp=sp,
                volname=f"{vm_name}-os.qcow2",
                sizeGB=eznode["os_disk_size"],
                baseimg=baseimgPath,
            )

            # swap disk
            create_datavol(
                sp=sp,
                volname=f"{vm_name}-swap.qcow2",
                sizeGB=eznode["swap_disk_size"],
            )

            # data disk(s)
            for i in range(eznode["no_of_disks"]):
                create_datavol(
                    sp=sp,
                    volname=f"{vm_name}-data{i}.qcow2",
                    sizeGB=eznode["data_disk_size"],
                )

        # Define VM
        vmXml = vm_xml(
            name=vm_name,
            memMB=int(eznode["memGB"] * 1024),
            cores=eznode["cores"],
            basepath=sp_path,
            baseimgPath=baseimgPath,
            bridge=bridge,
            no_of_datadisks=int(eznode["no_of_disks"]),
        )

        if dryrun:
            response["commands"] = [
                f"""virsh dom create <<EOF
                    {vmXml}
                EOF
                """
            ]
        else:
            logger.info("[ %s ] creating vm...", vm_name)
            try:
                dom = ezapp.connection.defineXMLFlags(vmXml, 0)

            except Exception as error:
                logger.warning("Failed at VM definition %s: %s", vm_name, error)
                return False

        # Update dns entry in virtualnet
        if dryrun:
            response[f"commands"].append(f"echo '{vm_ip} {vm_name}.{vm_domain}, {vm_name}' >> /etc/hosts")
        else:
            # ### THIS IS WRONG, NIC SHOULD BE DETACHED/ATTACHED ON ALL RUNNING INSTANCES
            try:
                logger.info("[ %s ] Update libvirt dns", vm_name)
                virnet = [
                    ezapp.connection.networkLookupByName(net)
                    for net in ezapp.connection.listNetworks()
                    if ezapp.connection.networkLookupByName(net).bridgeName() == bridge
                ].pop()
                if virnet:
                    dnshostXml = f"<host ip='{vm_ip}'><hostname>{vm_name}</hostname></host>"
                    if (
                        virnet.update(
                            command=libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST,
                            section=libvirt.VIR_NETWORK_SECTION_DNS_HOST,
                            parentIndex=-1,
                            xml=dnshostXml,
                            flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG | libvirt.VIR_DOMAIN_AFFECT_LIVE,
                        )
                        == 0
                    ):
                        logger.info("[ %s ] dns entry added for %s", vm_name, vm_ip)
                    else:
                        logger.info("[ %s ] dns update failed for %s, ignoring", vm_name, vm_ip)
                else:
                    logger.info("[ %s ] dns update failed for %s, are you using a bridge?", vm_name, vm_ip)

            except Exception as error:
                logger.warning("[ %s ] Failed to update virtualNetwork: %s, ignoring...", vm_name, error)

        # Create/Boot VM
        if not dryrun:
            logger.info("[ %s ] starting...", vm_name)
            try:
                if dom.create() < 0:
                    logger.warning("[ %s ] failed to create: %s", vm_name, error)
                    return False

                logger.info("[ %s ] booting", vm_name)
                dom.setAutostart(1)  # turn on autostart
            except Exception as error:
                logger.warning("[ %s ] failed to boot: %s", vm_name, error)
                return False

            logger.info("[ %s ] waiting startup...", vm_name)
            if not wait_for_ssh(f"{vm_name}.{vm_domain}", settings["username"], ssh_keyfile):
                logger.warning("[ %s ] ssh failed", dom.name())
                return False

            logger.info("[ %s ] ready for %s", dom.name(), eznode["product"])

    return response if dryrun else True


def vm_xml(name: str, memMB: int, cores: int, basepath: str, baseimgPath: str, bridge: str, no_of_datadisks: int):

    datadisks = ""
    letters = string.ascii_lowercase
    start_letter = letters.index("c")  # starting from /dev/vdc

    for i in range(no_of_datadisks):
        diskname = f"vd{letters[start_letter + i]}"
        datadisks += f"""
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' discard='unmap'/>
      <source file='{basepath}/{name}-data{i}.qcow2'/>
      <backingStore/>
      <target dev='{diskname}' bus='virtio'/>
      <alias name='virtio-disk{i+2}'/>
    </disk>
"""

    return f"""
<domain type="kvm">
  <name>{name}</name>
  <metadata>
    <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
      <libosinfo:os id="http://rockylinux.org/rocky/8"/>
    </libosinfo:libosinfo>
  </metadata>
  <memory unit='MiB'>{memMB}</memory>
  <currentMemory unit='MiB'>{memMB}</currentMemory>
  <memoryBacking>
    <source type='memfd'/>
    <access mode='shared'/>
  </memoryBacking>
  <vcpu placement='static'>{cores}</vcpu>
  <features>
    <acpi/>
    <apic/>
    <vmport state='off'/>
  </features>
  <resource>
    <partition>/machine</partition>
  </resource>
  <sysinfo type='smbios'>
    <system>
      <entry name='serial'>ds=nocloud</entry>
    </system>
  </sysinfo>
  <os>
    <type arch='x86_64' machine='pc-q35-6.2'>hvm</type>
    <boot dev='hd'/>
    <smbios mode='sysinfo'/>
  </os>
  <devices>
    <clock offset="utc"/>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' discard='unmap'/>
      <source file='{basepath}/{name}-os.qcow2'/>
      <backingStore type='file'>
        <format type='qcow2'/>
        <source file='{baseimgPath}'/>
        <backingStore/>
      </backingStore>
      <target dev='vda' bus='virtio'/>
      <alias name='virtio-disk0'/>
    </disk>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' discard='unmap'/>
      <source file='{basepath}/{name}-swap.qcow2'/>
      <backingStore/>
      <target dev='vdb' bus='virtio'/>
      <alias name='virtio-disk1'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='{basepath}/{name}-ci.iso'/>
      <backingStore/>
      <target dev='sda' bus='sata'/>
      <readonly/>
      <alias name='sata0-0-0'/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    {datadisks}
    <interface type="bridge">
      <source bridge="{bridge}"/>
    </interface>
    <input type="mouse" bus="ps2"/>
    <graphics type="vnc" autoport="yes" listen="127.0.0.1"/>
    <console type="pty">
      <source>
        <clipboard copypaste="yes"/>
      </source>
      <target type="virtio"/>
    </console>
    <memballoon model='virtio'/>
    <rng model='virtio'>
      <backend model='random'>/dev/urandom</backend>
      <alias name='rng0'/>
    </rng>
  </devices>
</domain>
"""


def create_datavol(sp: virStoragePool, volname: str, sizeGB: int):
    volXml = f"""
        <volume>
          <name>{volname}</name>
          <allocation>0</allocation>
          <capacity unit="GiB">{sizeGB}</capacity>
          <target>
            <format type='qcow2'/>
            <permissions>
              <mode>0644</mode>
              <label>virt_image_t</label>
            </permissions>
          </target>
        </volume>"""

    return sp.createXML(volXml, 0)


def create_osvol(sp: virStoragePool, volname: str, sizeGB: int, baseimg: str):
    volXml = f"""
        <volume>
          <name>{volname}</name>
          <allocation>0</allocation>
          <capacity unit="GiB">{sizeGB}</capacity>
          <target>
            <format type='qcow2'/>
            <backingStore type='file'>
                <format type='qcow2'/>
                <source file='{baseimg}'/>
                <backingStore/>
            </backingStore>
            <permissions>
              <mode>0644</mode>
              <label>virt_image_t</label>
            </permissions>
          </target>
        </volume>"""

    return sp.createXML(volXml, 0)


# def get_network_with_new_host(network: virNetwork, hostname: str, ip: str):

#     # <dns>
#     #   <host ip='192.168.122.2'>
#     #     <hostname>myhost</hostname>
#     #   </host>
#     # </dns>

#     raw_xml = network.XMLDesc(0)
#     tree = ET.ElementTree(ET.fromstring(raw_xml))
#     dnsDom = tree.find("dns")
#     if not dnsDom:
#         print("add dns entry")
#         dnsDom = ET.Element("dns")
#         tree.getroot().append(dnsDom)

#     else:
#         # check if ip exist (append host if so)
#         existing_ip = [h for h in dnsDom if h.get("ip") == ip]
#         if len(existing_ip) > 0:
#             hostElement = existing_ip[0]
#             if hostElement.find("hostname").text == hostname:
#                 # nothing to change
#                 return None
#             else:
#                 newhost = ET.Element("hostname")
#                 newhost.text = hostname
#                 hostElement.append(newhost)

#     # new host entry
#     newhost = ET.Element("hostname")
#     newhost.text = hostname
#     newip = ET.Element("host", ip=ip)
#     newip.append(newhost)
#     dnsDom.append(newip)

#     return ET.tostring(tree.getroot(), 'unicode')


# def get_nicXml(dom: virDomain, bridge: str):
#     tree = ET.ElementTree(
#         ET.fromstring(dom.XMLDesc(0))
#     )
#     root = tree.getroot()

#     interfaces = root.findall("./devices/interface")
#     nic = [nic for nic in interfaces if nic.find("source").attrib.get("bridge") == bridge].pop()

#     return ET.tostring(nic, 'unicode')


#         netXml = get_network_with_new_host(virnet, vm_name, vm_ip)
#         if netXml is not None:
#             virnet.destroy()
#             virnet.undefine()
#             network = ezapp.connection.networkDefineXML(netXml)
#             if network == None:
#                 print("Failed to create network", netXml)
#             else:
#                 network.create()
#                 network.setAutostart(1)
#                 # remove/attach VM nic
#                 nicXml = get_nicXml(dom, bridge)
#                 dom.dev
#                 dom.attachDeviceFlags(nicXml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
