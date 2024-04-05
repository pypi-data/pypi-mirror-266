"""Config handler."""

import json

import tornado

from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

from ..._version import __version__


# pylint: disable=W0223
class ConfigHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for configurations."""

    @tornado.web.authenticated
    def get(self):
        """Returns the configurations of the server extensions."""
        res = json.dumps({
            "extension": "jupyter_kernels",
            "version": __version__,
            "configuration": dict(
                [
                    (
                        ''.join(
                            w.title() if idx > 0 else w
                            for idx, w in enumerate(k.split('_'))
                        ),
                        v
                    ) for k, v in self.settings['jupyter_kernels_config'].items()
                ]
            )
        })
        self.finish(res)
