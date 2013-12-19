#!/usr/bin/python33

import sys, os

from appdirs import AppDirs

from PyQt5.QtWidgets import QApplication

from .gui.mainwindow import UI_Main

from .config import MCLConfig

def main():
    appdir = os.path.abspath(AppDirs("eve-mlc", 'narthollis', roaming=True).user_data_dir)

    try:
        os.makedirs(appdir, mode=0o700, exist_ok=True)
    except FileExistsError:
        pass

    try:
        config = MCLConfig.load(appdir + os.path.sep + 'config.json')
    except FileNotFoundError:
        config = MCLConfig(appdir + os.path.sep + 'config.json')

    app = QApplication(sys.argv)

    main = UI_Main(config=config)
    main.show()

    app.exec()
