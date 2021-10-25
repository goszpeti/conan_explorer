"""
Entry module of Conan App Launcher
Sets up cmd arguments, config file and starts the gui
"""
import os
import sys
import traceback
import platform
import tempfile
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

import conan_app_launcher as this
from conan_app_launcher.settings import Settings, LAST_CONFIG_FILE
from conan_app_launcher.base import Logger
from conan_app_launcher.ui.main_window import MainUi
from conan_app_launcher.components import (
    ConanWorker, parse_config_file, write_config_file, ConanInfoCache, TabConfigEntry, AppConfigEntry)

try:
    # this is a workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon)
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + this.__version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


def load_base_components(settings):
    """ Load all default components. """
    this.cache = ConanInfoCache(this.base_path / this.CACHE_FILE_NAME)

    # create or read config file
    config_file_setting = settings.get_string(LAST_CONFIG_FILE)
    default_config_file_path = Path.home() / this.DEFAULT_GRID_CONFIG_FILE_NAME

    # empty config, create it in home path
    if not config_file_setting or not os.path.exists(default_config_file_path):
        config_file_path = default_config_file_path
        Logger().info("Creating empty ui config file " + str(default_config_file_path))
        tab = TabConfigEntry("New Tab")
        tab.add_app_entry(AppConfigEntry({"name": "My App Link"}))
        write_config_file(default_config_file_path, [tab])
        settings.set(LAST_CONFIG_FILE, str(default_config_file_path))

    else:
        config_file_path = Path(config_file_setting)

    if config_file_path.is_file():  # escape error log on first opening
        this.tab_configs = parse_config_file(config_file_path)
        if not this.tab_configs:
            tab = TabConfigEntry("New Tab")
            tab.add_app_entry(AppConfigEntry({"name": "My App Link"}))
            this.tab_configs.append(tab)
            write_config_file(config_file_path, [tab])

    # start Conan Worker
    this.conan_worker = ConanWorker()


def main():
    """
    Start the Qt application and an all main components
    """

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)
    # Redirect stdout and stderr for usage with pythonw as executor -
    # otherwise conan will not work
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.path.join(tempfile.gettempdir(), "stderr-" + this.PROG_NAME), "w")
    # init logger first
    this.base_path = Path(__file__).absolute().parent
    this.asset_path = this.base_path / "assets"
    logger = Logger()

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    if not this.qt_app:
        this.qt_app = QtWidgets.QApplication([])
    icon = QtGui.QIcon(str(this.asset_path / "icons" / "icon.ico"))

    settings_file_path = Path.home() / this.SETTINGS_FILE_NAME
    this.settings = Settings(ini_file=settings_file_path)

    load_base_components(this.settings)

    this.main_window = MainUi()
    # load tabs needs the pyqt signals - constructor has to be finished
    this.main_window.start_app_grid()
    this.main_window.setWindowIcon(icon)
    this.main_window.show()

    try:
        this.qt_app.exec_()
    except:  # pylint:disable=bare-except
        trace_back = traceback.format_exc()
        logger.error(f"Application crashed: \n{trace_back}")
    finally:
        if this.conan_worker:  # cancel conan worker tasks on exit
            this.conan_worker.finish_working()


if __name__ == "__main__":
    main()
