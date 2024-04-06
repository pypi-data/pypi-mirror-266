from ezlab.parameters import NO_PROXY


def get_proxy_vars(proxy):
    if proxy[-1] != "/":
        proxy += "/"
    return {
        "HTTP_PROXY": proxy,
        "http_proxy": proxy,
        "HTTPS_PROXY": proxy,
        "https_proxy": proxy,
        "NO_PROXY": NO_PROXY,
        "no_proxy": NO_PROXY,
    }


def proxy_files(proxy_url, domain, cidr, noproxy):
    env = []
    prx = []
    for key, value in get_proxy_vars(proxy_url).items():
        val = value.format(vm_domain=domain, vm_network=cidr, no_proxy=noproxy)
        env.append(f"{key}={val}")
        prx.append(f"export {key}={val}")

    return [
        {"/etc/environment": "\n".join(env)},
        {"/etc/sysconfig/proxy": "\n".join(prx)},
    ]
