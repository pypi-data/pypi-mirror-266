"""The Jupyter Kernels Server application."""

import os

from traitlets import CInt

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from ._version import __version__

from .handlers.index.handler import IndexHandler
from .handlers.config.handler import ConfigHandler
from .handlers.jump.handler import JumpHandler
from .handlers.content.handler import ContentHandler
from .handlers.echo.handler import WsEchoHandler
from .handlers.relay.handler import WsRelayHandler
from .handlers.proxy.handler import WsProxyHandler
from .handlers.ping.handler import WsPingHandler
from .handlers.service_worker.handler import ServiceWorkerHandler

# from .keys.keys import setup_keys


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(
    os.path.dirname(__file__), "./templates")


class JupyterKernelsExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter Kernels Server extension."""

    name = "jupyter_kernels"

    extension_url = "/jupyter_kernels"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    max_kernels = CInt(
        3, config=True, help="Maximal number of remote kernels that can be spawned by an user."
    )

    max_temporary_kernels = CInt(
        3,
        config=True,
        help="Maximal number of temporary kernels that can be spawned by an user. They are not taking into account in the max_kernels limit."
    )

    def initialize_settings(self):
#        setup_keys(self.log)
        settings = dict(
            max_kernels=self.max_kernels,
            max_temporary_kernels=self.max_temporary_kernels
        )
        self.settings.update(**settings)

    def initialize_templates(self):
        self.serverapp.jinja_template_vars.update(
            {"jupyter_kernels_version": __version__})

    def initialize_handlers(self):
        pod_name_regex = r"(?P<pod_name>[\w\.\-%]+)"
        handlers = [
            ("jupyter_kernels", IndexHandler),
            (url_path_join("jupyter_kernels", "config"), ConfigHandler),
            (url_path_join("jupyter_kernels", "content"), ContentHandler),
            (r"/jupyter_kernels/jump/%s" % pod_name_regex, JumpHandler),
            (url_path_join("jupyter_kernels", "echo"), WsEchoHandler),
            (url_path_join("jupyter_kernels", "relay"), WsRelayHandler),
            (url_path_join("jupyter_kernels", "proxy"), WsProxyHandler),
            (url_path_join("jupyter_kernels", "ping"), WsPingHandler),
            (url_path_join("jupyter_kernels", "service-worker",
             r"([^/]+\.js)"), ServiceWorkerHandler),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterKernelsExtensionApp.launch_instance
