#!/usr/bin/env python3
"""
DESCRIPTION:
    Deploy VMs on my lab and configure them for Ezmeral
USAGE EXAMPLE:
    > ezlab for GUI, ezlabctl for command line
"""

import logging
from nicegui import Client, ui, app, native, binding
import requests

import ezlab
from ezlab.parameters import DF, SUPPORTED_HVES, UA
from ezlab.pages import ezmeral
from ezlab.pages import settings
from ezlab.pages import targets
from ezlab.utils import README, LogElementHandler, status_container, toggle_log


logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d: %(message)s",
        datefmt="%H:%M:%S",
    )
)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

# https://sam.hooke.me/note/2023/10/nicegui-binding-propagation-warning/
binding.MAX_PROPAGATION_TIME = 0.05

# Initialize
# Top-level keys in config
for key in ["target", "ui", "config", UA, DF, *SUPPORTED_HVES]:
    if key not in app.storage.general.keys():
        app.storage.general[key] = {}

# Set initial connection
app.storage.general["target"]["connected"] = False

# DEBUG for passed args
app.native.start_args["debug"] = True


def graceful_fail(exc: Exception):
    print("gracefully dying...")
    logger.debug("Exception: %s", exc)
    app.storage.user["busy"] = False


app.on_exception(graceful_fail)


# Main page
@ui.page("/")
async def home(client: Client):
    # initial status
    app.storage.user["busy"] = False
    # and log window
    app.storage.user["showlog"] = False

    # Header
    with ui.header(elevated=True).classes("items-center justify-between") as header:
        # home button
        ui.label("Ezlab").classes("text-bold text-lg")

        ui.space()

        with ui.row().classes("items-center"):
            ui.label("Settings")
            ui.button(icon="download", on_click=settings.config_show().open)
            ui.button(icon="upload", on_click=settings.config_load().open)

    # Footer
    with ui.footer() as footer:
        with ui.row().classes("w-full place-items-center"):
            ui.button(icon="menu", on_click=toggle_log).props("flat text-color=white")
            ui.label("Log")
            ui.space()
            status_container()
            ui.space()
            ui.spinner("ios", size="2em", color="red").bind_visibility_from(app.storage.user, "busy")
            ui.icon("check_circle", size="2em", color="green").bind_visibility_from(app.storage.user, "busy", lambda x: not x)
        log = ui.log().classes("w-full h-48 bg-neutral-300/30").style("white-space: pre-wrap").bind_visibility(app.storage.user, "showlog")
        logger.addHandler(LogElementHandler(log, logging.INFO))

    # Content

    # README section
    with (
        ui.expansion(
            "Readme",
            icon="description",
            caption="how to use this app?",
        )
        .classes("w-full")
        .classes("text-bold")
    ):
        # readme = ""
        # with open(os.path.dirname(__file__) + "/USAGE.md", "r") as readmefile:
        #     readme = readmefile.read()

        ui.markdown(README)

    # Settings section
    settings.menu()

    ui.separator()

    # Infrastructure section
    targets.menu()

    ui.separator()

    # Ezmeral Products section
    ezmeral.menu()

    ui.separator()

    # cleanup the download route after the client disconnected
    # await client.disconnected()
    # app.routes[:] = [route for route in app.routes if route.path != CONFIG_DL_PATH]


# INSECURE REQUESTS ARE OK in LAB
requests.packages.urllib3.disable_warnings()
urllib_logger = logging.getLogger("urllib3.connectionpool")
urllib_logger.setLevel(logging.WARNING)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.WARNING)
watcher_logger = logging.getLogger("watchfiles.main")
watcher_logger.setLevel(logging.FATAL)

paramiko_log = logging.getLogger("paramiko.transport")
paramiko_log.setLevel(logging.WARNING)

logger.debug("Running version: %s", ezlab.__version__)


# Entry point for the module
def enter():
    # ui.run(
    #     ezmeral_icon = """
    #     <svg width="48" height="24" viewBox="0 0 48 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    #         <path d="M7 8H41V16H7V8Z" fill="#01A982"/>
    #         <path d="M1 8H7V16H1V8Z" fill="#00775B"/>
    #         <path d="M41 8H47V16H41V8Z" fill="#00775B"/>
    #         <path d="M7 16H41V22H7V16Z" fill="#00775B"/>
    #         <path d="M7 2H41V8H7V2Z" fill="#00C781"/>
    #         <path d="M1 8L7 2V8H1Z" fill="#01A982"/>
    #         <path d="M1 16L7 22V16H1Z" fill="#01A982"/>
    #         <path d="M47 8L41 2V8H47Z" fill="#01A982"/>
    #         <path d="M47 16L41 22V16H47Z" fill="#01A982"/>
    #     </svg>
    #     """
    #     title="Ezlab",
    #     dark=None,
    #     favicon=ezmeral_icon,
    #     storage_secret = ("ezmeralr0cks",)
    #     show=True,
    #     # reload=False,
    # )

    ui.run(
        title="Ezlab",
        dark=None,
        native=True,
        window_size=(1024, 1024),
        # frameless=True,
        storage_secret="ezmeralr0cks",
        reload=False,
        port=native.find_open_port(),
    )


# For development and debugs
if __name__ in {"__main__", "__mp_main__"}:
    print("EZLAB RUNNING IN DEV MODE")
    ui.run(
        title="Ezlab",
        dark=None,
        native=True,
        window_size=(1024, 1024),
        # frameless=True,
        storage_secret="ezmeralr0cks",
        reload=True,
        port=native.find_open_port(),
    )
