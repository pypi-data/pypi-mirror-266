from ipaddress import ip_address
import logging
from time import sleep
from urllib.parse import quote
from proxmoxer import ProxmoxAPI
from ezinfra.sshkeys import get_ssh_pubkey_from_privatekey, get_privatekey_from_string
from ezinfra.remote import ssh_run_command, wait_for_ssh
from ezlab.utils import ezapp, get_new_vm_name

logger = logging.getLogger("ezinfra.pve")


def connect(host, username, password):
    result = None
    try:
        result = ProxmoxAPI(
            host,
            user=username,
            password=password,
            verify_ssl=False,
        )
    except Exception as error:
        return error

    return result


def vms():
    return ezapp.connection.cluster.resources.get(type="vm")


def pools():
    return ezapp.connection.cluster.resources.get(type="storage")


def networks():
    return ezapp.connection.cluster.resources.get(type="sdn")


# def bridges(fromtemplatename):
#     if not fromtemplatename or fromtemplatename == "":
#         return []

#     try:
#         template = next(iter([t for t in vms() if t["template"] and t["name"] == fromtemplatename]))
#     except IndexError:
#         return []

#     return ezapp.connection.nodes(template["node"]).network.get(type="any_bridge") if template else []


def bridges(fromtemplateid):
    if not fromtemplateid or fromtemplateid == "":
        return []

    try:
        template = next(iter([t for t in vms() if t["template"] and t["id"] == fromtemplateid]))
    except IndexError:
        return []

    return ezapp.connection.nodes(template["node"]).network.get(type="any_bridge") if template else []


def clone(
    resources: tuple,
    settings: dict,
    # vm_number: int,
    vm_count: int,
    dryrun: bool,
):
    template, volume, bridge, eznode, hostname, first_ip = resources

    response = {}
    response["commands"] = []
    response["task"] = f"Clone {vm_count} VMs for {eznode['name']}"
    response["settings"] = settings
    response["info"] = ""
    response["files"] = {}

    node = template["node"]
    template_type = template["type"]
    template_id = template["vmid"]

    vm_gateway = settings["gateway"]
    vm_network_bits = settings["cidr"].split("/")[1]
    privatekey: str = settings["privatekey"]

    # cloudinit requires OpenSSH format public key
    pk = get_privatekey_from_string(privatekey)
    publickey = get_ssh_pubkey_from_privatekey(pk)

    for vm_number in range(vm_count):
        multivm = vm_count > 1
        if multivm:
            vm_name = get_new_vm_name(hostname, vm_number)
        else:
            vm_name = hostname

        response[
            "info"
        ] += f"""
        Clone {vm_name} with disks:
            OS Disk: {eznode["os_disk_size"]}G
            Swap Disk: {eznode['swap_disk_size']}G
            Data Disks (qty: {eznode["no_of_disks"]}): {eznode['data_disk_size'] if 'data_disk_size' in eznode else 0}G
            """

        if not dryrun:
            logger.info("[ %s ] cloning...", vm_name)
            # wait for others to request vmid, used when run for multiple VMs in parallel
            sleep(vm_number * 1)
            nextid = ezapp.connection.cluster.nextid.get()
            logger.info("[ %s ] assigned id %s", vm_name, nextid)

        ipconfig = "ip="
        vm_ip = ""
        if first_ip == "dhcp":
            ipconfig += "dhcp"
        else:
            vm_ip = str(ip_address(first_ip) + vm_number if multivm else ip_address(first_ip))  # adjust for single VM
            ipconfig += f"{vm_ip}/{vm_network_bits}"
            ipconfig += f",gw={vm_gateway}"

        if not dryrun:
            logger.info("[ %s ] (%s) creating", vm_name, nextid)
            try:
                result = task_waitfor(
                    ezapp.connection,
                    node,
                    ezapp.connection.nodes(node)(template_type)(template_id).clone.post(
                        newid=nextid,
                        name=vm_name,
                        description=eznode["name"],
                    ),
                )
                if result:
                    new_vm = ezapp.connection.nodes(node)(template_type)(nextid)
                    logger.info("[ %s ] cloned", vm_name)
                else:
                    logger.warning("Clone failed for %s: %s", vm_name, result)
                    return False

            except Exception as error:
                logger.warning("PVE Exception for %s: %s", vm_name, error)
                return False

        if dryrun:
            response["files"].update(
                {
                    f"{vm_name}-ciconfig": f"""
                    cores={eznode["cores"]},
                    memory={eznode["memGB"] * 1024},
                    net0=virtio,bridge={bridge},firewall=0,
                    ipconfig0={ipconfig},
                    tags={eznode["product"]},
                    ciuser={settings["username"]},
                    cipassword=******,
                    nameserver={settings["nameserver"]},
                    searchdomain={settings["domain"]},
                    ciupgrade=0,
                    sshkeys={quote(publickey, safe="")},
                    onboot=1,
                    efidisk0={volume["storage"]}:1,efitype=4m,pre-enrolled-keys=1,size=4M",
                    """,
                }
            )

        else:
            # configure vm
            logger.info("[ %s ] reconfigure", vm_name)
            try:
                new_vm.config.post(
                    cores=eznode["cores"],
                    memory=eznode["memGB"] * 1024,
                    net0=f"virtio,bridge={bridge},firewall=0",
                    ipconfig0=ipconfig,
                    tags=eznode["product"],
                    ciuser=settings["username"],
                    cipassword=settings["password"],
                    nameserver=settings["nameserver"],
                    searchdomain=settings["domain"],
                    ciupgrade=0,
                    sshkeys=quote(publickey, safe=""),
                    onboot=1,
                    efidisk0=f"{volume['storage']}:1,efitype=4m,pre-enrolled-keys=1,size=4M",
                )
                logger.info("[ %s ] reconfigured", vm_name)
            except Exception as error:
                logger.warning("PVE Exception for %s: %s", vm_name, error)
                return False

        if not dryrun:
            logger.info("[ %s ] add disks", vm_name)
            try:
                # configure disks
                new_vm.resize.put(disk="scsi0", size=f"{eznode['os_disk_size']}G")
                # add swap disk
                swap_disk = f"{volume['storage']}:{eznode['swap_disk_size']},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"
                new_vm.config.post(scsi1=swap_disk)

                logger.info("[ %s ] %dGB swap disk added", vm_name, eznode["swap_disk_size"])
                # add data disks
                data_disk = f"{volume['storage']}:{eznode['data_disk_size'] if 'data_disk_size' in eznode else 0},backup=0,discard=on,cache=unsafe,iothread=1,replicate=0,ssd=1"

                disks = {}
                for diskno in range(eznode["no_of_disks"]):
                    # adding 2 since 0 is OS, 1 is SWAP
                    disks.update({"scsi" + str(diskno + 2): data_disk})

                # add all data disks at once, using (scsi2=xxx, scsi3=xxx) as params
                new_vm.config.post(**disks)

                logger.info("[ %s ] disks attached", vm_name)

            except Exception as error:
                logger.warning("PVE Exception for %s: %s", vm_name, error)
                return False

            # start vm
            new_vm.status.start.post()

            logger.info("[ %s ] waiting startup...", vm_name)

            # # apply customisations to vm
            if not wait_for_ssh(vm_ip, settings["username"], settings["privatekey"]):
                logger.warning(f"[ %s ] SSH FAILED", vm_ip)
                return False

            # Setup swap space
            for out in ssh_run_command(
                host=vm_ip,
                username=settings["username"],
                keyfile=settings["privatekeyfile"],
                command="sudo mkswap /dev/sdb; sudo swapon /dev/sdb",
            ):
                logger.info("[ %s ] swap on: %s", vm_name, out)
                UUID = out.split(" UUID=")[1]
                if UUID:
                    for out in ssh_run_command(
                        host=vm_ip,
                        username=settings["username"],
                        keyfile=settings["privatekeyfile"],
                        command=f"echo 'UUID={UUID} none swap sw,nofail 0 0' | sudo tee -a /etc/fstab",
                    ):
                        logger.debug("add swap to fstab %s", out)

            # # reboot for changes
            # if task_waitfor(
            #     proxmox=ezapp.connection,
            #     node=node,
            #     task_id=new_vm.status.reboot.post(timeout=60),
            # ) == TASK_FINISHED:
            #     sleep(30) # allow VM to reboot
            #     logger.info("[ %s ] ready for %s", vm_name, eznode["product"])
            #     return True

            logger.info("[ %s ] Finished", vm_name)

    return response if dryrun else True


def task_waitfor(proxmox, node, task_id):
    task_submitted = proxmox.nodes(node).tasks(task_id).status.get()
    if task_submitted["status"] == "stopped":
        return task_submitted["exitstatus"]

    try:
        status = proxmox.nodes(node).tasks(task_id).status.get()
        while status["status"] != "stopped":
            logger.debug("PVE task status: %s is %s", status["type"], status["status"])
            sleep(3)
            status = proxmox.nodes(node).tasks(task_id).status.get()
    except Exception as error:
        logger.warning("TASK WAIT FAILED: %s", error)
        return False

    return True
