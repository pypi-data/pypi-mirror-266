import logging
from nicegui import app, ui, run
from ezlab.pages.df import get_doc
from ezlab.parameters import EZNODES, KVM, PVE
from ezinfra.vms import clone
from ezinfra import kvm, pve
from ezlab.utils import get_new_vm_name


logger = logging.getLogger("ezlab.ui.vms")


def pve_newvm_dialog():

    @ui.refreshable
    def bridge_selector():
        app.storage.user["busy"] = True
        selector = (
            ui.select(
                options=app.storage.user.get("volumes", []),
                label="Base Image",
            )
            .classes("w-full")
            .props("inline")
            .bind_value(app.storage.general[PVE], "bridge")
        )
        app.storage.user["busy"] = False
        return selector

    def update_template():
        app.storage.user["bridges"] = pve.bridges(app.storage.general[PVE].get("template", None))
        bridge_selector.refresh()

    app.storage.user["busy"] = True

    templates = [x for x in pve.vms() if x["template"] and x["type"] == "qemu"]
    # networks = pve.networks(ezapp.connection)
    storage = pve.pools()

    app.storage.user["busy"] = False

    # vm settings dialog
    with ui.dialog() as dialog, ui.card():
        ui.select(
            options={x["id"]: f"{x['name']} ( {x['node']} )" for x in templates},
            label="Template",
            on_change=update_template,
        ).classes(
            "w-full"
        ).props("inline").bind_value(app.storage.general[PVE], "template")

        ui.select(
            options={x["id"]: f"{x['storage']} ( {x['node']} )" for x in storage},
            # if x["node"] == app.storage.user["template"]["node"]
            label="Data Disk Pool",
        ).classes("w-full").props("inline").bind_value(app.storage.general[PVE], "storage")

        # network_selector = (
        #     ui.select(
        #         options=[
        #             x["sdn"]
        #             for x in networks
        #             # if x["node"] == app.storage.user["template"]["node"]
        #         ],
        #         label="Network",
        #     )
        #     .classes("w-full")
        #     .props("inline")
        #     .bind_value(app.storage.general[PVE], "network")
        # )

        ui.select(
            options=[x["iface"] for x in app.storage.user.get("bridges", [])],
            label="Bridge",
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[PVE], "bridge")

        ui.select(
            options=[x["name"] for x in EZNODES],
            label="Node Type",
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[PVE], "eznode")

        ui.input(label="VM Name", placeholder="ezvm").classes("w-full").props("inline").bind_value(app.storage.general[PVE], "hostname")

        ui.input(
            label="First IP",
            placeholder=app.storage.general["config"]["gateway"],
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[PVE], "firstip")

        ui.button(
            "Create",
            on_click=lambda: dialog.submit(
                (
                    next(
                        (i for i in templates if i["id"] == app.storage.general[PVE]["template"]),
                        None,
                    ),
                    next(
                        (i for i in storage if i["id"] == app.storage.general[PVE]["storage"]),
                        None,
                    ),
                    app.storage.general[PVE]["bridge"],
                    next(
                        (i for i in EZNODES if i["name"] == app.storage.general[PVE]["eznode"]),
                        None,
                    ),
                    app.storage.general[PVE]["hostname"],
                    app.storage.general[PVE]["firstip"],
                )
            ),
        )

    return dialog


def kvm_newvm_dialog():
    @ui.refreshable
    def volume_selector():
        app.storage.user["busy"] = True
        selector = (
            ui.select(
                options=app.storage.user.get("volumes", []),
                label="Base Image",
            )
            .classes("w-full")
            .props("inline")
            .bind_value(app.storage.general[KVM], "baseimg")
        )
        app.storage.user["busy"] = False
        return selector

    def update_volumes():
        app.storage.user["volumes"] = kvm.volumes(app.storage.general[KVM].get("pool", "default"))
        volume_selector.refresh()

    # select dialog
    with ui.dialog() as dialog, ui.card():

        app.storage.user["busy"] = True

        pools = kvm.pools()
        bridges = kvm.bridges()

        app.storage.user["busy"] = False

        ui.select(
            options=[p.name() for p in pools],
            label="Pool",
            on_change=update_volumes,
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[KVM], "pool")

        # baseimg
        volume_selector()

        # volumes = kvm.volumes(app.storage.general[KVM].get("pool", "default"))
        # baseimg = (
        #     ui.select(
        #         options=volumes,
        #         label="Base Image",
        #     )
        #     .classes("w-full")
        #     .props("inline")
        #     .bind_value(app.storage.general[KVM], "baseimg")
        # )

        ui.select(
            options=bridges,
            label="Bridge",
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[KVM], "bridge")

        ui.select(
            options=[x["name"] for x in EZNODES],
            label="Node Type",
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[KVM], "eznode")

        ui.input(label="VM Name", placeholder="ezvm").classes("w-full").props("inline").bind_value(app.storage.general[KVM], "hostname")

        ui.input(
            label="First IP",
            placeholder="10.1.1.21",
        ).classes("w-full").props(
            "inline"
        ).bind_value(app.storage.general[KVM], "firstip")

        ui.button(
            "Create",
            on_click=lambda: dialog.submit(
                (
                    app.storage.general[KVM]["pool"],
                    app.storage.general[KVM]["baseimg"],
                    app.storage.general[KVM]["bridge"],
                    next(
                        (i for i in EZNODES if i["name"] == app.storage.general[KVM]["eznode"]),
                        None,
                    ),
                    app.storage.general[KVM]["hostname"],
                    app.storage.general[KVM]["firstip"],
                )
            ),
        )
    return dialog


async def new_vm_ui():

    if app.storage.general["target"]["hve"] == PVE:
        dialog = pve_newvm_dialog()
    elif app.storage.general["target"]["hve"] == KVM:
        dialog = kvm_newvm_dialog()
    else:
        ui.notify("not implemented")

    resources = await dialog

    if resources and all(resources):
        vm_count = resources[3]["count"]

        app.storage.user["busy"] = True
        dryrun = app.storage.general["config"].get("dryrun", True)

        result = await run.io_bound(
            clone,
            target=app.storage.general["target"]["hve"],
            resources=resources,
            settings=dict(app.storage.general["config"]),
            # vm_number=(0 if vmcount == 1 else count + 1),  # start from 1 not 0, use 0 for single vm
            vm_count=vm_count,
            dryrun=dryrun,
        )
        if dryrun:
            get_doc(result)
        elif result:
            logger.info("%s VMs ready: %s", vm_count, result)

        app.storage.user["busy"] = False

    else:
        ui.notify("VM creation cancelled", type="info")
