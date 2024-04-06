import io
import logging
import random
import socket
import string
from time import sleep
from paramiko import (
    AuthenticationException,
    AutoAddPolicy,
    BadHostKeyException,
    RSAKey,
    SSHClient,
    SSHException,
)

from ezlab.parameters import PVE

logger = logging.getLogger("ezinfra.remote")


def wait_for_ssh(host, username, privatekey):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    sleep_time = 15
    try:
        while True:
            sleep(sleep_time)
            logger.debug("check ssh for %s@%s", username, host)
            client.connect(
                host,
                username=username,
                # key_filename=privatekey,
                pkey=RSAKey.from_private_key(io.StringIO(privatekey)),
                timeout=sleep_time,
            )
            break
    except (
        BadHostKeyException,
        AuthenticationException,
        ConnectionResetError,
        SSHException,
        socket.error,
    ):
        logger.debug("%s: still waiting ssh...", host)
        sleep(sleep_time)
    except Exception as error:
        logger.warning("[ %s ] ssh failed: %s", host, error)
        return False
    finally:
        client.close()

    sleep(15)  # give some time to service as it doesn't come up right away
    return True


def ssh_run_command(
    host: str,
    username: str,
    keyfile: str,
    command: str,
):
    """
    Run commands over ssh using default credentials
    Params:
        <host>              : hostname/IP to SSH
        <username>          : username to authenticate
        <keyfile>           : private key for <username>
        <command>           : command to run
    Returns:
        Generator with stdout. Calling function should process output with a for loop.
        Prints out stderr directly into terminal.

    """
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    command_output = None
    # print(f"Try connection to {host}")
    try:

        # logger.debug("REMOTE SSH GOT %s", command)

        client.connect(
            host,
            username=username,
            # key_filename=keyfile,
            # pkey=RSAKey.from_private_key(io.StringIO(keyfile)),
            pkey=RSAKey.from_private_key_file(keyfile),
            timeout=60,
        )

        # if "hostname -f" not in command:
        #     yield f"SSHCMD: {command}"
        _stdin, _stdout, _stderr = client.exec_command(command, get_pty=True)
        command_output = _stdout.read().decode().strip()

        if _stderr.read().decode().strip() != "":
            yield f"[SSH CMD ERROR]: {_stderr.readlines()}"
        if command_output and command_output != "":
            # should return only the command output
            yield command_output
    except Exception as error:
        raise error

    finally:
        client.close()


def sftp_copy_file(host: str, username: str, keyfile: str, source: str, destfile: str):
    try:
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy)
            ssh.connect(hostname=host, username=username, pkey=RSAKey.from_private_key_file(keyfile))
            with ssh.open_sftp() as sftp:
                result = sftp.put(source, destfile)
                if result:
                    logger.debug("%s copied", source)
                else:
                    logger.warning("Failed to copy %s: ", source)

    except Exception as error:
        logger.warning("SFTP Exception %s", error)


def sftp_content_to_file(host: str, username: str, keyfile: str, content: str, filepath: str):
    random_eof = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    command = f"""cat << {random_eof} | sudo tee {filepath} > /dev/null
{content}
{random_eof}"""

    # logger.debug("REMOTE SFTP %s", filepath)

    return ssh_run_command(
        host=host,
        username=username,
        keyfile=keyfile,
        command=command,
    )
