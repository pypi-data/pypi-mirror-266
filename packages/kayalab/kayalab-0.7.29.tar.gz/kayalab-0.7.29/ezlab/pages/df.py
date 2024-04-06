"""
Data Fabric operations user interface
"""

import logging
import re
from nicegui import app, ui, run

from ezlab.ezmeral.ezdf import client_install, cluster_install, xcluster

from ezlab.parameters import DF, DFAAS
from ezinfra.vms import prepare
from ezlab.utils import get_doc, get_fqdn


logger = logging.getLogger("ezlab.ui.df")


@ui.refreshable
def add_remove_host(hosts: list):
    if hosts is None:
        hosts = []
    for host in hosts:
        with ui.row().classes("w-full items-center no-wrap"):
            ui.input(
                "Hostname",
                placeholder="Host shortnames, ie, ezvm1,ezvm2...",
            ).bind_value(host, "name")
            ui.input(
                "IP Address",
                placeholder="10.1.1.x",
            ).bind_value(host, "ip")


async def prepare_action():
    hosts = app.storage.general[DF]["hosts"]
    isDFaaS = app.storage.general[DF]["dfaas"]

    # deep check list[dict] for missing values (if any host's name or IP is missing)
    if not (len(hosts) > 0 and all([values for values in [all(host) for host in [h.values() for h in hosts]]])):
        ui.notify("Missing values", type="warning")
        return False

    logger.info("Starting configuration for DF")
    app.storage.user["busy"] = True
    for host in hosts:
        result = await run.io_bound(
            prepare,
            hostname=get_fqdn(host["ip"]),
            hostip=host["ip"],
            settings=dict(app.storage.general["config"]),
            addhosts=[h for h in hosts if h["name"] != host["name"]],
            add_to_noproxy=(
                re.split(":|/", app.storage.general[DF].get("maprlocalrepo").split("://")[1])[0]
                if app.storage.general[DF].get("maprrepoislocal", False)
                else None
            ),
            prepare_for=DFAAS if isDFaaS else DF,
            dryrun=app.storage.general["config"]["dryrun"],
        )
        if app.storage.general["config"]["dryrun"]:
            get_doc(result)
        elif result:
            logger.info("[ %s ] ready: %s", host["name"], result)
        else:
            ui.notify(f"[{host}] preparation failed!", type="warning")

    app.storage.user["busy"] = False


def prepare_menu():
    if not "hosts" in app.storage.general[DF].keys():
        app.storage.general[DF]["hosts"] = [{"name": "", "ip": ""}]

    ui.checkbox("DF as a Service?").bind_value(app.storage.general[DF], "dfaas")

    with ui.row().classes("w-full items-center items-stretch") as prep_view:
        ui.label("Hosts")
        ui.space()
        with ui.row():

            def add_host():
                try:
                    app.storage.general[DF]["hosts"].append({"name": "", "ip": ""})
                except (KeyError, AttributeError):
                    app.storage.general[DF]["hosts"] = [{"name": "", "ip": ""}]
                finally:
                    add_remove_host.refresh(app.storage.general[DF]["hosts"])

            def remove_host():
                if len(app.storage.general[DF]["hosts"]) > 0:
                    app.storage.general[DF]["hosts"].pop()
                    add_remove_host.refresh()

            ui.button(icon="add_box", color=None, on_click=add_host).props("flat")
            ui.button(icon="delete", color=None, on_click=remove_host).props("flat")

    # Hosts
    add_remove_host(app.storage.general[DF]["hosts"])


async def install_action(hosts_string: str):

    logger.info("Starting DF cluster installation")

    app.storage.user["busy"] = True

    result = await run.io_bound(
        cluster_install,
        hosts=hosts_string.split(","),
        settings=dict(app.storage.general["config"]),
        config=dict(app.storage.general[DF]),
        dryrun=app.storage.general["config"]["dryrun"],
    )

    if app.storage.general["config"]["dryrun"]:
        get_doc(result)

    elif result:
        ui.notify(f"Cluster is ready!", type="positive")

    else:
        ui.notify(f"Cluster creation failed!", type="negative")

    app.storage.user["busy"] = False


async def xcluster_action():

    logger.info("Starting DF cross-cluster setup: DISABLED")

    app.storage.user["busy"] = True

    if not await run.io_bound(
        xcluster,
        config=dict(app.storage.general["config"]),
        settings=dict(app.storage.general[DF]),
        dryrun=app.storage.general["config"]["dryrun"],
    ):
        ui.notify(f"Cluster creation failed!", type="negative")
        return False

    app.storage.user["busy"] = False
    return True


async def client_action():

    logger.info("Starting DF client configuration")

    app.storage.user["busy"] = True

    result = await run.io_bound(
        client_install,
        username=app.storage.general["config"]["username"],
        keyfile=app.storage.general["config"]["privatekeyfile"],
        config=dict(app.storage.general[DF]),
    )

    if not result:
        ui.notify("Client configuration failed", type="negative")

    app.storage.user["busy"] = False

    if result:
        ui.notify(f"Finished client configuration", type="positive")
        return True
    else:
        return False
