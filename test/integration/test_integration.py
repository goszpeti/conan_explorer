"""
The integration tests actually start the application.
Because the unit tests use qtbot helper, a QApplication object is already present (is a Singleton)
and it cannot be instatiated anew with the main loop of the program.
"""

import os
import sys
import threading
import time

import conan_app_launcher as app
from conan_app_launcher.conan import ConanWorker
from conan_app_launcher.logger import Logger
from conan_app_launcher.main import main
from conan_app_launcher.ui.layout_entries import AppUiEntry
from PyQt5 import QtCore, QtGui, QtWidgets


def testMainLoop(base_fixture):
    # this test causes a segmentation fault on linux - possibly because
    # the gui thread does not run in the main thread...

    import conan_app_launcher as app
    from conan_app_launcher.main import handle_cmd_args
    sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    main_thread = threading.Thread(target=handle_cmd_args, daemon=True)
    main_thread.start()

    time.sleep(7)

    try:
        print("Start quit")
        app.qt_app.quit()
        del(app.qt_app)
        app.qt_app = None
        time.sleep(3)
    finally:
        if main_thread:
            print("Join test thread")
            main_thread.join(5)
