
import os, os.path

from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt

from mcl.gui import resources
from mcl.gui.dialogs import UI_EditAccount, UI_ListClients, UI_About

from mcl.launch import Launch


class AccountRow(QtCore.QObject):

    def __init__(self, *, label, username, password, clients, parent):
        super(AccountRow, self).__init__()

        self.parent = parent
        self.label = label
        self.username = username
        self.password = password

        self.labelButton = QtWidgets.QPushButton(self.label)

        labelIcon = QtGui.QIcon()
        labelIcon.addPixmap(QtGui.QPixmap(":/icons/icons/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        labelIcon.addPixmap(QtGui.QPixmap(":/icons/icons/cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.labelButton.setIcon(labelIcon)
        self.labelButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.labelButton.setCheckable(True)
        self.labelButton.setStyleSheet("text-align: left")

        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(clients)

        self.launchButton = QtWidgets.QPushButton("Launch")
        self.editButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/wrench.png')), '')
        self.removeButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/delete.png')), '')

        self.launchButton.clicked.connect(lambda: self.on_launchButton_clicked())
        self.removeButton.clicked.connect(lambda: self.on_remove_clicked())
        self.editButton.clicked.connect(lambda: self.on_edit_clicked())

        self.labelButton.toggled.connect(lambda: self.on_labelButton_toggle())
        self.combobox.currentIndexChanged.connect(lambda: self.on_combobox_change())

        if self.label in self.parent.config.states.keys():
            state = self.parent.config.states[self.label]

            self.labelButton.setChecked(state.selected)

            if state.clientLabel is not None:
                try:
                    self.combobox.setCurrentIndex(self.combobox.findText(state.clientLabel))
                except Exception as e:
                    print(e)

    def remove(self):
        self.parent.accountGridLayout.removeWidget(self.labelButton)
        self.labelButton.deleteLater()

        self.parent.accountGridLayout.removeWidget(self.combobox)
        self.combobox.deleteLater()

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

        self.launchButton.setDisabled(False)
        self.launchButton.setFlat(False)
        self.launchButton.setText("Launch")

        self.labelButton.setText(self.label)

    def redraw_comboBox(self, clients):
        old_choice = self.combobox.currentText()
        self.combobox.clear()
        self.combobox.addItems(clients)
        try:
            self.combobox.setCurrentIndex(self.combobox.findText(old_choice))
        except Exception:
            pass

    def storeState(self):
        self.parent.config.setState(
            label=self.label,
            selected=self.labelButton.isChecked(),
            clientLabel=self.combobox.currentText()
        )
        self.parent.config.save()

    def launch(self):
        client_label = self.combobox.currentText()
        if client_label not in self.parent.config.clients.keys():
            dialog = QtWidgets.QMessageBox(parent=self.parent)
            dialog.setWindowTitle('No Client Selected')
            dialog.setText('You must select a client to use.')
            dialog.setModal(True)
            dialog.show()
            return

        exepath = os.path.join(self.parent.config.clients[client_label].path, 'bin', 'exefile.exe')
        if not os.path.exists(exepath):
            dialog = QtWidgets.QMessageBox(parent=self.parent)
            dialog.setWindowTitle('Client Not found')
            dialog.setText('Please ensure that the selected EVE Client is properly configuerd.')
            dialog.setModal(True)
            dialog.show()
            return

        self.launchButton.setDisabled(True)
        self.launchButton.setFlat(True)
        self.launchButton.setText("Launching....")


        self._launch = Launch(self.username, self.password, self.parent.config.clients[client_label])

        self._launch.error.connect(lambda e: self.on_login_error(e))
        self._launch.finished.connect(lambda a=None: self.on_launch_finished(a))

        self._launch.start()

        return

    def on_launch_finished(self, a=None):
        if a is False:
            self.launchButton.setText('Error')
        else:
            self.launchButton.setDisabled(False)
            self.launchButton.setFlat(False)
            self.launchButton.setText("Launch")

    def on_login_error(self, e):
        dialog = QtWidgets.QMessageBox(parent=self.parent)
        dialog.setWindowTitle('Login Error')
        dialog.setText(str(e))
        dialog.setModal(True)
        dialog.show()
        return

    def on_labelButton_toggle(self):
        self.storeState()

    def on_combobox_change(self, *args, **kwargs):
        self.storeState()

    def on_launchButton_clicked(self):
        self.launch()

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

        ui = QtCore.QFile(":/uis/main_window.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.accountGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.accountGridLayout.setColumnStretch(0, 3)
        self.accountGridLayout.setColumnStretch(1, 3)
        self.accountGridLayout.setColumnStretch(2, 1)
        self.accountGridLayout.setColumnStretch(3, 1)
        self.accountGridLayout.setColumnStretch(4, 1)

        self.flatClientList = list(self.config.clients.keys())
        self.accountRows = {}

        self.addRemoveAccountRows()
        #for account in self.config.accounts.values():
        #    self.addAccountRow(account)

    def addAccountRow(self, account):
        row_idx = len(self.accountRows)

        self.accountRows[account.label] = AccountRow(clients=self.flatClientList, parent=self, **account)

        self.accountGridLayout.addWidget(self.accountRows[account.label].labelButton, row_idx, 0)
        self.accountGridLayout.addWidget(self.accountRows[account.label].combobox, row_idx, 1)
        self.accountGridLayout.addWidget(self.accountRows[account.label].launchButton, row_idx, 2)
        self.accountGridLayout.addWidget(self.accountRows[account.label].editButton, row_idx, 3)
        self.accountGridLayout.addWidget(self.accountRows[account.label].removeButton, row_idx, 4)

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
        for row in self.accountRows.values():
            if row.labelButton.isChecked():
                row.launch()

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
    def on_actionManage_Configs_triggered(self, *args, **kwargs):
        dialog = UI_ListClients(parent=self, clients=self.config.clients)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()

    @QtCore.pyqtSlot()
    def on_actionAbout_triggered(self):
        dialog = UI_About(parent=self)
        dialog.setModal(True)
        dialog.show()
