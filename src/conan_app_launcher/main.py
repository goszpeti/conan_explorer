"""
Entry module of Conan App Launcher
Sets up cmd arguments, config file and starts the gui
"""
import os
import sys
import traceback
import platform
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

import conan_app_launcher as this
from conan_app_launcher.settings import Settings
from conan_app_launcher.base import Logger
from conan_app_launcher.ui import main_ui

try:
    # this is a workaround for windows, so that on the taskbar the
    # correct icon will be shown (and not the default python icon)
    from PyQt5.QtWinExtras import QtWin
    MY_APP_ID = 'ConanAppLauncher.' + this.__version__
    QtWin.setCurrentProcessExplicitAppUserModelID(MY_APP_ID)
except ImportError:
    pass

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


def main():
    """
    Start the Qt application
    """

    if platform.system() == "Darwin":
        print("Mac OS is currently not supported.")
        sys.exit(1)
    # Redirect stdout and stderr for usage with pythonw as executor -
    # otherwise conan will not work
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.path.join(os.getenv("TEMP"),
                                       "stderr-" + this.PROG_NAME), "w")
    # init logger first
    this.base_path = Path(__file__).absolute().parent
    logger = Logger()

    # apply Qt attributes (only at init possible)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # start Qt app and ui
    if not this.qt_app:
        this.qt_app = QtWidgets.QApplication([])
    icon = QtGui.QIcon(str(this.base_path / "assets" / "icon.ico"))

    settings_file_path = Path.home() / ".cal_config"
    settings = Settings(ini_file=settings_file_path)

    app_main_ui = main_ui.MainUi(settings)
    app_main_ui.setWindowIcon(icon)
    app_main_ui.show()

    try:
        this.qt_app.exec_()
    except:  # pylint:disable=bare-except
        trace_back = traceback.format_exc()
        logger.error(f"Application crashed: \n{trace_back}")
    finally:
        settings.save_to_file()  # save on exit
        if this.conan_worker:  # cancel conan worker tasks on exit
            this.conan_worker.finish_working()


if __name__ == "__main__":
    main()
