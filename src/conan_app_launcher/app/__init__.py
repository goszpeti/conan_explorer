import os
import platform
import sys

from conan_app_launcher import APP_NAME, SETTINGS_FILE_NAME, __version__, asset_path, user_save_path
from conan_app_launcher.core import ConanApi, ConanWorker
from conan_app_launcher.settings import SETTINGS_INI_TYPE, SettingsInterface, settings_factory
from .logger import Logger

from PySide6 import QtCore, QtGui, QtWidgets


if platform.system() == "Windows":
    # Workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon).
    from ctypes import windll  # Only exists on Windows.
    MY_APP_ID = 'ConanAppLauncher.' + __version__
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)

### Global variables ###

active_settings: SettingsInterface = settings_factory(SETTINGS_INI_TYPE,
                                                      user_save_path / (SETTINGS_FILE_NAME + "." + SETTINGS_INI_TYPE))
conan_api = ConanApi()
conan_worker = ConanWorker(conan_api, active_settings)

def run_application():
    """ Start the Qt application and load the main window """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    from conan_app_launcher.ui.common import activate_theme

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)

    # apply Qt attributes (only possible before QApplication is created)

    # to use icons in qss file
    QtCore.QDir.addSearchPath('icons', os.path.join(asset_path, 'icons'))
    # Passthrough seems to work well for high dpi scaling
    try:
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception:
        Logger().debug("Can't set DPI Rounding")
    qt_app = QtWidgets.QApplication([])
    qt_app.setApplicationName(APP_NAME)
    qt_app.setApplicationDisplayName(APP_NAME)
    from .crash import bug_dialog_exc_hook
    sys.excepthook = bug_dialog_exc_hook  # dialog needs qt_app
    activate_theme(qt_app)

    from conan_app_launcher.ui.main_window import MainWindow
    main_window = MainWindow(qt_app)
    main_window.setWindowIcon(QtGui.QIcon(str(asset_path / "icons" / "icon.ico")))

    conan_api.init_api()
    main_window.show()  # show first, then load appsgrid with progress bar
    main_window.load()
    main_window.installEventFilter(main_window)

    qt_app.exec()

    main_window.save_window_state()
    # cancel conan worker tasks on exit - this can possibly cancel an ongoing install task
    if conan_worker:
        conan_worker.finish_working(10)
