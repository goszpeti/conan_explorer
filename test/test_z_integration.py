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
from conan_app_launcher.ui.layout_entries import AppUiEntry
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
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.show()
    qtbot.addWidget(main_ui)
    qtbot.waitExposed(main_ui, 3000)
    main_ui._ui.menu_about_action.trigger()
    time.sleep(3)
    assert main_ui._about_dialog.isEnabled()
    qtbot.mouseClick(main_ui._about_dialog._button_box.buttons()[0], QtCore.Qt.LeftButton)


def testOpenApp(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.show()
    qtbot.addWidget(main_ui)
    qtbot.waitExposed(main_ui, 3000)
    tab_name = "Basics"
    app_name = "App2"
    app_ui_obj: AppUiEntry = main_ui._ui.tabs.findChild(
        QtWidgets.QVBoxLayout, name="tab_widgets_" + tab_name + app_name)
    qtbot.mouseClick(app_ui_obj._app_button, QtCore.Qt.LeftButton)
    # TODO need an app which stays open


def testMainLoop(base_fixture):
    # this test causes a segmentation fault on linux - possibly because
    # the gui thread does not run in the main thread...

    import conan_app_launcher as app
    from conan_app_launcher.main import handle_cmd_args
    sys.argv = ["main", "-f", str(base_fixture.testdata_path / "app_config.json")]
    main_thread = threading.Thread(target=handle_cmd_args)
    main_thread.start()

    time.sleep(7)

    try:
        print("Start quit")
        app.qt_app.quit()
        time.sleep(3)
    finally:
        if main_thread:
            print("Join test thread")
            main_thread.join(5)
