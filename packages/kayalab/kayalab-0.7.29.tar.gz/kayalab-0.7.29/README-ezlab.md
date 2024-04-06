# Ezlab UI

UI to create virtual machines and install HPE Ezmeral products.

## Usage

It supports install operations for Virtual Machines on Proxmox VE and Libvirt/KVM.
VMware used to work but their cloud-init (vm-customisations) is too complex to handle for me, so I left it there.


### Template VMs

Ensure you followed the steps in [README](README.md) file to create templates on your host platform.


### Configure Utility

Use Settings menu to save environment details. Use placeholder text to see correct/expected format.

Leave empty if not used (ie, proxy, local repository...)

### VMs Menu

Login to hypervisor

New VM:

Select correct template, if bridge name doesn't pop up, close the dialog (`ESC`) and re-open.

Select the pre-defined configuration:

    UA Control Plane    | 2 VMs | 4 cores | 32GB Memory
    UA Workers          | 3 VMs | 32 cores | 128GB Memory
    DF Single Node      | 1 VM | 8 cores | 64GB Memory
    DF 5-Node Cluster   | 5 VMs | 8 cores | 32GB Memory
    Generic (Client)    | 1 VM | 1 cores | 2GB Memory

### Ezmeral Menu

Only Data Fabric for now.

#### Install Ezmeral Data Fabric

Version 7.6.1 with EEP 9.2.1 will be installed on as many hosts provided. Installer will be installed on the first node and system will automatically distribute services across other nodes. Single node installation is also possible.

Core components (fileserver, DB, Kafka/Streams, s3server, Drill, HBase, Hive) and monitoring tools (Grafana, OpenTSDB...) will be installed. Subject to change to optimize installation time & complexity.

##### Configure Step

Prepare for Data Fabric installation. Set up proxy, ulimit etc for your environment. Run in `dry mode` (in Settings) to get a bash script for preparations.

Add nodes to prepare multiple nodes.

##### Install Step

Create Data Fabric cluster on the provided nodes.

##### Cross-Cluster Step

Will be working soon!

##### Connect Step

Will download secure files from the server and install/configure the client for the cluster.

## NOTES

If API servers (ProxmoxVE and/or vSphere) are using self-signed certificates, insecure connection warnings will mess up your screen. You can avoid this using environment variable (this is not recommended due to security concerns):

`export PYTHONWARNINGS="ignore:Unverified HTTPS request"`

## TODO

[ ] Proper documentation and code clean up

[ ] Test on standalone ESX host

[X] Test airgap
