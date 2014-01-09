
import os, subprocess, time
from PyQt5.QtCore import QThread, pyqtSignal


import mlp.login

class Launch(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)


    def __init__(self,  username, password, client_cfg, *args, **kwargs):
        self.username = username
        self.password = password
        self.client_cfg = client_cfg

        super(Launch, self).__init__(*args, **kwargs)

    def run(self):
        exepath = os.path.join(self.client_cfg.path, 'bin', 'exefile.exe')

        cmd = []

        if self.client_cfg.wine_cmd:
            cmd.append(self.client_cfg.wine_cmd)
            if self.client_cfg.wine_flags:
                cmd.append(self.client_cfg.wine_flags)

        cmd.append('"{}"'.format(exepath))

        if self.client_cfg.server == "singularity":
            cmd.append("/server:Singularity")

        try:
            launch_token = login.do_login(self.username, self.password)
        except login.LoginFailed as e:
            self.error.emit(e)
            self.finished.emit(False)
            return

        cmd.append("/ssoToken=" + launch_token)

        cmd.append("/noconsole")

        a = subprocess.Popen(" ".join(cmd), shell=True)

        time.sleep(10)

        self.finished.emit(a)
