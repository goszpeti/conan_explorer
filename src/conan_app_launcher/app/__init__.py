import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from conan_app_launcher.data.settings import SETTINGS_INI_TYPE, SettingsFactory, SettingsInterface
from conan_app_launcher.data.ui_config import UI_CONFIG_JSON_TYPE
from conan_app_launcher.data.ui_config.json_file import JsonUiConfig
from conan_app_launcher.model.ui_config import ApplicationModel

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

# this allows to use forward declarations to avoid circular imports
from typing import List, Optional

from conan_app_launcher import (
                                SETTINGS_FILE_NAME, PROG_NAME, __version__, asset_path,
                                base_path, user_save_path)
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanApi, ConanInfoCache, ConanWorker
from conan_app_launcher.components.conan_worker import ConanWorkerElement
from conan_app_launcher.data.settings.ini_file import (LAST_CONFIG_FILE,
                                                       IniSettings)
from conan_app_launcher.ui.bug_report import custom_exception_hook
from conan_app_launcher.ui.main_window import MainWindow

try:
    # this is a workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon)
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + __version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

### Global variables ###

main_window: Optional[MainWindow] = None  # TODO can this be removed?
conan_api = ConanApi()
conan_worker = ConanWorker(conan_api)
active_settings = SettingsFactory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)
model = ApplicationModel(active_settings)

def main():
    """
    Start the Qt application and an all main components
    """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    sys.excepthook = custom_exception_hook

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)

    # Redirect stdout and stderr for usage with pythonw as executor -
    # otherwise conan will not work
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.path.join(tempfile.gettempdir(), "stderr-" + PROG_NAME), "w")

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    qt_app = QtWidgets.QApplication([])

    app_icon = QtGui.QIcon(str(asset_path / "icons" / "icon.ico"))

    from conan_app_launcher.ui.main_window import MainWindow
    main_window = MainWindow()
    # load tabs needs the pyqt signals - constructor has to be finished
    main_window.start_app_grid()
    main_window.setWindowIcon(app_icon)
    main_window.show()

    qt_app.exec_()
