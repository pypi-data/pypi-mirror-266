from datalayer.application import NoStart

from ...application_base import JupyterKernelsBaseApp


class KernelStopApp(JupyterKernelsBaseApp):
    """Kernel Stop application."""

    description = """
      An application to stop a Kernel.
    """

    def start(self):
        try:
            super().start()
            self.log.info(f"Kernel Stop.")
        except NoStart:
            pass
        self.exit(0)
