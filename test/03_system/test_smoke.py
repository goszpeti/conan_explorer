"""
The system tests actually start the application.
Because the unit tests use qtbot helper, a QApplication object is already present (is a Singleton)
and it cannot be instatiated anew with the main loop of the program.
"""
import os
import sys
import time
from pathlib import Path
from subprocess import Popen

import conan_app_launcher
from conan_app_launcher.settings import (LAST_CONFIG_FILE, SETTINGS_INI_TYPE,
                                         settings_factory)
from PyQt5 import QtWidgets


def test_main_loop_mock(base_fixture, mocker):
    """
    Smoke test, that the application runs through.
    No error expected.
    """

    main_ui_mock = mocker.patch("conan_app_launcher.ui.main_window.MainWindow")
    qapp_mock = mocker.patch.object(QtWidgets.QApplication, "exec_")
    # delayed import necessary, so the mocker can patch the object before
    from conan_app_launcher import __main__

    __main__.run_conan_app_launcher()
    time.sleep(2)

    main_ui_mock.assert_called_once()
    qapp_mock.assert_called_once()


def test_main_loop(base_fixture):
    """
    Smoke test, that the application can start.
    No error expected.
    """

    settings_file_path = Path.home() / conan_app_launcher.SETTINGS_FILE_NAME
    settings = settings_factory(SETTINGS_INI_TYPE, settings_file_path)
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))
    settings.save()

    # conan_app_launcher
    proc = Popen([sys.executable, "-m", "conan_app_launcher"])
    time.sleep(7)
    try:
        assert proc.poll() is None
        proc.terminate()
        time.sleep(3)
        assert proc.poll() != 0  # terminate exits os dependently, but never with success (0)
    finally:
        # delete config file
        os.remove(str(settings_file_path))
