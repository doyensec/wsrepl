import importlib.util
import os
import os.path
import inspect
from urllib.parse import urlparse

from wsrepl.Plugin import Plugin


# Sanitize url and construct likely Origin, return a tuple of (url, origin)
def sanitize_url(url: str, origin: str = None) -> tuple[str, str]:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme

    if scheme == "http":
        parsed_url.scheme = "ws"
    elif scheme == "https":
        parsed_url.scheme = "wss"
    elif not scheme:
        # No scheme specified, assume wss
        parsed_url.scheme = "wss"
    url = parsed_url.geturl()

    # Set Origin header to match wss url, unless user specified a custom one or opted out
    if origin is None:
        if scheme == "wss":
            origin = "https://" + parsed_url.hostname
        else:
            origin = "http://" + parsed_url.hostname
    elif not origin:
        # False or empty string means no origin header
        origin = None

    return (url, origin)


def build_ws_args(url: str, origin: str | None = None, user_agent: str | None = None,
                  extra_headers: list[str] | None = None, extra_headers_file: str | None = None,
                  native_ping_enabled: bool = True, heartbeet_interval: int = 24, proxy: str | None = None,
                  skip_verify: bool = False):

    # Convert http / https into ws / wss if needed
    url, origin = sanitize_url(url, origin)

    args= {
        "url": url,
        "origin": origin
    }

    # --headers-file takes precedence over -H, --header
    if extra_headers_file:
        with open(extra_headers_file, "r") as f:
            extra_headers = [line.strip() for line in f.read().splitlines()]

    # Headers are provided as a list of strings, each string is a header in the format "Header-Name: Header-Value"
    if extra_headers:
        headers = {}
        for header in extra_headers:
            name, value = header.split(":", 1)
            headers[name.strip()] = value.strip()
        args["headers"] = headers

    # Set User-Agent header if specified
    if user_agent:
        headers = headers if headers else {}
        headers["User-Agent"] = user_agent

    # Disable native ping/pong
    if not native_ping_enabled:
        args["autoping"] = False

    # How often to initiate ping/pong
    if heartbeet_interval:
        args["heartbeat"] = heartbeet_interval

    # HTTP proxy
    if proxy:
        args["proxy"] = proxy

    # Disable SSL verification
    if skip_verify:
        args["ssl"] = False

    return args


def _get_plugin_name(plugin_path):
    # Extracts the module name from the plugin file path
    plugin_file = os.path.basename(plugin_path)
    plugin_name = os.path.splitext(plugin_file)[0]
    return plugin_name


def load_plugin(plugin_path) -> type[Plugin]:
    """Loads a plugin from a file path or returns an empty plugin if no path is specified"""
    if not plugin_path:
        return Plugin

    if not os.path.isfile(plugin_path):
        raise Exception("Plugin not found: {}".format(plugin_path))

    plugin_name = _get_plugin_name(plugin_path)
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find a subclass of Plugin in the module
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Plugin) and obj is not Plugin:
            # Instantiate it and return
            return obj

    raise ValueError(f"No subclass of Plugin found in {plugin_path}")
