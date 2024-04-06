import asyncio
from nicegui import app, ui
from proxmoxer import ProxmoxAPI
from libvirt import virConnect
import ezlab.utils as utils

from ezlab.parameters import KVM, PVE, SUPPORTED_HVES

from ezlab.pages.vms import new_vm_ui
from ezinfra import kvm, pve


@ui.refreshable
def menu():

    with ui.expansion("VMs", icon="computer", caption="create and configure").classes("w-full").classes("text-bold") as virtualmachines:
        with ui.row().classes("w-full items-center justify-between"):
            # Login dialog
            with ui.dialog() as dialog, ui.card():
                t = ui.radio(options=SUPPORTED_HVES).classes("w-full").props("inline").bind_value(app.storage.general["target"], "hve")

                h = ui.input("Host").classes("w-full").bind_value(app.storage.general["target"], "host")

                u = ui.input("Username").classes("w-full").bind_value(app.storage.general["target"], "username")

                p = (
                    ui.input(
                        "Password",
                        password=True,
                        password_toggle_button=True,
                    )
                    .classes("w-full")
                    .bind_value(app.storage.general["target"], "password")
                    .bind_enabled_from(  # disable password entry for kvm, only ssh key authorisation works (or user need to enter password at the cli)
                        app.storage.general["target"], "hve", backward=lambda x: x != KVM
                    )
                )

                ui.button(
                    "Login",
                    on_click=lambda: dialog.submit((t.value, h.value, u.value, p.value)),
                )

            # Connection view
            with ui.row():
                ui.button(icon="cloud_done", on_click=lambda: loginbuttonaction(dialog)).bind_visibility_from(
                    app.storage.general["target"],
                    "connected",
                )
                ui.button(icon="cloud_off", on_click=lambda: loginbuttonaction(dialog)).bind_visibility_from(
                    app.storage.general["target"],
                    "connected",
                    lambda x: not x,
                )

            # new vm button
            ui.label().bind_text_from(
                app.storage.general["target"],
                "hve",
                backward=lambda x: f"{x} connected",
            ).bind_visibility_from(app.storage.general["target"], "connected")
            ui.button("New VM", on_click=new_vm_ui).bind_visibility_from(app.storage.general["target"], "connected").bind_enabled_from(
                app.storage.user, "busy", backward=lambda x: not x
            )

    virtualmachines.bind_value(app.storage.general["ui"], "virtualmachines")


async def loginbuttonaction(loginform: ui.dialog):
    if app.storage.general["target"]["connected"]:
        # TODO: disconnect process/cleanup
        app.storage.general["target"]["connected"] = False

    else:
        result = await loginform

        # modify password field if target is KVM, so emptiness check below can proceed without password
        if result and result[0] == KVM:
            result[3] == "nopasswordsupportforkvm"

        # emptiness check
        if result and all(result):
            connection = await connect(result)
            if connection:
                utils.ezapp.connection = connection
                app.storage.general["target"]["connected"] = True

        else:
            ui.notify("Missing information", type="warning")


async def connect(params: set):
    target, host, username, password = params
    try:
        if target == PVE:
            result = await asyncio.to_thread(pve.connect, host, username, password)

        elif target == KVM:
            result = await asyncio.to_thread(kvm.connect, host, username)

        # elif target == VMWARE:
        #     return await asyncio.to_thread(vmw.connect, host, username, password)

        else:
            result = None

        if isinstance(result, ProxmoxAPI) or isinstance(result, virConnect):
            app.storage.general["target"]["connected"] = True
            return result
        else:
            app.storage.general["target"]["connected"] = False
            ui.notify(f"FAILED: {result}", type="negative")

    except Exception as error:
        ui.notify(f"CONNECT ERROR: {error}", type="negative")
