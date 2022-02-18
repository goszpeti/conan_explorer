import os
import platform
import sys
import tempfile

from conan_app_launcher import (PKG_NAME, SETTINGS_FILE_NAME, __version__,
                                asset_path, user_save_path)
from conan_app_launcher.core import ConanApi, ConanWorker
from conan_app_launcher.settings import (SETTINGS_INI_TYPE, SettingsInterface,
                                         settings_factory)

from PyQt5 import QtCore, QtGui, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

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


def run_application(conan_search=False):
    """ Start the Qt application and load the main window """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    from conan_app_launcher.ui.dialogs.bug_dialog import show_bug_dialog_exc_hook
    from conan_app_launcher.ui.common.theming import activate_theme
    sys.excepthook = show_bug_dialog_exc_hook

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)

    # Redirect stdout and stderr for usage with pythonw as executor -
    # otherwise conan will not work
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.path.join(tempfile.gettempdir(), "stderr-" + PKG_NAME), "w")

    # apply Qt attributes (only possible before QApplication is created)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QtCore.QDir.addSearchPath('icons', os.path.join(asset_path, 'icons'))

    qt_app = QtWidgets.QApplication([])
    activate_theme(qt_app)

    if conan_search:
        from conan_app_launcher.ui.dialogs.conan_search import ConanSearchDialog
        main_window = ConanSearchDialog()
    else:
        from conan_app_launcher.ui.main_window import MainWindow
        main_window = MainWindow(qt_app)

    app_icon = QtGui.QIcon(str(asset_path / "icons" / "icon.ico"))
    main_window.setWindowIcon(app_icon)
    main_window.show()  # show first, then load appsgrid with progress bar
    # load tabs needs the pyqt signals - constructor has to be finished
    main_window.load()

    qt_app.exec_()
    if conan_worker:  # cancel conan worker tasks on exit - this can possibly cancel an ongoing install task
        conan_worker.finish_working(10)
