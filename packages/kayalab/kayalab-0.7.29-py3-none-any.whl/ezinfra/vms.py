import logging
from ezinfra.proxy import proxy_files
from ezinfra.remote import sftp_content_to_file, ssh_run_command
from ezinfra.repo import get_epel_repo, get_insecure_registry, get_local_repo
from ezlab.parameters import DF, GENERIC, KVM, PVE, SETUP_COMMANDS
from ezinfra import pve
from ezinfra import kvm


logger = logging.getLogger("ezinfra.vms")


def prepare(
    hostname: str,
    hostip: str,
    settings: dict,
    addhosts: list,
    add_to_noproxy: str,
    prepare_for: str,
    dryrun: bool,
):
    """
    Configure VMs for selected product, taking care of pre-requisites
    Params:
        <hostname>      : VM hostname
        <hostip>        : VM IP address (should be reachable)
        <settings>      : Dictinary of configuration from app settings
        <addhosts>      : Other hosts to add to /etc/hosts file, dict{'ip', 'name'}
        <add_to_noproxy>: add to no_proxy (comma separated hosts/IPs)
        <prepare_for>   : EZUA | EZDF | DFAAS | Generic
        <dryrun>        : Do not execute but report

    Returns <bool>     : True in succesful completion, False otherwise. If dryrun, returns dict of job run
    """

    response = {}

    if dryrun:
        response["task"] = (
            f"Prepare {hostname} ({hostip}) for {prepare_for} {'with hosts: ' + ','.join([h for h in addhosts]) if len(addhosts) > 0 else 'as single node'}"
        )
        response["settings"] = settings

    domain = settings["domain"]
    cidr = settings["cidr"]
    username = settings["username"]
    # password = settings["password"]
    keyfile = settings["privatekeyfile"]
    # commands to execute, always prepend with generic/common commands, such as enable password auth, disable subscription mgr etc.
    commands = list(SETUP_COMMANDS[GENERIC])
    if prepare_for != GENERIC:
        commands += list(SETUP_COMMANDS[prepare_for])
    after_generic_commands = len(list(SETUP_COMMANDS[GENERIC]))

    files = {}
    # "/etc/cloud/templates/hosts.redhat.tmpl": f"127.0.0.1 localhost.localdomain localhost\n{hostip} {hostname}.{domain} {hostname}\n"

    # ensure shortname (no fqdn)
    hostname = hostname.split(".")[0]
    hosts = [
        "127.0.0.1 localhost.localdomain localhost",
        f"{hostip} {hostname}.{domain} {hostname}",
    ]
    # + [f"{socket.gethostbyname(h)} {h}" for h in addhosts]

    files = {"/etc/hosts": "\n".join(hosts)}

    # update env files for proxy
    noproxy = f"{hostip},{add_to_noproxy}" if add_to_noproxy is not None else hostip

    if settings.get("proxy", "").strip() != "":
        for file in proxy_files(settings["proxy"], domain, cidr, noproxy):
            files.update(file)

    # TODO: Not tested, enable insecure registry
    if settings.get("airgap_registry", "").strip() != "" and settings["airgap_registry"].split("://")[0] == "http":
        files.update({"/etc/docker/daemon.json": get_insecure_registry(settings["airgap_registry"])})

    repo_content = ""
    if settings.get("yumrepo", "").strip() != "":
        for repo in ["BaseOS", "AppStream", "PowerTools", "extras"]:
            repo_content += get_local_repo(repo, settings.get("yumrepo")) + "\n"

    else:
        logger.debug("Using system repositories")

    if settings.get("epelrepo", "").strip() != "":
        repo_content += get_epel_repo(settings.get("epelrepo"))

    else:
        epel_default = "sudo subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms; sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm"
        commands.insert(after_generic_commands, epel_default)

    if repo_content != "":  # yum or epel repo given
        files.update({"/etc/yum.repos.d/local.repo": repo_content})

    if dryrun:
        response["files"] = files
    else:
        try:
            for filepath, content in files.items():
                logger.info("[ %s ] COPY %s", hostname, filepath)
                for result in sftp_content_to_file(
                    host=hostip,
                    username=username,
                    keyfile=keyfile,
                    content=content,
                    filepath=filepath,
                ):
                    logger.debug("[ %s ] COPYOUT: %s", hostname, result)

        except Exception as error:
            logger.warning("SFTP FAIL: %s", error)
            return False

    if settings.get("yumrepo", "").strip() != "" or settings.get("epelrepo", "").strip() != "":
        commands.insert(
            after_generic_commands,
            "sudo dnf config-manager --set-disabled baseos appstream extras; sudo dnf config-manager --set-disabled 'rhel-8-*'",
        )

    if settings.get("proxy", "").strip() != "":
        commands.insert(
            after_generic_commands + 1,
            "sudo sed -i '/proxy=/d' /etc/dnf/dnf.conf > /dev/null; echo proxy={proxy_line} | sudo tee -a /etc/dnf/dnf.conf >/dev/null".format(
                proxy_line=(settings["proxy"] if settings["proxy"][-1] == "/" else settings["proxy"] + "/")
            ),
        )

    # set hostname for fqdn - required for DF
    if prepare_for == DF:
        commands.insert(after_generic_commands + 2, f"sudo hostnamectl set-hostname {hostname}.{domain}")

    if dryrun:
        response["commands"] = commands

    else:
        try:
            for command in commands:
                logger.info("[ %s ] SSH: %s", hostname, command)
                for output in ssh_run_command(host=hostip, username=username, keyfile=keyfile, command=command):
                    logger.debug("[ %s ] %s", hostname, output)
        except Exception as error:
            logger.warning("SSH FAIL %s", error)
            return False

    return response if dryrun else True


def clone(
    target: str,
    resources: set,
    settings: dict,
    # vm_number: int,
    vm_count: int,
    dryrun: bool,
):

    if target == PVE:
        return pve.clone(
            resources=resources,
            settings=settings,
            # vm_number=vm_number,
            vm_count=vm_count,
            dryrun=dryrun,
        )
    elif target == KVM:
        return kvm.clone(
            resources=resources,
            settings=settings,
            # vm_number=vm_number,
            vm_count=vm_count,
            dryrun=dryrun,
        )
    else:
        logger.debug("Unknown target %s", target)
        return False
