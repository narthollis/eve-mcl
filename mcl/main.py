#!/usr/bin/python33

import sys, os, argparse, logging, logging.handlers

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
    #app = QApplication(sys.argv)
    app = QtSingleApplication(APP_GUID, sys.argv)

    if app.isRunning(): sys.exit(0)


    parser = argparse.ArgumentParser()

    log_levels = [logging.getLevelName(i) for i in range(10, 50, 10)]
    log_levels.append('OFF')

    parser.add_argument('--log-level', action='store', choices=log_levels, default='OFF')
    parser.add_argument('--log-path', action='store', default='{}_v{}.log'.format(NAME, VERSION))

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

    app.setActivationWindow(main)

    app.exec()
