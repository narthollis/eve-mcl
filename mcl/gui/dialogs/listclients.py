import os

from PyQt5 import QtWidgets, QtCore, QtGui, uic


from .editclient import UI_EditClient


class ClientRow(QtCore.QObject):

    def __init__(self, *, parent, label, path, server, **kwargs):
        super(ClientRow, self).__init__()

        self.parent = parent

        self.client_config = kwargs
        self.client_config['label'] = label
        self.client_config['path'] = path
        self.client_config['server'] = server

        self.label = label

        self.qlabel_label = QtWidgets.QLabel(label)
        self.qlabel_path = QtWidgets.QLabel(path)
        self.qlabel_server = QtWidgets.QLabel(server)

        self.editButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/wrench.png')), '')
        self.removeButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/delete.png')), '')

        self.removeButton.clicked.connect(lambda: self.on_remove_clicked())
        self.editButton.clicked.connect(lambda: self.on_edit_clicked())

    @QtCore.pyqtSlot()
    def on_edit_clicked(self):
        dialog = UI_EditClient(parent=self.parent, **self.client_config)
        dialog.setModal(True)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_remove_clicked(self):
        self.parent.parent().config.removeClient(self.label)
        self.parent.parent().config.save()

        self.parent.addRemoveClientRows()

    def redraw(self, label, path, server, **kwargs):
        self.client_config = kwargs
        self.client_config['label'] = label
        self.client_config['path'] = path
        self.client_config['server'] = server

        self.label = label

        self.qlabel_label.setText(label)
        self.qlabel_path.setText(path)
        self.qlabel_server.setText(server)

    def remove(self):
        self.parent.clientsGridLayout.removeWidget(self.qlabel_label)
        self.qlabel_label.deleteLater()
        self.parent.clientsGridLayout.removeWidget(self.qlabel_path)
        self.qlabel_path.deleteLater()
        self.parent.clientsGridLayout.removeWidget(self.qlabel_server)
        self.qlabel_server.deleteLater()
        self.parent.clientsGridLayout.removeWidget(self.editButton)
        self.editButton.deleteLater()
        self.parent.clientsGridLayout.removeWidget(self.removeButton)
        self.removeButton.deleteLater()


class UI_ListClients(QtWidgets.QDialog):

    def __init__(self, *args, clients, **kwargs):
        super(UI_ListClients, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/dialogs/list_configurations.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.clientsGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.clientsGridLayout.setColumnStretch(0, 3)
        self.clientsGridLayout.setColumnStretch(1, 3)
        self.clientsGridLayout.setColumnStretch(2, 0)
        self.clientsGridLayout.setColumnStretch(3, 1)
        self.clientsGridLayout.setColumnStretch(4, 1)

        self.clientRows = {}
        self.addRemoveClientRows()

        self.pushButton_Done.clicked.connect(lambda: self.close())

    def addClientRow(self, client):
        row_idx = len(self.clientRows)

        self.clientRows[client.label] = ClientRow(parent=self, **client)

        self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_label, row_idx, 0)
        self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_path, row_idx, 1)
        self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_server, row_idx, 2)
        self.clientsGridLayout.addWidget(self.clientRows[client.label].editButton, row_idx, 3)
        self.clientsGridLayout.addWidget(self.clientRows[client.label].removeButton, row_idx, 4)

    def addRemoveClientRows(self):
        parent = self.parent()

        clientKeys = parent.config.clients.keys()
        for label in clientKeys:
            if label not in self.clientRows.keys():
                self.addClientRow(parent.config.clients[label])

            self.clientRows[label].redraw(**parent.config.clients[label])

        toRemove = []
        for label in self.clientRows.keys():
            if label not in clientKeys:
                toRemove.append(label)

        for label in toRemove:
            self.clientRows[label].remove()
            del self.clientRows[label]
