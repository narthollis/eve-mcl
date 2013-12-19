
import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSlot


class UI_EditConfiguration(QtWidgets.QDialog):

    def __init__(self, *args, name=None, path=None, server=None, wine_cmd=None, wine_flags=None, **kwargs):
        super(UI_EditConfiguration, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"edit_configuration.ui"), self)


class UI_ListConfigurations(QtWidgets.QDialog):

    def __init__(self, *args, configs=None, **kwargs):
        super(UI_ListConfigurations, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"list_configurations.ui"), self)


class UI_EditAccount(QtWidgets.QDialog):
    def __init__(self, *args, name=None, username=None, password=None, **kwargs):
        super(UI_EditAccount, self).__init__(*args, **kwargs)

        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"edit_account.ui"), self)

