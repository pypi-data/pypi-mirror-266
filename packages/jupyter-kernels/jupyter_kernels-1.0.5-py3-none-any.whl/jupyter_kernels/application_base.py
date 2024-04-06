from ._version import __version__

from traitlets import Bool, Unicode

from datalayer.application import DatalayerApp, base_aliases, base_flags


jupyter_kernels_aliases = dict(base_aliases)
jupyter_kernels_aliases["cloud"] = "JupyterKernelsBaseApp.cloud"
jupyter_kernels_aliases["server-base-url"] = "JupyterKernelsBaseApp.server_base_url"
jupyter_kernels_aliases["server-base-ws-url"] = "JupyterKernelsBaseApp.server_base_ws_url"
jupyter_kernels_aliases["server-token"] = "JupyterKernelsBaseApp.server_token"

jupyter_kernels_flags = dict(base_flags)
jupyter_kernels_flags["no-minimize"] = (
    {"JupyterKernelsBaseApp": {"minimize": False}},
    "Do not minimize a production build.",
)


class JupyterKernelsBaseApp(DatalayerApp):
    name = "jupyter_kernels"

    version = __version__

    aliases = jupyter_kernels_aliases

    flags = jupyter_kernels_flags

    cloud = Unicode("ovh", config=True, help="")

    minimize = Bool(True, config=True, help="")

    server_base_url = Unicode("http://localhost:8888", config=True, help="")

    server_base_ws_url = Unicode("ws://localhost:8888", config=True, help="")

    server_token = Unicode("60c1661cc408f978c309d04157af55c9588ff9557c9380e4fb50785750703da6", config=True, help="")

    router_url = Unicode("http://jupyter-router-api-svc:2001/api/routes", config=True, help="")

    router_token = Unicode("test", config=True, help="")

    lang = Unicode("python", config=True, help="")

    kernel_id = Unicode(None, allow_none=True, config=True, help="")
