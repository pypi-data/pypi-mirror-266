from ezlab.parameters import *
from ezlab.utils import *


logger = logging.getLogger("ezua")


def precheck():
    """Fabric pre-checks for roles"""

    # write_precheck_yaml()

    host = "LOCAL"
    role = ""
    # "ezfabricctl prechecks --input /tmp/prechecksInput.yaml --status /tmp/prechecks/prechecksStatus.txt",
    for out in execute("./tmp/ezfabricctl pc -i ./tmp/prechecksInput.yaml -s ./tmp/prechecks/prechecksStatus.txt"):
        if "Running checks for Ezmeral Unified Analytics role " in out:
            # should use regex but too lazy for it
            # extracting from string '***** Running checks for Ezmeral Unified Analytics role "worker" on host "vm23.kaya.home"'
            hostrole = out.split('role "')[1]
            role = hostrole.split('"')[0]
            host = hostrole.split('"')[2]

        logger.info("[ %s %s ]: %s", role.upper(), host, out)

        if "Additional information for debugging is written to" in out:
            # reset the host/role pair
            host = "LOCAL"
            role = ""


def install():
    """
    UA orchestrator installation
    """

    # write_ezkf_input_yaml()

    # "ezfabricctl orchestrator init --releasepkg /tmp/ezfab-release.tgz --input /tmp/ezkf-input.yaml --status /tmp/ezkf-orchestrator/status.txt --save-kubeconfig /tmp/ezkf-orchestrator/mgmt-kubeconfig",
    for out in execute(
        "./tmp/ezfabricctl o init -p ./tmp/ezfab-release.tgz -i ./tmp/ezkf-input.yaml -s ./tmp/ezkf-orchestrator/status.txt --save-kubeconfig ./tmp/ezkf-orchestrator/mgmt-kubeconfig"
    ):
        # ignore transfer messages, overloading UI
        if "Transferring to " not in out:
            logger.info(out)
            markword = "Save kubeconfig in "
            if markword in out:
                msg = out.split(markword)[1]
                APP_STATUS_CONTAINER.append(("Orchestrator Kubeconfig", msg.replace("./tmp", "/files", 1)))
                status_container.refresh()

    # write_hostPoolConfig_yaml()

    # "ezfabricctl poolhost init --input /tmp/hostPoolConfig.yaml --orchestrator-kubeconfig /tmp/ezkf-orchestrator/mgmt-kubeconfig --status /tmp/workload/hostPoolConfigStatus.txt",
    for out in execute(
        "./tmp/ezfabricctl ph i -i ./tmp/hostPoolConfig.yaml -c ./tmp/ezkf-orchestrator/mgmt-kubeconfig -s ./tmp/workload/hostPoolConfigStatus.txt"
    ):
        logger.info(out)

    # write_clusterConfig_yaml()

    # "ezfabricctl workload init --input /tmp/clusterConfig.yaml --orchestrator-kubeconfig /tmp/ezkf-orchestrator/mgmt-kubeconfig --status /tmp/workload/clusterConfigStatus.txt",
    for out in execute(
        "./tmp/ezfabricctl w i -i ./tmp/clusterConfig.yaml -c ./tmp/ezkf-orchestrator/mgmt-kubeconfig -s ./tmp/workload/clusterConfigStatus.txt"
    ):
        logger.info(out)

    # "ezfabricctl workload get kubeconfig --input /tmp/clusterConfig.yaml --orchestrator-kubeconfig /tmp/ezkf-orchestrator/mgmt-kubeconfig --status /tmp/workload/clusterConfigStatus.txt",
    for out in execute(
        "./tmp/ezfabricctl w g k -n ezlab -i ./tmp/clusterConfig.yaml -c ./tmp/ezkf-orchestrator/mgmt-kubeconfig -s ./tmp/workload/clusterConfigStatus.txt --save-kubeconfig ./tmp/workload/cluster-kubeconfig"
    ):
        logger.info(out)
        markword = "Fetched kubeconfig for "
        if markword in out:
            APP_STATUS_CONTAINER.append(("Workload Kubeconfig", "/files/workload/cluster-kubeconfig"))
            status_container.refresh()


def deploy():

    # AUTH_DATA={
    #     "admin_user": {
    #         "fullname": "Ez Admin",
    #         "email": "admin@ez.lab",
    #         "password": "admin",
    #         "username": "admin123"
    #     }
    # }

    # write_ezkf_workloaddeploy_yaml()

    # kubectl --kubeconfig=$WORKER_KUBECONFIG apply -f -
    for out in execute("kubectl --kubeconfig=./tmp/workload/cluster-kubeconfig apply -f ./tmp/ezkfWorkloadDeploy.yaml"):
        logger.info(out)
        if "ezkfworkloaddeploy.ezkfops.hpe.ezkf-ops.com/ezlab" in out and any(i in out for i in ["created", "configured", "unchanged"]):
            # STATUS="kubectl --kubeconfig=./worker_kubeconfig get ezkfworkloaddeploy/$CLUSTER_NAME -n $CLUSTER_NAME -o json | jq -r '.status.status'"
            logger.info(
                "Monitor CR Status with: %s",
                "kubectl --kubeconfig=./worker_kubeconfig get ezkfworkloaddeploy/$CLUSTER_NAME -n $CLUSTER_NAME -o json | jq -r '.status.status'",
            )

        # logger.warning("Deployment failed: %s", out)

    return True


def write_precheck_yaml():
    """
    Write the file for prechecks
    """

    hosts_yaml = ""
    for host in app.storage.general[UA]["workers"].split(","):
        hosts_yaml += f"      - host: {host}\n"

    input = f"""
defaultHostCredentials:
  sshUserName: {app.storage.general["config"]["username"]}
  sshPassword: {toB64({app.storage.general["config"]["password"]})}
  sshPort: 22
sudoPrefix: ""
prechecks:
  coordinator:
    controlplane: [
      - host: {app.storage.general[UA]["orchestrator"]}
    ]
  ua:
    controlplane:
      - host: {app.storage.general[UA]["controller"]}
    worker:
{hosts_yaml}
"""
    with open("./tmp/prechecksInput.yaml", "wt", "utf-8") as f:
        f.write(input)


def write_ezkf_input_yaml():
    """
    Write the file for orchestrator deployment
    """

    input = f"""
defaultHostCredentials:
  sshUserName: {app.storage.general["config"]["username"]}
  sshPassword: {toB64(app.storage.general["config"]["password"])}
  sshPort: 22
airgap:
  registryUrl: {app.storage.general[UA]["registryUrl"]}
  registryInsecure: {app.storage.general[UA]["registryInsecure"]}
  registryCaFile: {app.storage.general[UA]["registryCaFile"]}
  userName: {app.storage.general[UA]["registryUsername"]}
  password: {toB64(app.storage.general[UA]["registryPassword"])}
orchestrator:
  deployTarget: pph
  controlPlane:
    enableHa: false
    externalUrl: ""
  network:
    pods:
      cidrBlocks: 10.224.0.0/16
    serviceDomain: cluster.local
    services:
      cidrBlocks: 10.96.0.0/12
hosts:
  - host: {app.storage.general[UA]["orchestrator"]}
webproxy:
  httpProxy: {app.storage.general["config"]["proxy"]}
  httpsProxy: {app.storage.general["config"]["proxy"]}
  noProxy: {NO_PROXY.format(vm_domain=app.storage.general["config"]["domain"], vm_network=app.storage.general["config"]["cidr"],no_proxy=app.storage.general[UA]["orchestrator"])}
"""
    with open("./tmp/ezkf-input.yaml", "wt", "utf-8") as f:
        f.write(input)


def write_hostPoolConfig_yaml():
    """ """
    workers = app.storage.general[UA]["workers"].split(",")
    input = f"""
defaultHostCredentials:
  sshUserName: {app.storage.general["config"]["username"]}
  sshPassword: {toB64(app.storage.general["config"]["password"])}
  sshPort: 22
hosts:
  - host: {app.storage.general[UA]["controller"]}
    labels:
      role: controlplane
  - host: {workers[0]}
    labels:
      role: worker
  - host: {workers[1]}
    labels:
      role: worker
  - host: {workers[2]}
    labels:
      role: worker
"""
    with open("./tmp/hostPoolConfig.yaml", "wt", "utf-8") as f:
        f.write(input)


def write_clusterConfig_yaml():
    """ """
    input = f"""
workload:
  deployTarget: pph
  deployEnv: ezkube
  workloadType: ezua
  clusterName: ezlab
  resources:
    vcpu: 96
  controlPlaneHostLabels:
    role: controlplane
  workerHostLabels:
    role: worker
  dataFabricHostLabels:
    role: worker
  gpuHostLabels:
    role: worker
  clusterLabels: {{}}
  controlplane:
    enableHa: false
    controlPlaneEndpoint: {app.storage.general[UA]["controller"]}
airgap:
  registryUrl: {app.storage.general[UA]["registryUrl"]}
  registryInsecure: {app.storage.general[UA]["registryInsecure"]}
  registryCaFile: {app.storage.general[UA]["registryCaFile"]}
  userName: {app.storage.general[UA]["registryUsername"]}
  password: {toB64(app.storage.general[UA]["registryPassword"])}
"""

    with open("./tmp/clusterConfig.yaml", "wt", "utf-8") as f:
        f.write(input)


def write_ezkf_workloaddeploy_yaml():
    """
    Write the file for UA apps deployment
    """

    input = """
apiVersion: v1
data:
  userName: ezmeral
  password: QWRtaW4xMjMu
  registryCaFile: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUYxVENDQTcyZ0F3SUJBZ0lVQTlaVWlZRjhmSVArc0loV0IyL0NQNmxuRFJ3d0RRWUpLb1pJaHZjTkFRRUwKQlFBd2NqRUxNQWtHQTFVRUJoTUNSMEl4RURBT0JnTlZCQWdNQjBWdVoyeGhibVF4RHpBTkJnTlZCQWNNQmt4dgpibVJ2YmpFU01CQUdBMVVFQ2d3SlMyRjVZU0JJYjIxbE1Rd3dDZ1lEVlFRTERBTk1ZV0l4SGpBY0Jna3Foa2lHCjl3MEJDUUVXRDJGa2JXbHVRR3RoZVdFdWFHOXRaVEFlRncweU5EQXpNamt3TURVMU1qWmFGdzAwTkRBek1qUXcKTURVMU1qWmFNSEl4Q3pBSkJnTlZCQVlUQWtkQ01SQXdEZ1lEVlFRSURBZEZibWRzWVc1a01ROHdEUVlEVlFRSApEQVpNYjI1a2IyNHhFakFRQmdOVkJBb01DVXRoZVdFZ1NHOXRaVEVNTUFvR0ExVUVDd3dEVEdGaU1SNHdIQVlKCktvWklodmNOQVFrQkZnOWhaRzFwYmtCcllYbGhMbWh2YldVd2dnSWlNQTBHQ1NxR1NJYjNEUUVCQVFVQUE0SUMKRHdBd2dnSUtBb0lDQVFDOFFsUGdrbGFBUVNubUJTSlcwQjdBVWh2K1JUcU1nRml1ZWxyWlJxYjBZQWFxTW1ZZApsekdJalUyWHM5STBndTREZTBXMUN4b0RReTlKSHhjVVFZYUg4UStYdVp3ZmpmT3lNSFlZQUIwVEx4WWE3dlYyClc0cnVBSVdKWStOTVdHd2EySTdCVG1Odi9lYUpEVVNFZWJ2UVUzYSt4cHRBK2xuNHFmTVRWcDM2c3hwU0FqRFAKV0VDaXkyTmZYKy9QNFNNY3BnR0t6VVJqZi9FdG9mUzN2eW5peWpGS3pjNWQxK085VU1BWHFWZ1Z1NnY1Yk1XVQpWbFVZYVVNQUwzMmxkai9sZE9rWCtzeks5R0hGWkJUU3Y5cFdQZnc5VHdzQ0RIczRONCtSeTBGZ3dndGJURXhOCkZDUk5hOVEzVWNsblMrV2crcjhiaXJnTUpPa1ZJSzhSSEtsOGtrMGJ2UThYbzRDTmhDMGZSUVUyUWJIQlFZUG0Kd1RQV1lvRlYyQnh3UFhCejFmSWFTWHBESVh4WEo3OTNZbnFCOWhGUXFnRVk4YVZIOUNXenJPTzBMSXpFb01PbAp6Wnk1VUpNVHo3Uk5xYmZMUzVQUlR3c0RrSzQrQ0dEckNEcGFoUTFNZDlnSjh4cUpmcWdQTTlWMzlQb0VnSE5DCldtZkRVOVVlMnByd3FPN051dHpzZEtBYjYzcXprR3dabTE5a3lmelhPVHNsSmQxTWRFM2N4THpxSDV0TEp3YUwKNGhiV2RCc0tLbFF3VWdBb1pna21VOW43OHhWRDd0YXIxR1lPOHNtRFV5MG00cVh2aktWakw1aFRNQWdia3BjLwoyMVc3S0d3YnFpNUplT2UvWmpFaWZzNUtPTklwZkhJekc3ek1vMHkyN2FCc2UzbDlKbWxaR0dJbGZRSURBUUFCCm8yTXdZVEFkQmdOVkhRNEVGZ1FVZWhML2trcTBJR3NGOW9CbTlZSGVaQ3VDb2xnd0h3WURWUjBqQkJnd0ZvQVUKZWhML2trcTBJR3NGOW9CbTlZSGVaQ3VDb2xnd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBT0JnTlZIUThCQWY4RQpCQU1DQVlZd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dJQkFFTkFJNzZoeVJoL0p0eW9mcXRFMkVuK2RwQlo2UHdVCmVzaE5XUFNwSUoyQUpoS09VWVdhQUZtaDF1MlBZZFNxaGU3VjJvdE9OMy8xUi9aUHFXWVhsNXBFVW1UbFVhSVcKZWd0ZXlrZDN5MFRtMGdBU3JETUQrRmdrMnRHcUtNUkNzT1hDV3lhUUwrUGVyYW11VlZ1VnlpTGJrNlNWTEd5VQpDNkdNK0V6SVV3bWkvUzh4ZWI5ZWZJdFlMNWhBdUE1aVVEUnQyYkMvNzNFS2YrYWVzSXNkOWRwVjR3bWRKT3dRCnZBVmMxLzFOeEU3eG12WmRXNnFVTU9OMWdWVmxNaEd0VEVEc3FjV21RMjhmQzE1Q3FkYlFHUmcrd2xVbXhZRVYKM3hVdzRVYnhsZXRyc09VWEphbkgrNDZTSmkybDhaOWdvUjgrbk9lS2hsS0Y5VlJKRDZCeU1QVG93SEV1Y2pWLwpPeEhac2QxSDVCcjllVTFEVE05UEM2RFN3bEkxdEhsci9vT3VSRXVidC82cmRucUJuejhPUFQwN25pZmFZSkFoCjArNTVlUWlkU2RtUnI3dWh2Zk5JNEhBUFE4SU9ISDNmdGlYUXhsZGNGRjNlcGlYdVBORWRMWkNWWms1WXpoSTgKMXlVZWFJTGg4ck1WeElBZllKYmlZaVl6UmJodDRWajZBazNWN1I2WUp1TjFkejN6c1NjUmQ0S3N2bk5kVVY4Lwp4RS9MRnFqeE9XOFZaVENhL3hmbDUxa1JzbXprbloxL2RsZTVtemNCMkZwZEgzSTEyNHJLNW81eG1aWnV6TWlGCmo2UTZZbGZKRzVpSTBVYkNraE51aVIrSGlrRi9ZTWxiZ2M5ZXhMQW1BcngxRGFqOGsvbXkvdmQ1dUlYc1ZJdkkKdUdOSVJ3dVd3cDRLCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
kind: Secret
metadata:
  name: airgap
  namespace: ezlab
type: Opaque


---
apiVersion: v1
stringData:
  internal_auth: ewogICJhZG1pbl91c2VyIjogeyAKICAgICJmdWxsbmFtZSI6ICJhZG1pbiIsIAogICAgImVtYWlsIjogImFkbWluQGhwZS5jb20iLCAKICAgICJwYXNzd29yZCI6ICJhZG1pbjEyMyIsIAogICAgInVzZXJuYW1lIjogImFkbWluIiAKICB9IAp9
kind: Secret
metadata:
  name: authconfig
  namespace: ezlab
type: Opaque


---
apiVersion: ezkfops.hpe.ezkf-ops.com/v1alpha1
kind: EzkfWorkloadDeploy
metadata:
  name: ezlab
  namespace: ezlab
spec:
  deploytarget: pph
  workloadtype: ezua
  clustername: ezlab
  domainname: "ezua.kaya.home"
  isAirgap: true
  deployallinfra: true
  genericaddons:
    machine: true
    ezkube: true
  proxy:
    httpProxy: http://10.1.1.1:3128/
    httpsProxy: http://10.1.1.1:3128/
    noProxy: 10.96.0.0/12,10.224.0.0/16,10.43.0.0/16,192.168.0.0/16,.external.hpe.local,localhost,.cluster.local,.svc,.default.svc,127.0.0.1,169.254.169.254,.kaya.home,10.1.1.0/24,10.1.1.21,10.1.1.22,10.1.1.23,10.1.1.24,10.1.1.25
  workloadaddons:
    ua_prep: true
    hpecp_agent: true
    oidc: true
    kyverno: true
    monitoring: true
    keycloak: true
    chartmuseum: true
    ezaf_controller: true
  deployallapps: true # always set to true from UA
  authconfig:
    secret_name: "authconfig"
  airgap:
    secret_name: "airgap"
    registryUrl: 10.1.1.4/ezmeral/
    registryInsecure: false
    registryCaData: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUYxVENDQTcyZ0F3SUJBZ0lVQTlaVWlZRjhmSVArc0loV0IyL0NQNmxuRFJ3d0RRWUpLb1pJaHZjTkFRRUwKQlFBd2NqRUxNQWtHQTFVRUJoTUNSMEl4RURBT0JnTlZCQWdNQjBWdVoyeGhibVF4RHpBTkJnTlZCQWNNQmt4dgpibVJ2YmpFU01CQUdBMVVFQ2d3SlMyRjVZU0JJYjIxbE1Rd3dDZ1lEVlFRTERBTk1ZV0l4SGpBY0Jna3Foa2lHCjl3MEJDUUVXRDJGa2JXbHVRR3RoZVdFdWFHOXRaVEFlRncweU5EQXpNamt3TURVMU1qWmFGdzAwTkRBek1qUXcKTURVMU1qWmFNSEl4Q3pBSkJnTlZCQVlUQWtkQ01SQXdEZ1lEVlFRSURBZEZibWRzWVc1a01ROHdEUVlEVlFRSApEQVpNYjI1a2IyNHhFakFRQmdOVkJBb01DVXRoZVdFZ1NHOXRaVEVNTUFvR0ExVUVDd3dEVEdGaU1SNHdIQVlKCktvWklodmNOQVFrQkZnOWhaRzFwYmtCcllYbGhMbWh2YldVd2dnSWlNQTBHQ1NxR1NJYjNEUUVCQVFVQUE0SUMKRHdBd2dnSUtBb0lDQVFDOFFsUGdrbGFBUVNubUJTSlcwQjdBVWh2K1JUcU1nRml1ZWxyWlJxYjBZQWFxTW1ZZApsekdJalUyWHM5STBndTREZTBXMUN4b0RReTlKSHhjVVFZYUg4UStYdVp3ZmpmT3lNSFlZQUIwVEx4WWE3dlYyClc0cnVBSVdKWStOTVdHd2EySTdCVG1Odi9lYUpEVVNFZWJ2UVUzYSt4cHRBK2xuNHFmTVRWcDM2c3hwU0FqRFAKV0VDaXkyTmZYKy9QNFNNY3BnR0t6VVJqZi9FdG9mUzN2eW5peWpGS3pjNWQxK085VU1BWHFWZ1Z1NnY1Yk1XVQpWbFVZYVVNQUwzMmxkai9sZE9rWCtzeks5R0hGWkJUU3Y5cFdQZnc5VHdzQ0RIczRONCtSeTBGZ3dndGJURXhOCkZDUk5hOVEzVWNsblMrV2crcjhiaXJnTUpPa1ZJSzhSSEtsOGtrMGJ2UThYbzRDTmhDMGZSUVUyUWJIQlFZUG0Kd1RQV1lvRlYyQnh3UFhCejFmSWFTWHBESVh4WEo3OTNZbnFCOWhGUXFnRVk4YVZIOUNXenJPTzBMSXpFb01PbAp6Wnk1VUpNVHo3Uk5xYmZMUzVQUlR3c0RrSzQrQ0dEckNEcGFoUTFNZDlnSjh4cUpmcWdQTTlWMzlQb0VnSE5DCldtZkRVOVVlMnByd3FPN051dHpzZEtBYjYzcXprR3dabTE5a3lmelhPVHNsSmQxTWRFM2N4THpxSDV0TEp3YUwKNGhiV2RCc0tLbFF3VWdBb1pna21VOW43OHhWRDd0YXIxR1lPOHNtRFV5MG00cVh2aktWakw1aFRNQWdia3BjLwoyMVc3S0d3YnFpNUplT2UvWmpFaWZzNUtPTklwZkhJekc3ek1vMHkyN2FCc2UzbDlKbWxaR0dJbGZRSURBUUFCCm8yTXdZVEFkQmdOVkhRNEVGZ1FVZWhML2trcTBJR3NGOW9CbTlZSGVaQ3VDb2xnd0h3WURWUjBqQkJnd0ZvQVUKZWhML2trcTBJR3NGOW9CbTlZSGVaQ3VDb2xnd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBT0JnTlZIUThCQWY4RQpCQU1DQVlZd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dJQkFFTkFJNzZoeVJoL0p0eW9mcXRFMkVuK2RwQlo2UHdVCmVzaE5XUFNwSUoyQUpoS09VWVdhQUZtaDF1MlBZZFNxaGU3VjJvdE9OMy8xUi9aUHFXWVhsNXBFVW1UbFVhSVcKZWd0ZXlrZDN5MFRtMGdBU3JETUQrRmdrMnRHcUtNUkNzT1hDV3lhUUwrUGVyYW11VlZ1VnlpTGJrNlNWTEd5VQpDNkdNK0V6SVV3bWkvUzh4ZWI5ZWZJdFlMNWhBdUE1aVVEUnQyYkMvNzNFS2YrYWVzSXNkOWRwVjR3bWRKT3dRCnZBVmMxLzFOeEU3eG12WmRXNnFVTU9OMWdWVmxNaEd0VEVEc3FjV21RMjhmQzE1Q3FkYlFHUmcrd2xVbXhZRVYKM3hVdzRVYnhsZXRyc09VWEphbkgrNDZTSmkybDhaOWdvUjgrbk9lS2hsS0Y5VlJKRDZCeU1QVG93SEV1Y2pWLwpPeEhac2QxSDVCcjllVTFEVE05UEM2RFN3bEkxdEhsci9vT3VSRXVidC82cmRucUJuejhPUFQwN25pZmFZSkFoCjArNTVlUWlkU2RtUnI3dWh2Zk5JNEhBUFE4SU9ISDNmdGlYUXhsZGNGRjNlcGlYdVBORWRMWkNWWms1WXpoSTgKMXlVZWFJTGg4ck1WeElBZllKYmlZaVl6UmJodDRWajZBazNWN1I2WUp1TjFkejN6c1NjUmQ0S3N2bk5kVVY4Lwp4RS9MRnFqeE9XOFZaVENhL3hmbDUxa1JzbXprbloxL2RsZTVtemNCMkZwZEgzSTEyNHJLNW81eG1aWnV6TWlGCmo2UTZZbGZKRzVpSTBVYkNraE51aVIrSGlrRi9ZTWxiZ2M5ZXhMQW1BcngxRGFqOGsvbXkvdmQ1dUlYc1ZJdkkKdUdOSVJ3dVd3cDRLCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
"""
