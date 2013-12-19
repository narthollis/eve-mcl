
import os

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from . import resources
from .dialogs import UI_EditAccount, UI_EditConfiguration, UI_ListConfigurations


class AccountRow(QtCore.QObject):

    def __init__(self, *, label, username, password, clients):
        self.clients = clients
        self.label = label
        self.username = username
        self.password = password

        self.qlabel = QtWidgets.QLabel(self.label)
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(clients)

        self.checkbox = QtWidgets.QCheckBox()
        self.button = QtWidgets.QPushButton("Launch")

        self.button.clicked.connect(lambda: self.on_button_clicked())

    def on_button_clicked(self):
        print('on_button_cliecked', self.label, self.combobox.currentText())


class UI_Main(QtWidgets.QMainWindow):
    def __init__(self, *args, config=None, **kwargs):
        self.config = config

        super(UI_Main, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"main_window.ui"), self)

        self.accountGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.accountGridLayout.setColumnStretch(0, 3)
        self.accountGridLayout.setColumnStretch(1, 3)
        self.accountGridLayout.setColumnStretch(2, 0)
        self.accountGridLayout.setColumnStretch(3, 1)

        clients = list(config.clients.keys())
        rows = {}

        row_idx = 0
        for account in config.accounts.values():
            rows[account.label] = AccountRow(clients=clients, **account)

            self.accountGridLayout.addWidget(rows[account.label].qlabel, row_idx, 0)
            self.accountGridLayout.addWidget(rows[account.label].combobox, row_idx, 1)
            self.accountGridLayout.addWidget(rows[account.label].checkbox, row_idx, 2)
            self.accountGridLayout.addWidget(rows[account.label].button, row_idx, 3)

            row_idx += 1

    @QtCore.pyqtSlot()
    def on_actionLaunch_Selected_triggered(self):
        print('on_actionLaunch_Selected_triggered')

    @QtCore.pyqtSlot()
    def on_actionAdd_Account_triggered(self):
        print('on_actionAdd_Account_triggered')
        dialog = UI_EditAccount(parent=self)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionAdd_Config_triggered(self, *args, **kwargs):
        print('on_actionAdd_Config_triggered')
        dialog = UI_EditConfiguration(parent=self)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionManage_Configs_triggered(self, *args, **kwargs):
        print('on_actionManages_Config_triggered')
        dialog = UI_ListConfigurations(parent=self)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()
