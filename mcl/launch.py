
import os, subprocess, time, logging

from PyQt5.QtCore import QThread, pyqtSignal

import mlp.login


logger = logging.getLogger(__name__)


class Launch(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)


    def __init__(self,  username, password, client_cfg, *args, **kwargs):
        self.username = username
        self.password = password
        self.client_cfg = client_cfg

        super(Launch, self).__init__(*args, **kwargs)

        logger.debug('%s New', repr(self))

    def run(self):
        logger.debug('%s Launching', repr(self))

        exepath = os.path.join(self.client_cfg.path, 'bin', 'exefile.exe')

        cmd = []

        if self.client_cfg.wine_cmd:
            cmd.append(self.client_cfg.wine_cmd)
            if self.client_cfg.wine_flags:
                cmd.append(self.client_cfg.wine_flags)

        cmd.append('"{}"'.format(exepath))

        if self.client_cfg.server == "singularity":
            cmd.append("/server:Singularity")

        logger.debug('%s Login Start', repr(self))
        try:
            launch_token = mlp.login.do_login(self.username, self.password)
        except mlp.login.LoginFailed as e:
            logger.debug('%s Login Error (%s)', repr(self), repr(e))

            self.error.emit(e)
            self.finished.emit(False)

            return
        except Exception as e:
            logger.exception(e)

            return

        logger.debug('%s Login Success', repr(self))

        cmd.append("/ssoToken=" + launch_token)

        cmd.append("/noconsole")

        logger.debug('%s Doing Launch', repr(self))
        a = subprocess.Popen(" ".join(cmd), shell=True)

        logger.debug('%s Launched. waiting 10s to EVE to launch properly', repr(self))
        time.sleep(10)

        logger.debug('%s Done', repr(self))
        self.finished.emit(a)

    def __repr__(self):
        return '<Launch ("{}", config="{}", path="{}", server="{}")>'.format(
            self.username,
            self.client_cfg.label,
            self.client_cfg.path,
            self.client_cfg.server
        )
