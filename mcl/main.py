#!/usr/bin/python33

import sys
import os
import argparse
import logging
import logging.handlers

# http://stackoverflow.com/questions/9144724/unknown-encoding-idna-in-python-requests
import encodings.idna

from appdirs import AppDirs

#from PyQt5.QtWidgets import QApplication
from mcl.gui.qtsingleapplication import QtSingleApplication


from mcl import NAME, VERSION
from mcl.gui.mainwindow import UI_Main
from mcl.config import MCLConfig

logger = logging.getLogger(__name__)

APP_GUID = '69AA5B71-739D-4205-9331-6820672B5577'

def main():
    has_console = True
    try:
        sys.stdout.write("\n")
        sys.stdout.flush()
    except (IOError, AttributeError):
        has_console = False

    if not has_console:
        class dummyStream:
            ''' dummyStream behaves like a stream but does nothing. '''
            def __init__(self): pass
            def write(self,data): pass
            def read(self,data): pass
            def flush(self): pass
            def close(self): pass
        # and now redirect all default streams to this dummyStream:
        sys.stdout = dummyStream()
        sys.stderr = dummyStream()
        sys.stdin = dummyStream()
        sys.__stdout__ = dummyStream()
        sys.__stderr__ = dummyStream()
        sys.__stdin__ = dummyStream()

    #app = QApplication(sys.argv)
    app = QtSingleApplication(APP_GUID, sys.argv)

    if app.isRunning(): sys.exit(0)

    parser = argparse.ArgumentParser()

    log_levels = [logging.getLevelName(i) for i in range(10, 50, 10)]
    log_levels.append('OFF')

    parser.add_argument('--log-level', action='store', choices=log_levels, default='OFF')
    parser.add_argument('--log-path', action='store', default='{}_v{}.log'.format(NAME, VERSION))
    if has_console:
        parser.add_argument('--log-console', action='store_const', const=True, default=False)

    parser.add_argument('--start-in-tray', action='store_const', const=True, default=False)

    args = parser.parse_args()

    mcl_logger = logging.getLogger('mcl')
    mlp_logger = logging.getLogger('mlp')

    if args.log_level != 'OFF':
        formatter = logging.Formatter("{levelname!s:<8} {name!s:<25} {message!s}", style='{')
        handler = logging.handlers.RotatingFileHandler(filename=args.log_path, backupCount=10)
        handler.setFormatter(formatter)
        handler.doRollover()

        mcl_logger.addHandler(handler)
        mlp_logger.addHandler(handler)

        if has_console:
            if args.log_console:
                handler_console = logging.StreamHandler(stream=sys.stderr)
                handler_console.setFormatter(formatter)

                mcl_logger.addHandler(handler_console)
                mlp_logger.addHandler(handler_console)

        mcl_logger.setLevel(args.log_level)
        mlp_logger.setLevel(args.log_level)

    logger.debug('Starting....')
    logger.info('Log Path: %s', args.log_path)
    logger.info('Log Level: %s', args.log_level)

    appdir = os.path.abspath(AppDirs("eve-mlc", 'narthollis', roaming=True).user_data_dir)
    logger.info('Appdir: %s', appdir)

    try:
        os.makedirs(appdir, mode=0o700, exist_ok=True)
    except FileExistsError:
        pass

    try:
        config = MCLConfig.load(appdir + os.path.sep + 'config.json')
        logger.info('Loaded config file.')
    except FileNotFoundError:
        config = MCLConfig(appdir + os.path.sep + 'config.json')
        logger.info('Created new config file.')

    main = UI_Main(config=config)
    main.show()

    if args.start_in_tray:
        main.hide()
        main.trayIconMessageShown = True

    app.setActivationWindow(main)

    app.exec()
