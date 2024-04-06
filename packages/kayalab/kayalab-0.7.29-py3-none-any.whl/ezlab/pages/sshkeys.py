import os
from nicegui import app, ui
from ezinfra.sshkeys import create_sshkey, save_sshkey

from ezlab.parameters import SSHKEYNAME
from ezlab.utils import is_file


async def confirm_overwrite(file):
    with ui.dialog() as dialog, ui.card():
        ui.label(f"{file} will be overwritten, are you sure?")
        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
            ui.button("No", on_click=lambda: dialog.submit("No"))
    return await dialog


async def handle_keyimport(key: str):

    if key is not None:

        if is_file(SSHKEYNAME):
            if await confirm_overwrite(SSHKEYNAME) != "Yes":
                ui.notify("Cancelled", type="warning")
                return None

        (result, content) = save_sshkey(key)

        if result:

            app.storage.general["config"]["privatekey"] = content
            app.storage.general["config"]["privatekeyfile"] = os.path.abspath(SSHKEYNAME)

            ui.notify(f"Key saved as {os.path.abspath(SSHKEYNAME)}", type="positive")
            ssh_keys_ui.refresh()

        else:
            ui.notify(content, type="negative")

    else:
        ui.notify("Cancelled", type="warning")


@ui.refreshable
def ssh_keys_ui():
    if is_file(SSHKEYNAME):
        ui.label(f"Existing Key: {os.path.abspath(SSHKEYNAME)}")
    with ui.row():
        ui.upload(
            label="Import",
            on_upload=lambda e: handle_keyimport(e.content.read().decode("utf-8")),
            on_rejected=lambda x: ui.notify("No file selected"),
            max_file_size=1_000_000,
            max_files=1,
            auto_upload=True,
        ).props("accept=*")

        ui.button("Create New", on_click=create_sshkey)
