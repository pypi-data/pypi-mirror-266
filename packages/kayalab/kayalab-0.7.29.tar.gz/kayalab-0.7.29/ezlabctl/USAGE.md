# `ezlabctl`

**Usage**:

```console
$ ezlabctl [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `config`: manage deployment settings
* `create`: create templates and VMs
* `delete`: delete templates and VMs
* `ezdf`: Manage Ezmeral Data Fabric installation
* `ezua`: Manage Ezmeral Unified Analytics installation
* `info`: print usage
* `prepare`: Run pre-requisites on VM for specified product

## `ezlabctl config`

**Usage**:

```console
$ ezlabctl config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `get`
* `set`

### `ezlabctl config get`

**Usage**:

```console
$ ezlabctl config get [OPTIONS]
```

**Options**:

* `--out / --no-out`: [default: no-out]
* `--help`: Show this message and exit.

### `ezlabctl config set`

**Usage**:

```console
$ ezlabctl config set [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ezlabctl create`

**Usage**:

```console
$ ezlabctl create [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `template`
* `vm`

### `ezlabctl create template`

**Usage**:

```console
$ ezlabctl create template [OPTIONS] TARGET:{pve|vmw} HOST USERNAME PASSWORD
```

**Arguments**:

* `TARGET:{pve|vmw}`: [required]
* `HOST`: [required]
* `USERNAME`: [required]
* `PASSWORD`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ezlabctl create vm`

**Usage**:

```console
$ ezlabctl create vm [OPTIONS] TARGET:{pve|vmw} HOST USERNAME PASSWORD
```

**Arguments**:

* `TARGET:{pve|vmw}`: [required]
* `HOST`: [required]
* `USERNAME`: [required]
* `PASSWORD`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ezlabctl delete`

**Usage**:

```console
$ ezlabctl delete [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `template`
* `vm`

### `ezlabctl delete template`

**Usage**:

```console
$ ezlabctl delete template [OPTIONS] TARGET:{pve|vmw} HOST USERNAME PASSWORD
```

**Arguments**:

* `TARGET:{pve|vmw}`: [required]
* `HOST`: [required]
* `USERNAME`: [required]
* `PASSWORD`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ezlabctl delete vm`

**Usage**:

```console
$ ezlabctl delete vm [OPTIONS] TARGET:{pve|vmw} HOST USERNAME PASSWORD
```

**Arguments**:

* `TARGET:{pve|vmw}`: [required]
* `HOST`: [required]
* `USERNAME`: [required]
* `PASSWORD`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ezlabctl ezdf`

**Usage**:

```console
$ ezlabctl ezdf [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `cluster`: Create DF cluster
* `cross`: Configure cross-cluster
* `dfclient`: Create a DF client

### `ezlabctl ezdf cluster`

Create Data Fabric cluster with provided hosts

**Usage**:

```console
$ ezlabctl ezdf cluster [OPTIONS] HOSTS...
```

**Arguments**:

* `HOSTS...`: [required]

**Options**:

* `--name TEXT`: [default: ezlab]
* `--repouser TEXT`
* `--repotoken TEXT`
* `--help`: Show this message and exit.

### `ezlabctl ezdf cross`

Create cross-cluster connectivity between local and remote

**Usage**:

```console
$ ezlabctl ezdf cross [OPTIONS] LOCAL REMOTE
```

**Arguments**:

* `LOCAL`: [required]
* `REMOTE`: [required]

**Options**:

* `--luser TEXT`: [default: mapr]
* `--ruser TEXT`: [default: mapr]
* `--password TEXT`: [default: mapr]
* `--help`: Show this message and exit.

### `ezlabctl ezdf dfclient`

Configure DF client for specified cluster (CLDB)

**Usage**:

```console
$ ezlabctl ezdf dfclient [OPTIONS] SERVER CLIENT
```

**Arguments**:

* `SERVER`: [required]
* `CLIENT`: [required]

**Options**:

* `--user TEXT`
* `--token TEXT`
* `--help`: Show this message and exit.

## `ezlabctl ezua`

**Usage**:

```console
$ ezlabctl ezua [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `applycr`
* `create-workload-cluster`: Create UA workload cluster
* `install`
* `remove`: Remove UA
* `with-rest`

### `ezlabctl ezua applycr`

**Usage**:

```console
$ ezlabctl ezua applycr [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`: [default: ezlab]
* `--help`: Show this message and exit.

### `ezlabctl ezua create-workload-cluster`

Create UA workload cluster

Args:
    orchestrator (str): controller IP address
    kubeconf (str): path to orchestrator kubeconfig

**Usage**:

```console
$ ezlabctl ezua create-workload-cluster [OPTIONS] ORCHESTRATOR_IP
```

**Arguments**:

* `ORCHESTRATOR_IP`: [required]

**Options**:

* `--kubeconf TEXT`: [default: ./ezfab-orchestrator-kubeconfig]
* `--cluster-name TEXT`: [default: ezlab]
* `--help`: Show this message and exit.

### `ezlabctl ezua install`

**Usage**:

```console
$ ezlabctl ezua install [OPTIONS] ORCHESTRATOR_IP WORKERS...
```

**Arguments**:

* `ORCHESTRATOR_IP`: [required]
* `WORKERS...`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ezlabctl ezua remove`

Remove UA

Args:
    host (str): hostname/IP address to destroy

**Usage**:

```console
$ ezlabctl ezua remove [OPTIONS] HOST
```

**Arguments**:

* `HOST`: [required]

**Options**:

* `--ezfabrelease TEXT`: [default: ./ezfab-release.tgz]
* `--kubeconf TEXT`: [default: ./ezfab-orchestrator-kubeconfig]
* `--help`: Show this message and exit.

### `ezlabctl ezua with-rest`

**Usage**:

```console
$ ezlabctl ezua with-rest [OPTIONS]
```

**Options**:

* `--cluster-name TEXT`: [default: ezlab]
* `--help`: Show this message and exit.

## `ezlabctl info`

print usage

**Usage**:

```console
$ ezlabctl info [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `ezlabctl prepare`

Configure vm for given product

<ip>        : IP address
<name>      : Short hostname
<product>   : ezdf | ezua | generic

**Usage**:

```console
$ ezlabctl prepare [OPTIONS] VM_IP VM_NAME PRODUCT:{ezdf|ezua|generic}
```

**Arguments**:

* `VM_IP`: [required]
* `VM_NAME`: [required]
* `PRODUCT:{ezdf|ezua|generic}`: [required]

**Options**:

* `--help`: Show this message and exit.
