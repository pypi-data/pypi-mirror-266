from datalayer.application import NoStart

from ...application_base import JupyterKernelsBaseApp


class KernelTerminateApp(JupyterKernelsBaseApp):
    """Kernel Terminate application."""

    description = """
      An application to terminate a Kernel.
    """

    def start(self):
        try:
            super().start()
            self.log.info(f"Kernel Stop.")
        except NoStart:
            pass
        self.exit(0)
