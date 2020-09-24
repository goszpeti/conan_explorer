"""
Entry module of Conan App Launcher
Sets up cmd arguments, config file and starts the gui
"""

import argparse
import traceback
import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from conan_app_launcher import __version__ as AGC_VERSION
from conan_app_launcher import config
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui import main_ui

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


def main(settings_path: Path = config.base_path):
    """
    Main function, setting up Qt application
    """

    handle_cmd_args()

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    config.qt_app = QtWidgets.QApplication([])
    config.qt_app.setWindowIcon(QtGui.QIcon(str(Path("./icon.png"))))

    # main_ui must be held in this context, otherwise the gc will destroy the gui
    app_main_ui = main_ui.MainUi()
    app_main_ui.qt_root_obj.show()

    logger = Logger()
    try:
        config.qt_app.exec_()
    except:  # pylint:disable=bare-except
        trace_back = traceback.format_exc()
        logger.error("Application crashed: \n%s", trace_back)


def handle_cmd_args():
    """
    All CLI related functions.
    """
    parser = argparse.ArgumentParser(
        prog="App Grid for Conan", description="App Grid Conan commandline interface")
    parser.add_argument("-v", "--version", action="version",
                        version=AGC_VERSION)
    parser.add_argument("-f", "--file",
                    help='config json')
    args = parser.parse_args()
    if args.file:
        config.config_path = Path(args.file).resolve()
        if not config.config_path.exists():
            logger = Logger()
            logger.error("Cannot find config file %s", config.config_path)
            sys.exit(-1)

if __name__ == "__main__":
    main()
