import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from conan_app_launcher import (PROG_NAME, SETTINGS_FILE_NAME, __version__,
                                asset_path, user_save_path)
from conan_app_launcher.components import ConanApi, ConanWorker

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainWindow

from conan_app_launcher.settings import (LAST_CONFIG_FILE, SETTINGS_INI_TYPE,
                                         SettingsFactory, SettingsInterface)
from PyQt5 import QtCore, QtGui, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

try:
    # this is a workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon)
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + __version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

### Global variables ###

main_window: Optional["MainWindow"] = None  # TODO can this be removed?
conan_api = ConanApi()
conan_worker = ConanWorker(conan_api)
active_settings: SettingsInterface = SettingsFactory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)


def main():
    """
    Start the Qt application and an all main components
    """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    from conan_app_launcher.ui.common.bug_dialog import \
        show_bug_dialog_exc_hook
    sys.excepthook = show_bug_dialog_exc_hook

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
    main_window.load(active_settings.get(LAST_CONFIG_FILE))
    main_window.setWindowIcon(app_icon)
    main_window.show()

    qt_app.exec_()
    if conan_worker:  # cancel conan worker tasks on exit
        conan_worker.finish_working()
