import os

from PyQt5 import QtWidgets, QtCore, uic

class UI_EditClient(QtWidgets.QDialog):

    def __findEvePath(self):
        try:
            import win32com.client

            objShell = win32com.client.Dispatch("WScript.Shell")
            allUserProgramsMenu = objShell.SpecialFolders("AllUsersPrograms")
            userMenu = objShell.SpecialFolders("StartMenu")

            allUsersFullPath = os.path.join(allUserProgramsMenu, 'EVE', 'Play EVE.lnk')
            userMenuFullPath = os.path.join(userMenu, 'Programs', 'EVE', 'Play EVE.lnk')

            lnkPath = None
            if os.path.exists(allUsersFullPath):
                lnkPath = allUsersFullPath
            elif os.path.exists(userMenuFullPath):
                lnkPath = userMenuFullPath

            if lnkPath:
                shortcut = objShell.CreateShortCut(lnkPath)
                return shortcut.TargetPath

        except ImportError:
            pass

        return '.'

    def __init__(self, *args, label=None, path=None, server=None, wine_cmd=None, wine_flags=None, **kwargs):
        super(UI_EditClient, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/dialogs/edit_configuration.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.oldLabel = label
        if label: self.configName.setText(label)
        if path: self.configPath.setText(path)
        if server: self.configServer.setCurrentIndex(self.configServer.findText(server))
        if wine_cmd: self.configWineCMD.setText(wine_cmd)
        if wine_flags: self.configWineFlags.setText(wine_flags)

        self.configPathBrowse.clicked.connect(self.on_configPathBrowsed_clicked)

    def on_configPathBrowsed_clicked(self):
        path = '.'
        if os.path.exists(os.path.join(self.configPath.text(), 'bin', 'exefile.exe')):
            path = self.configPath.text()
        else:
            path = self.__findEvePath()

        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            'Find EVE Directory',
            path,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        self.configPath.setText(dir)

    def accept(self):
        parent = self.parent()

        realParent = parent

        try:
            parent.config
        except AttributeError:
            parent = parent.parent()

        label = self.configName.text()

        if self.oldLabel:
            if self.oldLabel in parent.config.clients.keys():
                parent.config.removeClient(self.oldLabel)

        if label in parent.config.clients.keys():
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setWindowTitle('Client Label Conflict')
            dialog.setText('You can not have 2 clients with the same label.')
            dialog.setModal(True)
            dialog.show()
            return

        if not os.path.exists(os.path.join(self.configPath.text(), 'bin', 'exefile.exe')):
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setWindowTitle('bin/exefile.exe not found')
            dialog.setText('bin/exefile.exe not found.\n\nPlease ensure you have selected an EVE Online install directory.')
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

        if realParent != parent:
            realParent.addRemoveClientRows()

        self.close()

