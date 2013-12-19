
import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot


class UI_EditAccount(QtWidgets.QDialog):
    def __init__(self, *args, label=None, username=None, password=None, **kwargs):
        super(UI_EditAccount, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_account.ui"), self)

        self.oldLabel = label
        if label: self.accountLabel.setText(label)
        if username: self.accountUsername.setText(username)
        if password: self.accountPassword.setText(password)

    def accept(self):
        parent = self.parent()

        label = self.accountLabel.text()

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
            password=self.accountPassword.text()
        )

        parent.config.save()
        parent.addRemoveAccountRows()

        self.close()
