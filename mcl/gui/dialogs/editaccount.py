
import os

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot


class UI_EditAccount(QtWidgets.QDialog):
    def __init__(self, *args, label=None, username=None, password=None, protected=False, **kwargs):
        super(UI_EditAccount, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/dialogs/edit_account.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.oldLabel = label
        if label: self.accountLabel.setText(label)
        if username: self.accountUsername.setText(username)
        if password: self.accountPassword.setText(password)
        self.accountProtectLaunch.setChecked(protected)

    def accept(self):
        parent = self.parent()

        label = self.accountLabel.text().strip()

        if self.oldLabel:
            if self.oldLabel in parent.config.accounts.keys():
                parent.config.removeAccount(self.oldLabel)

        if label in parent.config.accounts.keys():
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setText('You can not have 2 accounts with the same label.')
            dialog.setModal(True)
            dialog.show()
            return

        parent.config.addAccount(
            label=label,
            username=self.accountUsername.text(),
            password=self.accountPassword.text(),
            protected=self.accountProtectLaunch.isChecked()
        )

        parent.config.save()
        parent.addRemoveAccountRows()

        self.close()
