
import os, subprocess
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMessageBox

import login

class Launch(QThread):

    def __init__(self, username, password, client_cfg, *args, **kwargs):
        self.username = username
        self.password = password
        self.client_cfg = client_cfg

        super(Launch, self).__init__(*args, **kwargs)

    def __del__(self):
        self.wait()

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
            dialog = QMessageBox(parent=self.parent)
            dialog.setWindowTitle('Login Error')
            dialog.setText(str(e))
            dialog.setModal(True)
            dialog.show()
            return

        cmd.append("/ssoToken=" + launch_token)

        cmd.append("/noconsole")

        subprocess.Popen(" ".join(cmd), shell=True)
