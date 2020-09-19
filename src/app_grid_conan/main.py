"""
Entry module of PiWheater
Sets up cmd arguments, settings and starts the gui
"""

import argparse
import sys
import time
import traceback
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from app_grid_conan import __version__ as AGC_VERSION
from app_grid_conan import config
from app_grid_conan.logger import Logger
from app_grid_conan.ui import main_ui, qt
from app_grid_conan.settings.settings import Settings
from app_grid_conan.grid_file import GridFile

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


def main(settings_path: Path = config.base_path):
    """
    Main function, calling setup, loading components and safe shutdown.
    param settings_path: only used for testing
    """

    # System is first, is_target_system is the most basic check

    handle_cmd_args()

    settings = Settings(ini_folder=settings_path)
    # Set up global Qt Application instance

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    config.qt_app = QtWidgets.QApplication([])
    config.qt_app.setWindowIcon(QtGui.QIcon(str(Path("./icon.png"))))

    gr = GridFile(config.config_path)

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
    config.config_path = Path(args.file).resolve()
    if not config.config_path.exists():
        logger = Logger()
        logger.error("Cannot find config file %s", config.config_path)
        quit(-1)

if __name__ == "__main__":
    main()
