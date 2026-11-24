"""Installed system-wide so every Python start routes urllib through the proxy.

rusty_v8's prepare_android_v8.py and its build.rs fetch the chromium sysroot
and clang from commondatastorage.googleapis.com using urllib.request.urlopen,
which ignores HTTPS_PROXY on its own. Dropping this file into
site-packages makes those downloads use the proxy without editing upstream.
"""

import os
import urllib.request

_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

if _proxy:
    _no_proxy = (os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or "")
    _no_proxy_list = [item.strip() for item in _no_proxy.split(",") if item.strip()]

    class _ProxiedWithBypass(urllib.request.ProxyHandler):
        def proxy_open(self, req, proxy, type):
            host = req.host or ""
            for skip in _no_proxy_list:
                if skip and (host == skip or host.endswith("." + skip)):
                    return None
            return super().proxy_open(req, proxy, type)

    urllib.request.install_opener(
        urllib.request.build_opener(
            _ProxiedWithBypass({"http": _proxy, "https": _proxy}),
        )
    )