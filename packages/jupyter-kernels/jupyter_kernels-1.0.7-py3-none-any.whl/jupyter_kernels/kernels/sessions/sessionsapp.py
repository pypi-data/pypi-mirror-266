import warnings

from tornado.httpclient import HTTPClient
from tornado.escape import json_decode, json_encode
from rich.console import Console
from rich.table import Table
from datalayer.application import NoStart

from ...application_base import JupyterKernelsBaseApp


def new_session_table(title="Jupyter Session"):
    table = Table(title=title)
    table.add_column("Id", justify="right", style="cyan", no_wrap=True)
    table.add_column("Path", style="magenta", no_wrap=True)
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Type", justify="right", style="green", no_wrap=True)
    table.add_column("Kernel Id", justify="right", style="green", no_wrap=True)
    table.add_column("Kernel Name", justify="right", style="green", no_wrap=True)
    table.add_column("Kernel Last Activity", justify="right", style="green", no_wrap=True)
    table.add_column("Notebook Path", justify="right", style="green", no_wrap=True)
    table.add_column("Notebok Name", justify="right", style="green", no_wrap=True)
    return table


def add_session_to_table(table, session):
    """
    {
        'id': '21942928-d117-4f13-adfe-2f39c9b3e7c6',
        'path': 'Untitled3.ipynb',
        'name': 'Untitled3.ipynb',
        'type': 'notebook',
        'kernel': {'id': '19fa77fa-2a00-43e6-bb04-ee0a594d6261', 'name': 'run-python', 'last_activity': '2023-11-22T17:02:55.147289Z', 'execution_state': 'starting', 'connections': 0},
        'notebook': {'path': 'Untitled3.ipynb', 'name': 'Untitled3.ipynb'}
    }
    """
    table.add_row(
        session["id"],
        session["path"],
        session["name"],
        session["type"],
        session.get("kernel", {"id": ""})["id"],
        session.get("kernel", {"name": ""})["name"],
        session.get("kernel", {"last_activity": ""})["last_activity"],
        session.get("notebook", {"path": ""})["path"],
        session.get("notebook", {"name": ""})["name"],
    )


class KernelSessionCreateApp(JupyterKernelsBaseApp):
    """An application to create a session."""

    description = """
      An application to create the session.
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 3:  # pragma: no cover
            warnings.warn("Too many arguments were provided for session create.")
            self.exit(1)
        session_name = self.extra_args[0]
        session_path = self.extra_args[1]
        kernel_id = self.extra_args[2]
        client = HTTPClient()
        response = client.fetch(
            '{}/api/sessions'.format(self.server_base_url),
            method='POST',
            headers={
                "Authorization": f"token {self.server_token}",
            },
            body=json_encode({
                "name": session_name,
                "path": session_path,
                "type": "console",
                "kernel": {
                    "id": kernel_id,
                }
            })
        )
        session = json_decode(response.body)
        table = new_session_table()
        add_session_to_table(table, session)
        console = Console()
        console.print(table)


class KernelSessionListApp(JupyterKernelsBaseApp):
    """An application to list the sessions."""

    description = """
      An application to list the sessions.
    """

    def initialize(self, *args, **kwargs):
        """Initialize the app."""
        super().initialize(*args, **kwargs)

    def start(self):
        """Start the app."""
        if len(self.extra_args) > 1:  # pragma: no cover
            warnings.warn("Too many arguments were provided for session list.")
            self.exit(1)
        client = HTTPClient()
        response = client.fetch(
            '{}/api/sessions'.format(self.server_base_url),
            method='GET',
            headers={
                "Authorization": f"token {self.server_token}",
            }
        )
        sessions = json_decode(response.body)
        table = new_session_table(title="Jupyter Sessions")
        for session in sessions:
            add_session_to_table(table, session)
        console = Console()
        console.print(table)


class KernelSessionApp(JupyterKernelsBaseApp):
    """A Session application."""

    description = """
      The JupyterKernels application for Sessions.
    """

    subcommands = {}
    subcommands["create"] = (KernelSessionCreateApp, KernelSessionCreateApp.description.splitlines()[0])
    subcommands["list"] = (KernelSessionListApp, KernelSessionListApp.description.splitlines()[0])

    def start(self):
        try:
            super().start()
            self.log.error(f"One of `{'`, `'.join(KernelSessionApp.subcommands.keys())}` must be specified.")
            self.exit(1)
        except NoStart:
            pass
        self.exit(0)
