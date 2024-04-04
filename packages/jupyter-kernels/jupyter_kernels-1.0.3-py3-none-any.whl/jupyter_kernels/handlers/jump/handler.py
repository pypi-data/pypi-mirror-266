"""Jump handler."""

import os
import getpass
import json
import random
from pathlib import Path

import tornado
from tornado import concurrent

from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

from ..._version import __version__


HOME = Path.home()

JUMP_SERVER = "dev1.datalayer.tech"

LOCAL_USERNAME = getpass.getuser()

# REMOTE_FOLDER = "/home/jovyan"
REMOTE_FOLDER = "/home/jovyan/content/local"

EXECUTOR = concurrent.futures.ThreadPoolExecutor(8)


def mount(pod_name, local_dir, logger):

    port = random.randrange(10000, 40000)

    create_remote_folder_cmd = f"ssh -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no -p 2522 jovyan@{pod_name}.jupyter-kernel.datalayer.svc.cluster.local -oProxyCommand='ssh -W %h:%p -p 2223 -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no datalayer@{JUMP_SERVER}' 'mkdir {REMOTE_FOLDER}; fusermount -u {REMOTE_FOLDER}; ls {REMOTE_FOLDER}'"
    logger.info(f"Creating remote folder: {create_remote_folder_cmd}")
    os.system(create_remote_folder_cmd)

    # Use this option if you want more debug: -o StrictHostKeyChecking=debug no,debug,sshfs_debug,loglevel=debug,default_permissions,idmap=user
    mount_local_to_remote_folder = f"ssh -R {port}:localhost:22 -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no -p 2522 jovyan@{pod_name}.jupyter-kernel.datalayer.svc.cluster.local -oProxyCommand='ssh -W %h:%p -p 2223 -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no datalayer@{JUMP_SERVER}' 'sshfs -p {port} -o StrictHostKeyChecking=no,default_permissions,idmap=user {LOCAL_USERNAME}@localhost:{local_dir} {REMOTE_FOLDER}'"
    logger.info(f"Mounting local to remote folder: {mount_local_to_remote_folder}")
    os.system(mount_local_to_remote_folder)


def unmount(pod_name, logger):

#    unmount_cmd = f"ssh -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no -p 2522 jovyan@{pod_name}.jupyter-kernel.datalayer.svc.cluster.local -oProxyCommand='ssh -W %h:%p -p 2223 -i ~/.ssh/datalayer-jump -oStrictHostKeyChecking=no datalayer@{JUMP_SERVER}' 'fusermount -u {REMOTE_FOLDER}'"
    unmount_cmd = "pkill ssh"
    logger.info(f"Unmount: {unmount_cmd}")
    os.system(unmount_cmd)


# pylint: disable=W0223
class JumpHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for jump."""

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, pod_name):
        """Mount a the local folder."""
        root_dir = self.settings.get(
            "server_root_dir", self.settings.get(
              "root_dir", self.settings.get(
                  "notebook_dir", f"{HOME}/Desktop")))
        root_dir_absolute = Path(root_dir).expanduser().resolve()
        self.log.info(f"Requesting connection via Datalayer Jump to pod {pod_name} for local path {root_dir_absolute}")
        EXECUTOR.submit(mount, pod_name, root_dir_absolute, self.log)
        res = json.dumps({
            "extension": "jupyter_kernels",
            "version": __version__,
        })
        self.finish(res)


    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self, pod_name):
        """Unmount a the local folder."""
        self.log.info(f"Requesting unmount via Datalayer Jump to pod {pod_name}")
        EXECUTOR.submit(unmount, pod_name, self.log)
        res = json.dumps({
            "extension": "jupyter_kernels",
            "version": __version__,
        })
        self.finish(res)
