# Generate cloud-init files


def cloudinit_userdata(
    hostname: str,
    fqdn: str,
    ssh_username: str,
    ssh_password: str,
    ssh_pubkey: str,
    swap_disk: str,
):
    return f"""
#cloud-config
hostname: {hostname}
manage_etc_hosts: true
fqdn: {fqdn}
user: {ssh_username}
password: {ssh_password}
ssh_authorized_keys:
  - {ssh_pubkey}
chpasswd:
  list: |
    {ssh_username}:{ssh_password}
    root:{ssh_password}
  expire: False
ssh_pwauth: true
disable_root: false

# users:
#   - default

fs_setup:
  - device: {swap_disk}
    filesystem: swap
mounts:
  - ["{swap_disk}", "none", "swap", "sw,nofail,x-systemd.requires=cloud-init.service", "0", "0"]

"""


def cloudinit_metadata(hostname: str):
    return f"""
instance-id: {hostname}
local-hostname: {hostname}"""


def cloudinit_networkconfig(interface: str, ip_address: str, network_bits: int, gateway: str, nameserver: str, searchdomain: str):
    return f"""version: 1
config:
  - type: physical
    name: {interface}
    subnets:
      - type: static
        address: {ip_address}/{network_bits}
        gateway: {gateway}
        dns_nameservers:
          - {nameserver}
        dns_search:
         - {searchdomain}
"""
