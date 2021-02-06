"""
The system tests actually start the application.
Because the unit tests use qtbot helper, a QApplication object is already present (is a Singleton)
and it cannot be instatiated anew with the main loop of the program.
"""
import os
import time
from pathlib import Path
from subprocess import Popen

from PyQt5 import QtWidgets
import conan_app_launcher
from conan_app_launcher import main
#from conan_app_launcher.ui import main_window
#from conan_app_launcher.settings import *


def testDebugDisabledForRelease():
    assert conan_app_launcher.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMainLoopMock(base_fixture, mocker):
    """
    Smoke test, that the application runs through.
    No error expected.
    """

    mocker.patch("conan_app_launcher.ui.main_window.MainUi")
    mocker.patch.object(QtWidgets.QApplication, "exec_")

    main.main()
    time.sleep(2)

    conan_app_launcher.ui.main_window.MainUi.assert_called_once()
    QtWidgets.QApplication.exec_.assert_called_once()


def testMainLoop(base_fixture):
    """
    Smoke test, that the application can start.
    No error expected.
    """

    settings_file_path = Path.home() / ".cal_config"
    settings = Settings(ini_file=settings_file_path)
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))
    settings.save_to_file()

    # conan_app_launcher
    proc = Popen(["python", str(base_fixture.base_path / "src" / "conan_app_launcher" / "main.py")])
    time.sleep(7)
    try:
        assert proc.poll() is None
        proc.terminate()
        time.sleep(3)
        assert proc.poll() != 0  # terminate exits os dependently, but never with success (0)
    finally:
        # delete config file
        os.remove(str(settings_file_path))
