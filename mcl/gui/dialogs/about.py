from PyQt5 import QtWidgets, QtCore, QtGui, uic

class UI_About(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(UI_About, self).__init__(*args, **kwargs)

        ui = QtCore.QFile(":/uis/dialogs/about.ui")
        ui.open(QtCore.QIODevice.ReadOnly)
        uic.loadUi(ui, self)

        self.pushButton_Close.clicked.connect(lambda: self.close())
