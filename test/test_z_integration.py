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


def testDebugDisabledForRelease():
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testStartupAndOpenMenu(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    # app.conan_worker = ConanWorker()
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.qt_root_obj.show()

    time.sleep(7)

    qtbot.addWidget(main_ui)
    main_ui._ui.menu_about_action.trigger()
    assert main_ui._about_dialog.isEnabled()


# def testClickApp(base_fixture):
#     pass
