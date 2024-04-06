import os

from ezlab.parameters import DF, GENERIC, UA

ini_file = os.path.expanduser("~/.ezconfig.ini")


ez_files = {
    DF: {
        "/etc/sysctl.d/mapr.conf": "vm.swappiness=1\n",
        "/etc/profile.d/mapr.sh": "umask 0022\n",
    },
    UA: {},
    GENERIC: {},
}


ez_installers = {
    DF: {
        "image": "maprtech/edf-seed-container:latest",
        "start_installer": "./datafabric_container_setup.sh",
        "url": "https://localhost:8443/app/dfui/#/installer",
        "commands": [],
    },
    UA: {
        "start_installer": "./start_ezua_installer_ui.sh",
        # "image": "marketplace.us1.greenlake-hpe.com/ezua/ezua/hpe-ezua-installer-ui:latest",
        "image": "us.gcr.io/mapr-252711/hpe-ezua-installer-ui:1.2.0-d16afb0",
        "url": "http://localhost:8080",
    },
    GENERIC: {},
}
