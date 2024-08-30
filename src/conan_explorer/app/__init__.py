import argparse
import os
import platform
import sys
from tempfile import gettempdir
from typing import TYPE_CHECKING

from conan_explorer import (APP_NAME, PKG_NAME, SETTINGS_FILE_NAME, __version__,
                            asset_path, user_save_path)
from conan_explorer.settings import (SETTINGS_INI_TYPE, SettingsInterface,
                                     settings_factory)

from .base_ui.crash import bug_dialog_exc_hook
from .base_ui.loading import LoaderGui
from .base_ui.theming import activate_theme
from .logger import Logger
from .system import check_for_wayland

if TYPE_CHECKING:
    from conan_explorer.conan_wrapper import ConanCommonUnifiedApi, ConanWorker

### Global variables ###

active_settings: SettingsInterface = settings_factory(SETTINGS_INI_TYPE,
                                        user_save_path / (SETTINGS_FILE_NAME + ".ini"))
conan_api: "ConanCommonUnifiedApi"  # initialized by load_conan
conan_worker: "ConanWorker"  # initialized by load_conan
qt_platform = ""

def run_application():
    """ Start the Qt application and load the main window """
    parse_cmd_args()
    init_platform()
    # Change cwd to temp, so temporary files become writable, 
    # even if the current folder is not - Fixes #168
    os.chdir(gettempdir())

    qt_app = load_qapp()
    # Loading dialog until Conan is available
    loader = LoaderGui(None)
    loader.load_for_blocking(None, load_conan, (loader, ), cancel_button=False,
                                loading_text="Starting " + APP_NAME + " " + __version__)
    loader.wait_for_finished()

    from conan_explorer.ui.main_window import MainWindow
    from PySide6 import QtGui
    # inline imports to optimize load times
    main_window = MainWindow(qt_app)
    main_window.setWindowIcon(QtGui.QIcon(str(asset_path / "icons" / "icon.ico")))
    main_window.show()  # show first, then load appsgrid with progress bar
    main_window.load()

    qt_app.exec()

    main_window.save_window_state()
    # cancel conan worker tasks on exit
    if conan_worker:
        conan_worker.finish_working(10)


def parse_cmd_args():
    """
    All CLI related functions.
    """
    parser = argparse.ArgumentParser(
        prog=PKG_NAME, description=f"{PKG_NAME} command line interface")
    parser.add_argument("-v", "--version", action="version",
                        version=__version__)
    parser.add_argument("-p", "--platform", type=str)

    args = parser.parse_args()
    global qt_platform
    qt_platform = args.platform

def init_platform():
    if platform.system() == "Windows":
        # Workaround for Windows, so that on the taskbar the
        # correct icon will be shown (and not the default python icon).
        from ctypes import windll  # Only exists on Windows.
        MY_APP_ID = 'ConanAppLauncher.' + __version__
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)
    elif platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)


def load_conan(loader: LoaderGui):
    global conan_api, conan_worker
    from conan_explorer.conan_wrapper import ConanApiFactory, ConanWorker
    conan_api = ConanApiFactory()
    conan_worker = ConanWorker(conan_api, active_settings)
    loader.loading_string_signal.emit("Initializing Conan")
    conan_api.init_api()

def load_qapp():
    """ Load bootstrapping to be able to display a first widget. """
    # this import takes seconds - it could only be possibly parallelized 
    # with more basics gui frameworks
    from PySide6 import QtCore, QtWidgets

    # Apply Qt attributes (only possible before QApplication is created)
    try:
        # Passthrough seems to work well for high dpi scaling
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception:
        Logger().debug("Can't set DPI Rounding", exc_info=True)

    if qt_platform:
        os.environ["QT_QPA_PLATFORM"] = qt_platform
    else:
        if check_for_wayland(): # enable native Wayland support
            os.environ["QT_QPA_PLATFORM"] = "wayland"

    # to use icons in qss file
    QtCore.QDir.addSearchPath('icons', os.path.join(asset_path, 'icons'))

    # disable reacting on light and dark themed mode automatically, otherwise
    # we can get get dark mode window bar in light mode
    QtWidgets.QApplication.setDesktopSettingsAware(False)

    qt_app = QtWidgets.QApplication(sys.argv)
    qt_app.setApplicationName(APP_NAME)
    qt_app.setApplicationDisplayName(APP_NAME)

    # Overwrite the excepthook with our own -
    # this will provide a method to report bugs for the user
    sys.excepthook = bug_dialog_exc_hook  # dialog needs qt_app
    activate_theme(qt_app)
    return qt_app
