import os
import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from ezlab.parameters import SSHKEYNAME


def save_sshkey(key: str):
    # verify format and get private key
    private_key = get_privatekey_from_string(key)
    if private_key is None:
        return (False, "Not a known key format")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(SSHKEYNAME, "wb") as private_keyfile:
        private_keyfile.write(private_pem)
    os.chmod(SSHKEYNAME, 0o600)

    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        .decode("utf-8")
    )

    with open(f"{SSHKEYNAME}.pub", "w") as public_keyfile:
        public_keyfile.write(public_pem)

    return (True, private_pem.decode())


def get_privatekey_from_string(key: str):
    try:
        # try OpenSSL format (RSA?)
        return serialization.load_pem_private_key(key.encode(), password=None)
    except ValueError:
        # try OpenSSH format
        try:
            return serialization.load_ssh_private_key(key.encode(), password=None)
        except (ValueError, TypeError, cryptography.exceptions.UnsupportedAlgorithm):
            return None
    except Exception as error:
        print(error)
        return None


def get_ssh_pubkey_from_privatekey(privatekey):
    try:
        return (
            privatekey.public_key()
            .public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            )
            .decode()
        )
    except Exception as error:
        print(error)
        return None


def get_rsa_private_key(privatekey: serialization.SSHPrivateKeyTypes):
    if privatekey is not None:
        return privatekey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:
        return None


async def create_sshkey():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    await save_sshkey(private_pem)
