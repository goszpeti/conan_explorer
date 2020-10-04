"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import sys
import threading
import time

from conan_app_launcher.main import main
from PyQt5 import QtCore, QtGui, QtWidgets
from conan_app_launcher.logger import Logger
import conan_app_launcher as app


def testDebugDisabledForRelease(base_fixture, qtbot):
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMinimalUseCase(base_fixture):
    # Start the gui and check if it runs and does not throw errors
    #sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_thread = threading.Thread(target=main)
    main_thread.start()

    time.sleep(7)

    # try:
    print("Start quit")
    app.app_main_ui.qt_root_obj.close()
    app.qt_app.quit()
    time.sleep(5)
    main_thread.join()
    # finally:
    #    if main_thread:
    #        print("Join test thread")
    #        main_thread.join()


def testOpenMenu(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    #app.conan_worker = ConanWorker()
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.qt_root_obj.show()
    qtbot.addWidget(main_ui)
    main_ui._ui.menu_about_action.trigger()
    # qtbot.mouseClick(main_ui._ui, QtCore.Qt.LeftButton)

# def testClickApp(base_fixture):
#     pass
