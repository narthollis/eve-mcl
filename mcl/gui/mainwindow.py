
import os, os.path, logging

from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt

from mcl.gui import resources
from mcl.gui.dialogs import UI_EditAccount, UI_ListClients, UI_About

from mcl.launch import Launch


logger = logging.getLogger(__name__)

class AccountRow(QtCore.QObject):

    def __init__(self, *, label, username, password, clients, parent):
        super(AccountRow, self).__init__()

        self.parent = parent
        self.label = label
        self.username = username
        self.password = password

        logger.debug('%s New', repr(self))

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

        self.launchAction = QtWidgets.QAction('Launch ' + self.label, self.parent)
        self.setLaunchActionIcon()
        #self.launchAction.triggered.connect(lambda: self.on_launchButton_clicked())
        self.launchAction.triggered.connect(lambda: self.labelButton.toggle())

        self.parent.trayIconMenu.addAction(self.launchAction)

        if self.label in self.parent.config.states.keys():
            state = self.parent.config.states[self.label]

            self.labelButton.setChecked(state.selected)

            if state.clientLabel is not None:
                try:
                    self.combobox.setCurrentIndex(self.combobox.findText(state.clientLabel))
                except Exception as e:
                    logger.error(e)

    def setLaunchActionIcon(self):
        if self.labelButton.isChecked():
            self.launchAction.setIcon(QtGui.QIcon(":/icons/icons/tick.png"))
        else:
            self.launchAction.setIcon(QtGui.QIcon(":/icons/icons/cross.png"))

    def remove(self):
        logger.debug('%s Remove', repr(self))

        self.parent.trayIconMenu.removeAction(self.launchAction)
        self.launchAction.deleteLater()

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
        logger.debug('%s Redraw', repr(self))

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
        logger.debug('%s Store State', repr(self))

        self.parent.config.setState(
            label=self.label,
            selected=self.labelButton.isChecked(),
            clientLabel=self.combobox.currentText()
        )
        self.parent.config.save()

    def launch(self):
        logger.info('%s Launch', repr(self))

        if not self.launchButton.isEnabled():
            logger.debug('%s Launch Aborted (Launch Button Disabled)', repr(self))
            return

        client_label = self.combobox.currentText()
        if client_label not in self.parent.config.clients.keys():
            dialog = QtWidgets.QMessageBox(parent=self.parent)
            dialog.setWindowTitle('No Client Selected')
            dialog.setText('You must select a client to use.')
            dialog.setModal(True)
            dialog.show()

            logger.debug('%s Launch Aborted (Client Missing)', repr(self))
            return

        exepath = os.path.join(self.parent.config.clients[client_label].path, 'bin', 'exefile.exe')
        if not os.path.exists(exepath):
            dialog = QtWidgets.QMessageBox(parent=self.parent)
            dialog.setWindowTitle('Client Not found')
            dialog.setText('Please ensure that the selected EVE Client is properly configuerd.')
            dialog.setModal(True)
            dialog.show()

            logger.debug('%s Launch Aborted (exefile.exe Missing)', repr(self))
            return

        self.launchButton.setDisabled(True)
        self.launchButton.setFlat(True)
        self.launchButton.setText("Launching....")

        logger.debug('%s Pre-Launch Tests Passed', repr(self))

        self._launch = Launch(self.username, self.password, self.parent.config.clients[client_label])

        self._launch.error.connect(lambda e: self.on_login_error(e))
        self._launch.finished.connect(lambda a=None: self.on_launch_finished(a))

        self._launch.start()

        logger.debug('%s Launch Thread Started', repr(self))

        return

    def on_launch_finished(self, a=None):
        logger.debug('%s On Launch Finished (%s)', repr(self), repr(a))

        if a is False:
            self.launchButton.setText('Error')
        else:
            self.launchButton.setDisabled(False)
            self.launchButton.setFlat(False)
            self.launchButton.setText("Launch")

    def on_login_error(self, e):
        logger.debug('%s On Login Error (%s)', repr(self), repr(e))

        dialog = QtWidgets.QMessageBox(parent=self.parent)
        dialog.setWindowTitle('Login Error')
        dialog.setText(str(e))
        dialog.setModal(True)
        dialog.show()
        return

    def on_labelButton_toggle(self):
        logger.debug('%s On Label Button Toggle', repr(self))

        self.setLaunchActionIcon()
        self.storeState()

    def on_combobox_change(self, *args, **kwargs):
        logger.debug('%s On Combobox Change', repr(self))

        self.storeState()

    def on_launchButton_clicked(self):
        logger.debug('%s On Launch Button Clicked', repr(self))

        self.launch()

    def on_edit_clicked(self):
        logger.debug('%s On Edit Clicked', repr(self))

        dialog = UI_EditAccount(parent=self.parent, label=self.label, username=self.username, password=self.password)
        dialog.setModal(True)
        dialog.show()

    def on_remove_clicked(self):
        logger.debug('%s On Remove Clicked', repr(self))

        self.parent.config.removeAccount(self.label)
        self.parent.config.save()

        self.parent.addRemoveAccountRows()

    def __repr__(self):
        return '<AccountRow("{}")>'.format(self.label)


class UI_Main(QtWidgets.QMainWindow):
    def __init__(self, *args, config=None, **kwargs):
        self.config = config

        super(UI_Main, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/main_window.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/MCL.png')))

        self.addSystemTrayIcon()

        self.accountGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.accountGridLayout.setColumnStretch(0, 3)
        self.accountGridLayout.setColumnStretch(1, 3)
        self.accountGridLayout.setColumnStretch(2, 1)
        self.accountGridLayout.setColumnStretch(3, 1)
        self.accountGridLayout.setColumnStretch(4, 1)

        self.flatClientList = list(self.config.clients.keys())
        self.accountRows = {}

        self.addRemoveAccountRows()

    def addSystemTrayIcon(self):
        self.trayIconMenu = QtWidgets.QMenu(parent=self)
        self.trayIconMenu.addAction(self.actionExit)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.actionLaunch_Selected)
        self.trayIconMenu.addSeparator()

        self.trayIcon = QtWidgets.QSystemTrayIcon(parent=self)
        self.trayIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/MCL.png')))
        self.trayIcon.setContextMenu(self.trayIconMenu)

        self.trayIcon.activated.connect(self.on_trayIcon_activated)

        self.trayIconMessageShown = False

        self.trayIcon.show()

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

    def closeEvent(self, event, *args, **kwargs):
        if self.trayIcon.isVisible():
            if not self.trayIconMessageShown:
                QtWidgets.QMessageBox.information(self,
                                                  "Systray",
                                                  "The program will keep running in the " +
                                                  "system tray. To terminate the program, " +
                                                  "choose <b>Exit</b> in the context menu " +
                                                  "of the system tray entry, or in the toolbar.")
                self.trayIconMessageShown = True

            self.hide()
            event.ignore()

    @QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
    def on_trayIcon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger or \
           reason == QtWidgets.QSystemTrayIcon.DoubleClick:

            self.show()

    @QtCore.pyqtSlot()
    def on_actionLaunch_Selected_triggered(self):
        logger.debug('<MainWindow> on_actionLaunch_Selected_triggered')
        for row in self.accountRows.values():
            if row.labelButton.isChecked():
                row.launch()

    @QtCore.pyqtSlot()
    def on_actionAdd_Account_triggered(self):
        logger.debug('<MainWindow> on_actionAdd_Account_triggered')
        if len(self.config.clients) == 0:
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setText('Please add a Client first.')
        else:
            dialog = UI_EditAccount(parent=self)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionManage_Configs_triggered(self, *args, **kwargs):
        logger.debug('<MainWindow> on_actionManage_Configs_triggered')
        dialog = UI_ListClients(parent=self, clients=self.config.clients)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        logger.debug('<MainWindow> on_actionExit_triggered')

        self.trayIcon.hide()
        self.close()

    @QtCore.pyqtSlot()
    def on_actionAbout_triggered(self):
        logger.debug('<MainWindow> on_actionAbout_triggered')
        dialog = UI_About(parent=self)
        dialog.setModal(True)
        dialog.show()
