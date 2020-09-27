"""
Entry module of Conan App Launcher
Sets up cmd arguments, config file and starts the gui
"""
import argparse
import sys
import traceback
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

import conan_app_launcher as this
from conan_app_launcher.conan import ConanWorker
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui import main_ui

try:
    # this is a workaround for windows, so that on the taskbar the
    # correct icon will bes shown (and not the default python icon)
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + this.__version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


def main():
    """
    Start the Qt application
    """
    # init logger first
    logger = Logger()
    handle_cmd_args(logger)

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    this.qt_app = QtWidgets.QApplication([])
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(str(this.base_path / "icon.png")).scaled(
        64, 64, transformMode=Qt.SmoothTransformation), QtGui.QIcon.Normal, QtGui.QIcon.On)
    this.qt_app.setWindowIcon(icon)

    # init conan worker global instance before gui
    this.conan_worker = ConanWorker()
    # main_ui must be held in this context, otherwise the gc will destroy the gui
    app_main_ui = main_ui.MainUi()
    app_main_ui.qt_root_obj.show()

    try:
        this.qt_app.exec_()
    except:  # pylint:disable=bare-except
        trace_back = traceback.format_exc()
        logger.error("Application crashed: \n%s", trace_back)
    if this.conan_worker:  # cancel conan worker tasks on exit
        this.conan_worker.finish_working(2)


def handle_cmd_args(logger: Logger):
    """
    All CLI related functions.
    """
    parser = argparse.ArgumentParser(
        prog="App Grid for Conan", description="App Grid Conan commandline interface")
    parser.add_argument("-v", "--version", action="version",
                        version=this.__version__)
    parser.add_argument("-f", "--file",
                        help='config json')
    args = parser.parse_args()
    if args.file:
        config_path = Path(args.file).resolve()
        if not config_path.exists():
            logger.error("Cannot find config file %s", config_path)
            sys.exit(-1)
        this.config_path = config_path


if __name__ == "__main__":
    main()
