import logging
from nicegui import app, ui
from ezlab.parameters import DF, UA

from ezlab.pages import df, ua

logger = logging.getLogger("ezlab.ui.ezmeral")

# so we can serve kubeconfig files
app.add_static_files("/files", "tmp")


@ui.refreshable
def menu():
    with (
        ui.expansion(
            "Ezmeral",
            icon="analytics",
            caption="install, configure and use",
        )
        .classes("w-full")
        .classes("text-bold") as ezmeral
    ):

        with ui.tabs().classes("w-full") as tabs:
            one = ui.tab(DF)
            two = ui.tab(UA)
        with ui.tab_panels(tabs, value=one).classes("w-full"):
            # Data Fabric Workflow
            with ui.tab_panel(one):
                with ui.stepper().props("vertical header-nav").classes("w-full") as dfstepper:
                    with ui.step("Prepare", icon=""):
                        df.prepare_menu()
                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=lambda: df.prepare_action(),
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=dfstepper.next,
                            ).props("color=secondary")

                    with ui.step("Install"):
                        ui.input("Cluster Name", placeholder="ezlab").bind_value(app.storage.general[DF], "cluster_name").classes("w-full")

                        maprclusterhosts = (
                            ui.input(
                                "Hosts",
                                placeholder="One or more comma-separated IPs, i.e., 10.1.1.x,10.1.1.y",
                            )
                            .classes("w-full")
                            .bind_value(app.storage.general[DF], "maprclusterhosts")
                        )

                        ui.input(
                            "Data Disk(s)",
                            placeholder="One or more comma-separated raw disk path, i.e., /dev/sdb,/dev/vdb",
                        ).bind_value(
                            app.storage.general[DF], "maprdisks"
                        ).classes("w-full")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=lambda: df.install_action(maprclusterhosts.value),
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=dfstepper.next,
                            ).props("color=secondary")
                            ui.button("Back", icon="fast_rewind", on_click=dfstepper.previous).props("flat")

                    with ui.step("Cross-Cluster"):
                        ui.label("Configure cross cluster communication between two clusters")
                        ui.input("Local Cluster CLDB node", placeholder="core.ez.lab").bind_value(app.storage.general[DF], "crosslocalcldb").classes(
                            "w-full"
                        )
                        ui.input("Remote Cluster CLDB node", placeholder="edge.ez.lab").bind_value(
                            app.storage.general[DF], "crossremotecldb"
                        ).classes("w-full")
                        ui.input("Cluster Admin User", placeholder="mapr").bind_value(app.storage.general[DF], "crossadminuser").classes("w-full")
                        ui.input(
                            "Cluster Admin Password",
                            placeholder="mapr",
                            password=True,
                            password_toggle_button=True,
                        ).bind_value(
                            app.storage.general[DF], "crossadminpassword"
                        ).classes("w-full")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=lambda: df.xcluster_action(),
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=dfstepper.next,
                            ).props("color=secondary")
                            ui.button("Back", icon="fast_rewind", on_click=dfstepper.previous).props("flat")

                    with ui.step("Client"):
                        ui.label("Setup a client to a Data Fabric cluster")
                        ui.input("Server", placeholder="Hostname or ip address").bind_value(app.storage.general[DF], "connect_to")
                        ui.switch("Remote", value=False).bind_value(app.storage.general[DF], "isclientremote")
                        ui.input("Client", placeholder="Hostname or ip address").bind_value(
                            app.storage.general[DF], "maprclient"
                        ).bind_visibility_from(app.storage.general[DF], "isclientremote")
                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=lambda: df.client_action(),
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button("Back", icon="fast_rewind", on_click=dfstepper.previous).props("flat")

            # Unified Analytics Workflow
            with ui.tab_panel(two):
                with ui.stepper().props("vertical header-nav").classes("w-full") as uastepper:
                    with ui.step("Prepare", icon=""):

                        ui.input("Orchestrator", placeholder="10.1.1.11").bind_value(app.storage.general[UA], "orchestrator")
                        ui.input("K8s Master", placeholder="10.1.1.12").bind_value(app.storage.general[UA], "controller")
                        ui.input("Workers", placeholder="10.1.1.13,10.1.1.14,10.1.1.15").bind_value(app.storage.general[UA], "workers")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=ua.prepare_action,
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=uastepper.next,
                            ).props("color=secondary")

                    with ui.step("Prechecks", icon=""):

                        ui.label(f"Orchestrator: {app.storage.general[UA].get('orchestrator', None)}")
                        ui.label(f"Controller: {app.storage.general[UA].get('controller', None)}")
                        ui.label(f"Workers: {app.storage.general[UA].get('workers', None)}")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=ua.precheck_action,
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=uastepper.next,
                            ).props("color=secondary")

                    with ui.step("Install", icon=""):

                        ui.label(f"Orchestrator: {app.storage.general[UA].get('orchestrator', None)}")
                        ui.label(f"Controller: {app.storage.general[UA].get('controller', None)}")
                        ui.label(f"Workers: {app.storage.general[UA].get('workers', None)}")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=ua.install_action,
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=uastepper.next,
                            ).props("color=secondary")

                    with ui.step("Deploy", icon=""):

                        ui.label(f"Orchestrator: {app.storage.general[UA].get('orchestrator', None)}")
                        ui.label(f"Controller: {app.storage.general[UA].get('controller', None)}")
                        ui.label(f"Workers: {app.storage.general[UA].get('workers', None)}")

                        with ui.stepper_navigation():
                            ui.button(
                                "Run",
                                icon="play_arrow",
                                on_click=ua.deploy_action,
                            ).bind_enabled_from(app.storage.user, "busy", backward=lambda x: not x)
                            ui.button(
                                "Next",
                                icon="fast_forward",
                                on_click=uastepper.next,
                            ).props("color=secondary")

    ezmeral.bind_value(app.storage.general["ui"], "ezmeral")
