#!/usr/bin/python

import sys

from PyQt5.QtWidgets import QApplication

from .gui.mainwindow import UI_Main


def main():
    app = QApplication(sys.argv)

    main = UI_Main()
    main.show()

    app.exec()
