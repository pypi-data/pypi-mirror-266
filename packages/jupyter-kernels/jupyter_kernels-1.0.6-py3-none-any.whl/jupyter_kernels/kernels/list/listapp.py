import warnings

from datalayer.application import NoStart
from rich.console import Console
from rich.table import Table
from tornado.httpclient import HTTPClient
from tornado.escape import json_decode, json_encode

from ...application_base import JupyterKernelsBaseApp


def new_kernel_table(title="Jupyter Kernel"):
    table = Table(title=title)
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
        table = new_kernel_table(title="Jupyter Kernels")
        for kernel in kernels:
            add_kernel_to_table(table, kernel)
        console = Console()
        console.print(table)
