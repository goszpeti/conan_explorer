"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import sys
import threading
import time

import conan_app_launcher as app
from conan_app_launcher.conan import ConanWorker
from conan_app_launcher.logger import Logger
from conan_app_launcher.main import main
from PyQt5 import QtCore, QtGui, QtWidgets


def testDebugDisabledForRelease():
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testAbouDialog(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    logger = Logger()  # init logger
    root_obj = QtWidgets.QWidget()
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    widget = main_ui.AboutDialog(root_obj)
    widget.show()
    qtbot.waitForWindowShown(widget)
    qtbot.addWidget(widget)

    assert "Conan App Launcher" in widget._text.text()
    qtbot.mouseClick(widget._button_box.buttons()[0], QtCore.Qt.LeftButton)
    assert widget.isHidden()


def testStartupAndOpenMenu(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    app.conan_worker = ConanWorker()
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.show()
    qtbot.addWidget(main_ui)
    qtbot.waitExposed(main_ui, 3000)
    main_ui._ui.menu_about_action.trigger()
    time.sleep(3)
    assert main_ui._about_dialog.isEnabled()

    # app.conan_worker.finish_working(5)

# def testClickApp(base_fixture):
#     pass
