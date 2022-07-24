import os
import platform
import sys

from conan_app_launcher import SETTINGS_FILE_NAME, __version__, asset_path, user_save_path
from conan_app_launcher.core import ConanApi, ConanWorker
from conan_app_launcher.settings import SETTINGS_INI_TYPE, SettingsInterface, settings_factory
from .logger import Logger

from PyQt5 import QtCore, QtGui, QtWidgets

if platform.system() == "Windows":
    # Workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon).
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + __version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)

### Global variables ###

active_settings: SettingsInterface = settings_factory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)
conan_api = ConanApi()
conan_worker = ConanWorker(conan_api, active_settings)


def run_application():
    """ Start the Qt application and load the main window """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    from conan_app_launcher.ui.dialogs import show_bug_dialog_exc_hook
    from conan_app_launcher.ui.common import activate_theme
    sys.excepthook = show_bug_dialog_exc_hook

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)

    # apply Qt attributes (only possible before QApplication is created)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    try:
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor)
    except:
        Logger().debug("Can't set DPI Rounding")
    QtCore.QDir.addSearchPath('icons', os.path.join(asset_path, 'icons'))

    qt_app = QtWidgets.QApplication([])

    activate_theme(qt_app)

    from conan_app_launcher.ui.main_window import MainWindow
    main_window = MainWindow(qt_app)

    app_icon = QtGui.QIcon(str(asset_path / "icons" / "icon.ico"))
    main_window.setWindowIcon(app_icon)

    main_window.show()  # show first, then load appsgrid with progress bar
    main_window.load()
    main_window.installEventFilter(main_window)

    qt_app.exec_()

    main_window.save_window_state()
    # cancel conan worker tasks on exit - this can possibly cancel an ongoing install task
    if conan_worker:
       conan_worker.finish_working(10)
