
from PyQt5 import QtWidgets, QtCore, uic


from mcl import VERSION


class UI_About(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(UI_About, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/dialogs/about.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.versionLabel.setText(VERSION)

        self.pushButton_Close.clicked.connect(lambda: self.close())
