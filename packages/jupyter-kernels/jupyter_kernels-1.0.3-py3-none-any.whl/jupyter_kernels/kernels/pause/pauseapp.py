from datalayer.application import NoStart

from ...application_base import JupyterKernelsBaseApp


class KernelPauseApp(JupyterKernelsBaseApp):
    """Kernel Pause application."""

    description = """
      An application to stop a Kernel.
    """

    def start(self):
        try:
            super().start()
            self.log.info(f"Kernel Pause.")
        except NoStart:
            pass
        self.exit(0)
