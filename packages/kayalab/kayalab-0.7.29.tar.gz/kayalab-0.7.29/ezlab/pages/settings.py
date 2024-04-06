# Config show dialog
import json
import logging
from nicegui import app, ui
from ezlab.parameters import DF
from ezlab.pages import ezmeral

from ezlab.pages.sshkeys import ssh_keys_ui
from ezlab.pages import targets
from ezlab.pages import settings
from ezlab.utils import CONFIG_DL_PATH

logger = logging.getLogger("ezlab.ui.settings")


def save_config(val: str, dialog):
    try:
        for key, value in json.loads(val.replace("\n", "")).items():
            app.storage.general[key] = value
        for m in (ezmeral.menu, targets.menu, settings.menu):
            m.refresh()
        dialog.close()
        ui.notify("Settings loaded", type="positive")
    except (TypeError, json.decoder.JSONDecodeError, ValueError) as error:
        ui.notify("Not a valid json", type="negative")
        logger.warning(error)


def config_show():
    with ui.dialog() as config_show, ui.card().classes("w-full h-full"):
        config_json = json.dumps(app.storage.general, indent=2)
        ui.code(config_json, language="json").classes("w-full text-wrap")
        with ui.row():
            ui.button(
                "Save",
                icon="save",
                on_click=lambda: ui.download(CONFIG_DL_PATH),
            )
            ui.button(
                "Close",
                icon="cancel",
                on_click=config_show.close,
            )
    return config_show


# Config load dialog
def config_load():
    with ui.dialog() as config_load, ui.card().classes("w-full h-full"):
        jsontext = ui.textarea().props("stack-label=json autogrow filled").classes("h-dvh w-full text-wrap")
        with ui.row():
            ui.button(
                "Save",
                on_click=lambda _: save_config(
                    jsontext.value,
                    config_load,
                ),
                icon="save",
            )
            ui.button(
                "Close",
                icon="cancel",
                on_click=config_load.close,
            )

    return config_load


@ui.refreshable
def menu():
    with (
        ui.expansion(
            "Settings",
            icon="settings",
            caption="for your environment",
        )
        .classes("w-full")
        .classes("text-bold") as settings
    ):
        ui.checkbox("Dry Run", value=False).bind_value(app.storage.general["config"], "dryrun")
        ui.label("Network Settings").classes("text-bold")
        with ui.row():
            ui.input("VM Network", placeholder="10.1.1.0/24").bind_value(app.storage.general["config"], "cidr")
            ui.input("Gateway", placeholder="10.1.1.1").bind_value(app.storage.general["config"], "gateway")
            ui.input("Name Server", placeholder="10.1.1.1").bind_value(app.storage.general["config"], "nameserver")
            ui.input("Domain", placeholder="ez.lab").bind_value(app.storage.general["config"], "domain")
            ui.input("HTTP Proxy", placeholder="").bind_value(app.storage.general["config"], "proxy")

        ui.label("Repositories").classes("text-bold")
        with ui.row().classes("w-full"):
            # YUM Repo
            ui.input("YUM Repo", placeholder="").bind_value(app.storage.general["config"], "yumrepo")

            ui.input("EPEL Repo", placeholder="").bind_value(app.storage.general["config"], "epelrepo")
            # ui.input("Insecure Registry", placeholder="").bind_value(
            #     app.storage.general["config"], "airgap_registry"
            # )

        # MapR Repository Configuration
        with ui.row().classes("w-full"):
            ui.label("MapR Repo").classes("self-center")
            switch = ui.switch("Use local", value=False).props("left-label").bind_value(app.storage.general[DF], "maprrepoislocal")

            # Using default HPE repository
            with ui.row().bind_visibility_from(switch, "value", lambda x: not x).classes("w-full items-justify"):
                ui.input("HPE Passport e-mail").bind_value(app.storage.general[DF], "maprrepouser")
                ui.input("HPE Passport token", password=True, password_toggle_button=True).bind_value(app.storage.general[DF], "maprrepotoken")

            # Using local repository
            with ui.row().bind_visibility_from(switch, "value"):
                ui.input(
                    "MapR Repo",
                    placeholder="https://repo.ez.lab/mapr/",
                ).bind_value(app.storage.general[DF], "maprlocalrepo")
                authlocal = ui.switch("Authenticate", value=True).bind_value(app.storage.general[DF], "maprlocalrepoauth")
                with ui.row():
                    ui.input("Username", password=True).bind_value(app.storage.general[DF], "maprlocalrepousername").bind_visibility(
                        authlocal, "value"
                    )
                    ui.input("Password", password=True).bind_value(app.storage.general[DF], "maprlocalrepopassword").bind_visibility(
                        authlocal, "value"
                    )

        ui.label("Cloudinit Settings").classes("text-bold")
        with ui.row():
            ui.input("username", placeholder="ezmeral").bind_value(app.storage.general["config"], "username")
            ui.input("password", password=True, password_toggle_button=True).bind_value(app.storage.general["config"], "password")

        ui.label("SSH Key").classes("text-bold")
        ssh_keys_ui()

    settings.bind_value(app.storage.general["ui"], "settings")
