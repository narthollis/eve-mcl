
import os

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from . import resources
from .dialogs import UI_EditAccount, UI_EditClient, UI_ListClients


class AccountRow(QtCore.QObject):

    def __init__(self, *, label, username, password, clients, parent):
        super(AccountRow, self).__init__()

        self.parent = parent
        self.label = label
        self.username = username
        self.password = password

        self.qlabel = QtWidgets.QLabel(self.label)
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(clients)

        self.checkbox = QtWidgets.QCheckBox()
        self.launchButton = QtWidgets.QPushButton("Launch")
        self.editButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/wrench.png')), '')
        self.removeButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/delete.png')), '')

        self.launchButton.clicked.connect(lambda: self.on_button_clicked())
        self.removeButton.clicked.connect(lambda: self.on_remove_clicked())
        self.editButton.clicked.connect(lambda: self.on_edit_clicked())

    def remove(self):
        self.parent.accountGridLayout.removeWidget(self.qlabel)
        self.qlabel.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.combobox)
        self.combobox.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.checkbox)
        self.checkbox.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.launchButton)
        self.launchButton.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.removeButton)
        self.removeButton.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.editButton)
        self.editButton.deleteLater()

    def redraw(self, *, label, username, password):
        self.label = label
        self.username = username
        self.password = password

        self.qlabel.clear()
        self.qlabel.setText(self.label)

    def redraw_comboBox(self, clients):
        old_choice = self.combobox.currentText()
        self.combobox.clear()
        self.combobox.addItems(clients)
        try:
            self.combobox.setCurrentIndex(self.combobox.findText(old_choice))
        except Exception:
            pass

    def on_button_clicked(self):
        print('on_button_clicked', self.label)

    def on_edit_clicked(self):
        dialog = UI_EditAccount(parent=self.parent, label=self.label, username=self.username, password=self.password)
        dialog.setModal(True)
        dialog.show()

    def on_remove_clicked(self):
        self.parent.config.removeAccount(self.label)
        self.parent.config.save()

        self.parent.addRemoveAccountRows()


class UI_Main(QtWidgets.QMainWindow):
    def __init__(self, *args, config=None, **kwargs):
        self.config = config

        super(UI_Main, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"main_window.ui"), self)

        self.accountGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.accountGridLayout.setColumnStretch(0, 0)
        self.accountGridLayout.setColumnStretch(1, 3)
        self.accountGridLayout.setColumnStretch(2, 3)
        self.accountGridLayout.setColumnStretch(3, 1)
        self.accountGridLayout.setColumnStretch(4, 1)
        self.accountGridLayout.setColumnStretch(5, 1)

        self.flatClientList = list(self.config.clients.keys())
        self.accountRows = {}

        self.addRemoveAccountRows()
        #for account in self.config.accounts.values():
        #    self.addAccountRow(account)

    def addAccountRow(self, account):
        row_idx = len(self.accountRows)

        self.accountRows[account.label] = AccountRow(clients=self.flatClientList, parent=self, **account)

        self.accountGridLayout.addWidget(self.accountRows[account.label].checkbox, row_idx, 0)
        self.accountGridLayout.addWidget(self.accountRows[account.label].qlabel, row_idx, 1)
        self.accountGridLayout.addWidget(self.accountRows[account.label].combobox, row_idx, 2)
        self.accountGridLayout.addWidget(self.accountRows[account.label].launchButton, row_idx, 3)
        self.accountGridLayout.addWidget(self.accountRows[account.label].editButton, row_idx, 4)
        self.accountGridLayout.addWidget(self.accountRows[account.label].removeButton, row_idx, 5)

    def addRemoveAccountRows(self):
        self.flatClientList = list(self.config.clients.keys())

        configKeys = self.config.accounts.keys()
        for label in configKeys:
            if label not in self.accountRows:
                self.addAccountRow(self.config.accounts[label])

            self.accountRows[label].redraw(**self.config.accounts[label])
            self.accountRows[label].redraw_comboBox(self.flatClientList)

        toRemove = []
        for label in self.accountRows.keys():
            if label not in configKeys:
                toRemove.append(label)

        for label in toRemove:
            self.accountRows[label].remove()
            del self.accountRows[label]

    @QtCore.pyqtSlot()
    def on_actionLaunch_Selected_triggered(self):
        print('on_actionLaunch_Selected_triggered')

    @QtCore.pyqtSlot()
    def on_actionAdd_Account_triggered(self):
        if len(self.config.clients) == 0:
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setText('Please add a Client first.')
        else:
            dialog = UI_EditAccount(parent=self)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionAdd_Config_triggered(self, *args, **kwargs):
        dialog = UI_EditClient(parent=self)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionManage_Configs_triggered(self, *args, **kwargs):
        print('on_actionManages_Config_triggered')
        dialog = UI_ListClients(parent=self, clients=self.config.clients)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()
