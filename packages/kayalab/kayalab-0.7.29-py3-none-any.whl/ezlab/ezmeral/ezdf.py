from paramiko import AutoAddPolicy, SSHClient
from ezinfra.remote import sftp_content_to_file, ssh_run_command
from ezinfra.repo import get_mapr_repo
from ezlab.utils import *
from ezlab.parameters import *
from paramiko_expect import SSHClientInteraction


logger = logging.getLogger("ezdf")


def cluster_install(
    hosts: list[str],
    settings: dict,  # settings from "config" key
    config: dict,  # settings from "EZDF" key
    dryrun: bool = True,
):
    hostnames = []
    name = config.get("cluster_name", "ezlab")
    disks = config.get("maprdisks", "/dev/sdz")

    response = {}
    if dryrun:
        response["task"] = f"Create Data Fabric cluster {name} on {','.join(hosts)} using disk(s) {disks}"
        response["settings"] = settings

    # lazy way to catch exceptions
    try:
        username = settings.get("username")
        # used for connecting to nodes from this app
        keyfile = settings.get("privatekeyfile")
        # used for connection between cluster nodes
        password = settings.get("password")

        # get fqdn for each host
        if dryrun:

            def get_hostname_command(host):
                return f"ssh {settings.get('username')}@{host} 'hostname -f'"

            response["commands"] = [get_hostname_command(host) for host in hosts]

        else:
            for host in hosts:
                for result in ssh_run_command(
                    host=host.strip(),
                    username=username,
                    keyfile=keyfile,
                    command="hostname -f",
                ):
                    hostnames.append(result)

        commands: list[str] = INSTALL_COMMANDS[DF]

        if config.get("maprrepoislocal", False):
            # using local repository for mapr packages
            ezrepo: str = config.get("maprlocalrepo", "").rstrip("/")
            repouser = config["maprlocalrepousername"]
            repopass = config["maprlocalrepopassword"]

            wgetauthstring = f"--user={repouser} --password={repopass}" if config.get("maprlocalrepoauth", False) else ""

            proto, path, *_ = ezrepo.split("://")
            repourl = f"{proto}://{repouser}:{repopass}@{path}" if config.get("maprlocalrepoauth", False) else ezrepo

            commands.insert(
                0,
                f"[ -f /tmp/mapr-setup.sh ] || wget -q {wgetauthstring} {ezrepo.rstrip('/')}/installer/redhat/mapr-setup.sh -P /tmp; chmod +x /tmp/mapr-setup.sh",
            )

            commands.insert(
                1,
                f"curl -s -k https://127.0.0.1:9443/ > /dev/null || (sudo /tmp/mapr-setup.sh -y -r {repourl.rstrip('/')} && echo 'Sleeping to let installer to be ready' && sleep 30)",
            )

        else:
            # using HPE repository
            ezrepo = f"https://package.ezmeral.hpe.com/releases"
            repouser = config["maprrepouser"]
            repotoken = config["maprrepotoken"]

            commands.insert(
                0,
                f"[ -f /tmp/mapr-setup.sh ] || wget -q --user={repouser} --password= {repotoken} {ezrepo.rstrip('/')}/installer/redhat/mapr-setup.sh -P /tmp; chmod +x /tmp/mapr-setup.sh",
            )

            commands.insert(
                1,
                f"curl -s -k https://127.0.0.1:9443/ > /dev/null || (sudo /tmp/mapr-setup.sh -y --repo-user {repouser} --repo-token {repotoken} && echo 'Sleeping to let installer to be ready' && sleep 30)",
            )

        first_host = hosts[0].strip()

        # using this to provide UI link to the installer
        commands.insert(2, f"echo 'Installer ready at https://{first_host}:9443/'")

        # Create and upload stanza file
        stanza = get_mapr_stanza(
            hosts=hostnames,
            username=username,
            password=password,
            disks=disks.split(","),
            cluster_name=name,
        )

        if dryrun:
            stanza = get_mapr_stanza(
                hosts=hosts,
                username=username,
                password=password,
                disks=disks.split(","),
                cluster_name=name,
            )
            response["files"] = {"/tmp/mapr.stanza": stanza}

        else:
            logger.info("[ %s ] COPY /tmp/mapr.stanza", first_host)
            # print(f"[ {first_host} ] COPY /tmp/mapr.stanza")
            for result in sftp_content_to_file(
                host=first_host,
                username=username,
                keyfile=keyfile,
                content=stanza,
                filepath="/tmp/mapr.stanza",
            ):
                logger.debug("[ %s ]: %s", first_host, result)

            logger.info("[ %s ] starting installer", first_host)

        if dryrun:
            response["commands"].extend(commands)

        else:
            for command in commands:
                logger.info("[ %s ] RUN %s", first_host, command)
                for result in ssh_run_command(
                    host=first_host,
                    username=username,
                    keyfile=keyfile,
                    command=command,
                ):
                    logger.debug("[ %s ] %s", first_host, result)
                    if "Installer ready at" in result:
                        APP_STATUS_CONTAINER.append((f"{name.upper()} Installer", f"https://mapr:mapr@{first_host}:9443/"))
                        status_container.refresh()

            logger.info(
                "Cluster ready at https://%s:8443/",
                first_host,
            )
            APP_STATUS_CONTAINER.append((f"{name.upper()} MCS", f"https://mapr:mapr@{first_host}:8443/app/mcs/"))
            status_container.refresh()

    except Exception as error:
        logger.warning("Cluster creation exception: %s", error)
        if dryrun:
            return response
        else:
            return False

    if dryrun:
        return response
    else:
        return True


def client_install(
    username: str,
    keyfile: str,
    config: dict,  # settings from "EZDF" key
):
    server = config.get("connect_to")
    client = config.get("maprclient")
    cluster_name = config.get("cluster_name")

    if config.get("maprrepoislocal", False):
        # using local repository for mapr packages
        ezrepo: str = config.get("maprlocalrepo", "").rstrip("/")
    else:
        # using HPE repository
        ezrepo = f"https://package.ezmeral.hpe.com/releases"

    repo_content = get_mapr_repo(ezrepo)
    repofilename = "/etc/yum.repos.d/mapr.repo"

    logger.info("[ %s ] Install client for %s to %s", client, cluster_name, server)

    if client is not None:
        try:
            for out in sftp_content_to_file(
                host=client,
                username=username,
                keyfile=keyfile,
                content=repo_content,
                filepath=repofilename,
            ):
                logger.debug(f"[ {client} ] COPY {repofilename}: {out}")

        except Exception as error:
            logger.warning("Client file copy exception: %s", error)
            return False

    else:  # working on local machine
        with open(repofilename, "w") as repofile:
            repofile.write(repo_content)

    commands = INSTALL_COMMANDS[DFCLIENT]

    for file in DF_SECURE_FILES:
        commands.append(f"sudo curl -s --insecure --user mapr:mapr sftp://{server}{file} --output {file}")

    # Run these last
    # Configure client for cluster
    commands.append(f"sudo /opt/mapr/server/configure.sh -c -C {server} -N {cluster_name} -secure")
    # Generate ticket for root and enable posix-client (/mapr mount)
    commands.append(
        """echo mapr | sudo maprlogin password -user mapr ;
        sudo maprlogin generateticket -user mapr -type service -out /opt/mapr/conf/maprfuseticket -duration 30:0:0 -renewal 90:0:0;
        [ -d /mapr ] || sudo mkdir /mapr;
        sudo systemctl start mapr-posix-client-basic.service
        """
    )
    for command in commands:
        # print(f"Runnning {command}")
        logger.info("[ %s ] RUN %s", client, command)
        try:
            if client is not None:
                for result in ssh_run_command(host=client, username=username, keyfile=keyfile, command=command):
                    logger.debug(f"[ %s ] $s", client, result)

            else:  # running locally
                result = subprocess.run(
                    command.split(" "), shell=True, capture_output=True, text=True, check=True, universal_newlines=True, timeout=300
                )
                logger.info("[ LOCALHOST ] %s: %s", command, result)

        except Exception as error:
            logger.warning("[ %s ] CMD %s failed with: %s", client, command, error)
            return False

    return True


def xcluster(
    config: dict,
    settings: dict,
    dryrun: bool = True,
):
    local = settings["crosslocalcldb"]
    remote = settings["crossremotecldb"]
    adminuser = settings["crossadminuser"]
    adminpassword = settings["crossadminpassword"]
    username = config["username"]
    keyfile = config["privatekeyfile"]

    logger.info("Create cross cluster connectivity between %s and %s", local, remote)

    response = {}
    if dryrun:
        response["task"] = f"Cross-cluster setup between {local} and {remote}"
        response["settings"] = {**config, **settings}

    else:  # get truststore passwords
        try:
            local_truststore_password = ""
            remote_truststore_password = ""

            for out in ssh_run_command(
                host=local,
                command="sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
                username=username,
                keyfile=keyfile,
            ):
                local_truststore_password = out

            for out in ssh_run_command(
                host=remote,
                command="sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2",
                username=username,
                keyfile=keyfile,
            ):
                remote_truststore_password = out

            if local_truststore_password and remote_truststore_password:
                logger.info(f"using local truststore password: {local_truststore_password}")
                logger.info(f"using remote truststore password: {remote_truststore_password}")
            else:
                logger.warning(f"ERROR: failed to get truststore passwords, local: {local_truststore_password}, remote: {remote_truststore_password}")
                return False
        except Exception as error:
            logger.warning("Cross cluster setup exception: %s", error)
            return False

    cross_cluster_setup = f"sudo rm -rf /tmp/mapr-xcs; sudo -i -u {adminuser} /opt/mapr/server/configure-crosscluster.sh create all \
    -localcrossclusteruser {adminuser} -remotecrossclusteruser {adminuser} \
    -localtruststorepassword {local_truststore_password if local_truststore_password else 'LOCAL_TRUSTSTORE_PASSWORD'} \
    -remotetruststorepassword {remote_truststore_password if remote_truststore_password else 'REMOTE_TRUSTSTORE_PASSWORD'} \
    -remoteip {remote} -localuser {adminuser} -remoteuser {adminuser}"

    if dryrun:
        response["commands"] = f"ssh {local} sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2"
        response["commands"] = f"ssh {remote} sudo grep ssl.server.truststore /opt/mapr/conf/store-passwords.txt | cut -d'=' -f2"
        response["commands"] = cross_cluster_setup
        return response

    else:
        try:
            logger.info("If fails run the configure-crosscluster.sh command on one of the cluster nodes:")
            logger.info(cross_cluster_setup)

            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy)

            client.connect(hostname=local, username=username, key_filename=keyfile)

            interact = SSHClientInteraction(client, timeout=300, display=True)
            prompt = f".*[{username}@{local} ~]$.*"
            interact.expect(prompt)
            # print(interact.current_output_clean)

            interact.send("sudo dnf -q install -y pssh expect")
            interact.expect(prompt)

            interact.send(cross_cluster_setup)

            interact.expect("Enter password for mapr user.*")
            interact.send(adminpassword)
            interact.expect("Enter password for mapr user.*")
            interact.send(adminpassword)

            interact.expect(prompt)
            interact.send("exit")
            interact.expect()
        except Exception as error:
            logger.warning("Cross cluster setup exception: %s", error)
            return False

        logger.info("crosscluster-setup.sh finished, check logs for errors")
        return True


def get_mapr_stanza(hosts: list, username: str, password: str, disks: list, cluster_name: str):
    """
    Return stanza for Data Fabric installation
    """
    hosts_yaml = ""
    for host in hosts:
        hosts_yaml += f"  -   {host}\n"

    disks_yaml = ""
    for disk in disks:
        disks_yaml += f"  -   {disk}\n"

    return f"""
environment:
  mapr_core_version: {MAPR_CORE_VERSION}
config:
  hosts:
{hosts_yaml}
  ssh_id: {username}
  ssh_password: {password}
  enable_nfs: False
  db_admin_user: root
  db_admin_password: mapr123
  log_admin_password: mapr123
  metrics_ui_admin_password: mapr123
  enable_encryption_at_rest: True
  license_type: M7
  mep_version: {MAPR_MEP_VERSION}
  disks:
{disks_yaml}
  disk_format: true
  disk_stripe: 1
  cluster_name: {cluster_name}
  services:
    template-05-converged:
    # template-30-maprdb3:
    # template-20-drill:
    mapr-keycloak:
      enabled: False
    mapr-hivemetastore:
      database:
        name: hive
        user: hive
        password: mapr123
    # this conflicts with keycloak
    mapr-hbase-rest:
      enabled: False
    mapr-grafana:
      enabled: True
    mapr-opentsdb:
      enabled: True
    mapr-collectd:
      enabled: True
    mapr-fluentd:
      enabled: False
    mapr-kibana:
      enabled: False
    mapr-elasticsearch:
      enabled: False
    mapr-data-access-gateway:
    mapr-mastgateway:
    mapr-streams:
    mapr-airflow:
    mapr-hue:
      enabled: False
    mapr-httpfs:
      enabled: False
"""
