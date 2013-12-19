import os

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import pyqtSlot

class ClientRow(QtCore.QObject):

    def __init__(self, *, parent, label, path, server, **kwargs):
        super(ClientRow, self).__init__()

        self.label = label

        self.qlabel_label = QtWidgets.QLabel(label)
        self.qlabel_path = QtWidgets.QLabel(path)
        self.qlabel_server = QtWidgets.QLabel(server)

        self.editButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/wrench.png')), '')
        self.removeButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(':/icons/icons/delete.png')), '')

        self.removeButton.clicked.connect(lambda: self.on_remove_clicked())
        self.editButton.clicked.connect(lambda: self.on_edit_clicked())

    def on_edit_clicked(self):
        pass

    def on_remove_clicked(self):
        pass


class UI_ListClients(QtWidgets.QDialog):

    def __init__(self, *args, clients, **kwargs):
        super(UI_ListClients, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "list_configurations.ui"), self)

        self.clientsGridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.clientsGridLayout.setColumnStretch(0, 3)
        self.clientsGridLayout.setColumnStretch(1, 3)
        self.clientsGridLayout.setColumnStretch(2, 0)
        self.clientsGridLayout.setColumnStretch(3, 1)
        self.clientsGridLayout.setColumnStretch(4, 1)

        self.clientRows = {}
        for client in clients.values():
            row_idx = len(self.clientRows)

            self.clientRows[client.label] = ClientRow(parent=self, **client)


            self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_label, row_idx, 0)
            self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_path, row_idx, 1)
            self.clientsGridLayout.addWidget(self.clientRows[client.label].qlabel_server, row_idx, 2)
            self.clientsGridLayout.addWidget(self.clientRows[client.label].editButton, row_idx, 3)
            self.clientsGridLayout.addWidget(self.clientRows[client.label].removeButton, row_idx, 4)
