UI to create virtual machines and install HPE Ezmeral products.

**Create a template VM if you want VM provisioning**

ProxmoxVE and Libvirt/KVM are working. Rocky8 and RHEL8 are tested.

#### Settings Menu

Use Settings menu to save environment details. Use placeholder text to see correct/expected format.

Leave empty if not used (ie, proxy, local repository...)

#### VMs Menu

Login to hypervisor.

**New VM button**

Select correct template.

Select the pre-defined configuration:

    | Node Type           | # of VMs | Cores | Memory |
    | ------------------- | -------- | ----- | -----  |
    | UA Control Plane    | 2        | 4     | 32GB   |
    | UA Workers          | 3        | 32    | 128GB  |
    | DF Single Node      | 1        | 16    | 128GB  |
    | DF 5-Node Cluster   | 5        | 8     | 32GB   |
    | Generic (Client)    | 1        | 2     | 4GB    |

#### Ezmeral Menu

Only Data Fabric for now.

##### Ezmeral Data Fabric

Version 7.6.1 with EEP 9.2.1 will be installed on as many hosts provided. Installer will be installed on the first node and system will automatically distribute services across other nodes. Single node installation is also possible.

Core components (fileserver, DB, Kafka/Streams, s3server, Drill, HBase, Hive) and monitoring tools (Grafana, OpenTSDB...) will be installed. Subject to change to optimize installation time & complexity.

###### Configure Step

Prepare for Data Fabric installation.

Add more nodes (+ sign) to prepare multiple nodes together.

###### Install Step

Create Data Fabric cluster on given nodes.

###### Cross-Cluster Step

Will be working soon!

###### Connect Step

Will download secure files from the server and install/configure the client for the cluster.
