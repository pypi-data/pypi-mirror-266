import asyncio
import base64
from datetime import datetime, timedelta
from ipaddress import IPv4Address, ip_address
import logging
import os
import random
import shlex
import socket
import string
import subprocess
import importlib.resources
import io
import json
import time
import uuid

from fastapi.responses import StreamingResponse
from nicegui import app, ui


class ModuleContext:
    connection = None

    def __init__(self) -> None:
        pass


ezapp = ModuleContext()


class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log, level: int = logging.NOTSET) -> None:
        self.element = element
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        # change log format for UI
        self.setFormatter(
            logging.Formatter(
                "%(asctime)s:%(levelname)s: %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        try:
            msg = self.format(record)
            self.element.push(msg)
        except Exception:
            self.handleError(record)


# Read the usage
README = importlib.resources.read_text("ezlab", "USAGE.md")


# validation for non-zero entry
def nonzero(val):
    return len(val) != 0


# wrapper to make sync calls async-like
def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *[v for v in kwargs.values()])

    return wrapped


# find app on system path
def find_app(name: str):
    """Return executable path for `name` on PATH or in CWD."""
    from shutil import which

    return which(cmd=name, path=f"{os.environ.get('PATH')}:{os.getcwd()}")


# execute app/script locally
def execute(cmd: str):
    proc = subprocess.Popen(
        args=shlex.split(cmd),
        stdout=subprocess.PIPE,
        universal_newlines=True,
        # env=sub_env,
    )

    while proc.stdout:
        output = proc.stdout.readline().strip()
        if output == "" and proc.poll() is not None:
            break
        if output:
            yield output
    rc = proc.poll()


# Base64 conversion for secrets etc
def toB64(string: str):
    return base64.b64encode(string.encode("ascii")).decode("utf-8")


# IP address validation
def validate_ip(ip_string: str) -> bool:
    try:
        return isinstance(ip_address(ip_string), IPv4Address)
    except:
        return False


# reliably get FQDN for given IP
def get_fqdn(ip_string: str) -> str:
    fqdn, _, _ = socket.gethostbyaddr(ip_string)
    return fqdn


# def get_host_ip(hostname: str):
#     info = socket.getaddrinfo(
#         hostname, 22, family=socket.AF_INET, proto=socket.IPPROTO_TCP
#     )
#     return info[0][4][0]


def is_file(file):
    return os.path.isfile(os.path.abspath(file))


def dt_from_iso(timestring: str):
    # Workaround since received timestring with " AM"/" PM" suffix is not parsed properly
    isPM = " PM" in timestring
    dt = datetime.strptime(timestring.replace(" AM", "").replace(" PM", ""), "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt + timedelta(hours=12) if isPM else dt


def create_ci_iso(files: dict, destfile: str):
    from io import BytesIO
    import pycdlib

    metadata = files["meta-data"]
    userdata = files["user-data"]
    netconf = files["network-config"]

    iso = pycdlib.PyCdlib()
    iso.new(
        interchange_level=3,
        joliet=True,
        sys_ident="LINUX",
        rock_ridge="1.09",
        vol_ident="cidata",
    )

    metadata_file = BytesIO(metadata.encode())
    metadata_file.seek(0)
    iso.add_fp(
        metadata_file,
        len(metadata),
        "/METADATA.;1",
        rr_name="meta-data",
        joliet_path="/meta-data",
    )

    userdata_file = BytesIO(userdata.encode())
    iso.add_fp(
        userdata_file,
        len(userdata),
        "/USERDATA.;1",
        rr_name="user-data",
        joliet_path="/user-data",
    )

    netconf_file = BytesIO(netconf.encode())
    netconf_file.seek(0)
    iso.add_fp(
        netconf_file,
        len(netconf),
        "/NETWORK_.;1",
        rr_name="network-config",
        joliet_path="/network-config",
    )

    iso.write(destfile)
    iso.close()
    userdata_file.close()
    metadata_file.close()
    netconf_file.close()


# Define a download path for config downloads
CONFIG_DL_PATH = f"/config/{uuid.uuid4()}.json"


@app.get(CONFIG_DL_PATH)
def download(content: str = None):
    # by default downloading settings
    if content is None:
        content = app.storage.general

    string_io = io.StringIO(json.dumps(content))  # create a file-like object from the string

    headers = {"Content-Disposition": "attachment; filename=config.json"}
    return StreamingResponse(string_io, media_type="text/plain", headers=headers)


APP_STATUS_CONTAINER = []


@ui.refreshable
def status_container():
    with ui.row():
        for stat in APP_STATUS_CONTAINER:
            item, dest = stat
            ui.link(text=item, target=dest, new_tab=True).classes("text-emerald-400")
            ui.space()


def toggle_log():
    app.storage.user["showlog"] = not app.storage.user["showlog"]


def get_doc(content: dict):

    random_eof = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def indent(strings: str, spaces: int):
        return strings.strip().replace("\n", f"\n{' '*spaces}")

    settings = ""

    for key, value in content["settings"].items():
        settings += f"""
    #   {key}: {value if len(str(value)) < 80 else value[:77] + '...'}"""

    files = ""
    for filepath, filecontent in content["files"].items():
        files += f"""
    sudo cat <<{random_eof}>{filepath}
    {indent(filecontent,4)}
    {random_eof}
    """

    commands = ""
    for command in content["commands"]:
        commands += f"""
    {indent(command,4)}
    """

    doc = f"""
    #!/usr/bin/env bash

    # Ezlab Run {time.strftime('%Y%m%d%H%M%z')}

    # {content["task"]}

    # Settings
        {settings}

    # Write Files
        {files}

    # Run Commands
        {commands}

    # End of {content['task']}

"""

    with (
        ui.dialog().props("full-width") as dialog,
        ui.card().classes("w-full"),
    ):
        ui.code(doc, language="bash").classes("w-full text-wrap")
        with ui.row():
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: download(doc),
            )
            ui.button(
                "Close",
                icon="cancel",
                on_click=dialog.close,
            )
    dialog.open()


def get_new_vm_name(name_pattern: str, count: int):
    # intelligently increase the hostname counter
    # if we have single host, no need to append a number
    # else, check if the hostname is already numbered, if so, add to that number
    # NOTE: it won't roll to tens (ie, if previous host was named vm39, next will be vm310, not vm40)
    lastchar = name_pattern[-1]
    if lastchar.isdigit():
        count = int(lastchar) + count
        newname = name_pattern[:-1]

    return newname + str(count)
