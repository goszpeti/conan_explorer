"""
The system tests actually start the application.
Because the unit tests use qtbot helper, a QApplication object is already present (is a Singleton)
and it cannot be instatiated anew with the main loop of the program.
"""
import os
import sys
import threading
import time
from pathlib import Path

import conan_app_launcher as app
from conan_app_launcher.settings import *


def testDebugDisabledForRelease():
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMainLoop(base_fixture):
    # this test causes a segmentation fault on linux - possibly because
    # the gui thread does not run in the main thread...

    settings_file_path = Path.home() / ".cal_config"
    settings = Settings(ini_file=settings_file_path)
    config_file_path = base_fixture.testdata_path / "app_config.json"
    settings.set(LAST_CONFIG_FILE, str(config_file_path))
    settings.save_to_file()

    from conan_app_launcher.main import main
    sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    main_thread = threading.Thread(target=main, daemon=True)
    main_thread.start()

    time.sleep(7)

    try:
        app.qt_app.quit()
        del(app.qt_app)
        app.qt_app = None
        time.sleep(3)
    finally:
        if main_thread:
            print("Join test thread")
            main_thread.join(5)
        # delete config file
        os.remove(str(settings_file_path))
