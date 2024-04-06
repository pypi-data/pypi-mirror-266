from ezlab.parameters import MAPR_CORE_VERSION, MAPR_MEP_VERSION


def get_local_repo(repo: str, repo_url: str):
    return rf"""[local-{repo.lower()}]
name = Local {repo}
enabled = 1
gpgcheck = 0
baseurl = {repo_url.rstrip('/')}/\$releasever/{repo}/\$basearch/os
ui_repoid_vars = releasever basearch
priority=1
proxy=
"""


def get_insecure_registry(registry):
    return f"""
{
  "log-driver": "journald",
  "insecure-registries" : [ {registry} ]
}
"""


def get_epel_repo(epelurl):
    return f"""
[local-epel]
name = Local EPEL
enabled = 1
gpgcheck = 0
baseurl = {epelurl}
priority=1
proxy="""


def get_mapr_repo(repo):
    return f"""
[ezmeral]
name = Ezmeral Packages
enabled = 1
gpgcheck = 0
baseurl = {repo.rstrip('/')}/v{MAPR_CORE_VERSION}/redhat
priority=1
proxy=

[ezmeral-eep]
name = Ezmeral EEP Packages
enabled = 1
gpgcheck = 0
baseurl = {repo.rstrip('/')}/MEP/MEP-{MAPR_MEP_VERSION}/redhat
priority=1
proxy=

"""
