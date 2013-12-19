import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

class UI_EditClient(QtWidgets.QDialog):

    def __init__(self, *args, label=None, path=None, server=None, wine_cmd=None, wine_flags=None, **kwargs):
        super(UI_EditClient, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_configuration.ui"), self)

        self.oldLabel = label
        if label: self.configName.setText(label)
        if path: self.configPath.setText(path)
        if server: self.configServer.setCurrentIndex(self.configServer.findText(server))
        if wine_cmd: self.configWineCMD.setText(wine_cmd)
        if wine_flags: self.configWineFlags.setText(wine_flags)

        self.configPathBrowse.clicked.connect(self.on_configPathBrowsed_clicked)

    def on_configPathBrowsed_clicked(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Find EVE Directory',
            '.',
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        self.configPath.setText(dir)

    def accept(self):
        parent = self.parent()

        label = self.configName.text()

        if self.oldLabel:
            if self.oldLabel in parent.config.clients.keys():
                parent.config.removeClient(self.oldLabel)

        if label in parent.config.clients.keys():
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setText('You can not have 2 clients with the same label.')
            dialog.setModal(True)
            dialog.show()
            return

        parent.config.addClient(
            label=label,
            path=self.configPath.text(),
            server=self.configServer.currentText(),
            wine_cmd=self.configWineCMD.text(),
            wine_flags=self.configWineFlags.text()
        )

        parent.config.save()
        parent.addRemoveAccountRows()

        self.close()

