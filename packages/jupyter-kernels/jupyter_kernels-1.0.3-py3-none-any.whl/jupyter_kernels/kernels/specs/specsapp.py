import warnings

from tornado.httpclient import HTTPClient
from tornado.escape import json_decode, json_encode
from rich.console import Console
from rich.table import Table
from datalayer.application import NoStart

from ...application_base import JupyterKernelsBaseApp


def new_kernel_table():
    table = Table(title="Jupyter Kernel")
    table.add_column("Id", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Last Activity", justify="right", style="green", no_wrap=True)
    table.add_column("Execution State", justify="right", style="green", no_wrap=True)
    table.add_column("Connections", justify="right", style="green", no_wrap=True)
    return table


def add_kernel_to_table(table, kernel):
    table.add_row(
        kernel["id"],
        kernel["name"],
        kernel["last_activity"],
        kernel["execution_state"],
        str(kernel["connections"]),
    )


class KernelCreateApp(JupyterKernelsBaseApp):
    """An application to create a kernel."""

    description = """
      An application to create the kernel.
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for kernel create.")
            self.exit(1)
        kernel_name = self.extra_args[0]
        client = HTTPClient()
        response = client.fetch(
            '{}/api/kernels'.format(self.server_base_url),
            method='POST',
            headers={
                "Authorization": f"token {self.server_token}",
            },
            body=json_encode({
                "name": kernel_name,
#                "path": "test.ipynb",
            })
        )
        kernel = json_decode(response.body)
        table = new_kernel_table()
        add_kernel_to_table(table, kernel)
        console = Console()
        console.print(table)


class KernelListApp(JupyterKernelsBaseApp):
    """An application to list the kernels."""

    description = """
      An application to list the kernels.
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for kernel list.")
            self.exit(1)
        client = HTTPClient()
        response = client.fetch(
            '{}/api/kernels'.format(self.server_base_url),
            method='GET',
            headers={
                "Authorization": f"token {self.server_token}",
            }
        )
        kernels = json_decode(response.body)
        table = new_kernel_table()
        for kernel in kernels:
            add_kernel_to_table(table, kernel)
        console = Console()
        console.print(table)


class KernelSpecsApp(JupyterKernelsBaseApp):
    """A Kernel application."""

    description = """
      The JupyterKernels application for Kernels.
    """

    subcommands = {}
    subcommands["create"] = (KernelCreateApp, KernelCreateApp.description.splitlines()[0])
    subcommands["list"] = (KernelListApp, KernelListApp.description.splitlines()[0])

    def start(self):
        try:
            super().start()
            self.log.error(f"One of `{'`, `'.join(KernelSpecsApp.subcommands.keys())}` must be specified.")
            self.exit(1)
        except NoStart:
            pass
        self.exit(0)
