import os
import platform
import sys
import tempfile
from typing import TYPE_CHECKING

from conan_app_launcher import PKG_NAME, SETTINGS_FILE_NAME, __version__, asset_path, base_path, user_save_path
from conan_app_launcher.core import ConanApi, ConanWorker
from conan_app_launcher.settings import GUI_STYLE, GUI_STYLE_DARK, SETTINGS_INI_TYPE, settings_factory, SettingsInterface

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

try:
    # Workaround for Windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon).
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + __version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

### Global variables ###
active_settings: SettingsInterface = settings_factory(SETTINGS_INI_TYPE, user_save_path / SETTINGS_FILE_NAME)
conan_api = ConanApi()
conan_worker = ConanWorker(conan_api, active_settings)


def run_application(conan_search=False):
    """ Start the Qt application and an all main base """
    # Overwrite the excepthook with our own - this will provide a method to report bugs for the user
    from conan_app_launcher.ui.common.bug_dialog import show_bug_dialog_exc_hook
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

    # start Qt app and ui
    qt_app = QtWidgets.QApplication([])

    app_icon = QtGui.QIcon(str(asset_path / "icons" / "icon.ico"))

    if conan_search:
        from conan_app_launcher.ui.modules.conan_search import ConanSearchDialog
        main_window = ConanSearchDialog()
    else:
        from conan_app_launcher.ui.main_window import MainWindow
        main_window = MainWindow(qt_app)

    style_file = "light_style.qss"
    if active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
        style_file = "dark_style.qss"

    with open(base_path / "ui" / style_file) as fd:
        style_sheet = fd.read()
        qt_app.setStyleSheet(style_sheet)

    main_window.setWindowIcon(app_icon)
    main_window.show()  # show first, then load appsgrid with progress bar
    # load tabs needs the pyqt signals - constructor has to be finished
    main_window.load()

    qt_app.exec_()
    if conan_worker:  # cancel conan worker tasks on exit - this can possibly cancel an ongoing install task
        conan_worker.finish_working(10)
