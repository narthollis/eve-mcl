
import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot


from . import resources

class UI_Main(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(UI_Main, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"main_window.ui"), self)

    @pyqtSlot()
    def on_actionLaunch_Selected_triggered(self):
        print('on_actionLaunch_Selected_triggered')

    @pyqtSlot()
    def on_actionAdd_Account_triggered(self, *args, **kwargs):
        print('on_actionAdd_Account_triggered', *args, **kwargs)

    @pyqtSlot()
    def on_actionAdd_Config_triggered(self, *args, **kwargs):
        print('on_actionAdd_Config_triggered', *args, **kwargs)

    @pyqtSlot()
    def on_actionManage_Configs_triggered(self, *args, **kwargs):
        print('on_actionManages_Config_triggered', *args, **kwargs)

    @pyqtSlot()
    def on_actionExit_triggered(self, *args, **kwargs):
        self.close()
