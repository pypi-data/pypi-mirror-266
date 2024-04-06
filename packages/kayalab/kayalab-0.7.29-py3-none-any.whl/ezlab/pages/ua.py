import logging
from nicegui import app, ui, run

from ezlab.ezmeral.ezua import deploy, install, precheck
from ezlab.parameters import UA
from ezinfra.vms import prepare
from ezlab.utils import get_doc, get_fqdn


logger = logging.getLogger("ezlab.ui.ua")


async def prepare_action():
    orchestrator = app.storage.general[UA].get("orchestrator", None)
    controller = app.storage.general[UA].get("controller", None)
    workers = app.storage.general[UA].get("workers", None)

    if orchestrator is None or controller is None or workers is None or len(workers.split(",")) < 3:
        logger.warning("Missing hosts, fix and retry!")
        logger.debug(
            "Orchestrator: %s, Controller: %s, Workers: %s",
            orchestrator,
            controller,
            workers,
        )
        return None

    logger.info("Starting configuration for UA")
    app.storage.user["busy"] = True

    hosts = [orchestrator, controller]
    hosts.extend(workers.split(","))

    for host in hosts:
        result = await run.io_bound(
            prepare,
            hostname=get_fqdn(host),
            hostip=host,
            settings=dict(app.storage.general["config"]),
            addhosts=[h for h in hosts if h != host],
            add_to_noproxy=f"{orchestrator},{controller},{workers}",
            prepare_for=UA,
            dryrun=app.storage.general["config"]["dryrun"],
        )
        if app.storage.general["config"]["dryrun"]:
            get_doc(result)
        elif result:
            logger.info("[ %s ] ready: %s", host, result)
        else:
            ui.notify(f"[{host}] preparation failed!", type="warning")

    app.storage.user["busy"] = False


async def precheck_action():
    logger.info("Running prechecks for UA")
    app.storage.user["busy"] = True

    result = await run.io_bound(precheck)
    logger.debug("RESULT: %s", result)

    app.storage.user["busy"] = False


async def install_action():
    logger.info("Starting UA installation")
    app.storage.user["busy"] = True
    result = await run.io_bound(install)

    logger.debug("RESULT: %s", result)

    app.storage.user["busy"] = False


async def deploy_action():
    logger.info("Deploying UA Applications")
    app.storage.user["busy"] = True
    result = await run.io_bound(deploy)

    logger.debug("RESULT: %s", result)

    app.storage.user["busy"] = False
