"""
The system tests actually start the application.
Because the unit tests use qtbot helper, a QApplication object is already present (is a Singleton)
and it cannot be instatiated anew with the main loop of the program.
"""
import os
import time
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, CREATE_NEW_PROCESS_GROUP

import conan_app_launcher as app
from conan_app_launcher.settings import *


def testDebugDisabledForRelease():
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMainLoop(base_fixture):
    """
    Smoke test, that the application can start.
    No error expected.
    """
    # this test causes a segmentation fault on linux - possibly because
    # the gui thread does not run in the main thread...

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
        assert proc.poll() == 1  # terminate exits always with 1
    finally:
        # delete config file
        os.remove(str(settings_file_path))
