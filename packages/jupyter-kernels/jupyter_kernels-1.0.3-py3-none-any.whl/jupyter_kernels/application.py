from pathlib import Path

from datalayer.application import NoStart

from ._version import __version__
from .application_base import JupyterKernelsBaseApp

from .kernels.create.createapp import KernelCreateApp
from .kernels.list.listapp import KernelListApp
from .kernels.pause.pauseapp import KernelPauseApp
from .kernels.sessions.sessionsapp import KernelSessionApp
from .kernels.specs.specsapp import KernelSpecsApp
from .kernels.start.startapp import KernelStartApp
from .kernels.stop.stopapp import KernelStopApp
from .kernels.terminate.terminateapp import KernelTerminateApp


HERE = Path(__file__).parent


class JupyterKernelsApp(JupyterKernelsBaseApp):
    description = """
      The JupyterKernels application.
    """

    subcommands = {
        "create": (KernelCreateApp, KernelCreateApp.description.splitlines()[0]),
        "list": (KernelListApp, KernelListApp.description.splitlines()[0]),
        "pause": (KernelPauseApp, KernelPauseApp.description.splitlines()[0]),
        "session": (KernelSessionApp, KernelSessionApp.description.splitlines()[0]),
        "specs": (KernelSpecsApp, KernelSpecsApp.description.splitlines()[0]),
        "start": (KernelStartApp, KernelStartApp.description.splitlines()[0]),
        "stop": (KernelStopApp, KernelStopApp.description.splitlines()[0]),
        "terminate": (KernelTerminateApp, KernelTerminateApp.description.splitlines()[0]),
    }

    def initialize(self, argv=None):
        """Subclass because the ExtensionApp.initialize() method does not take arguments."""
        super().initialize()

    def start(self):
        super(JupyterKernelsApp, self).start()
        self.log.info("JupyterKernels - Version %s - Cloud %s ", self.version, self.cloud)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterKernelsApp.launch_instance

if __name__ == "__main__":
    main()
