"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import platform
import time
import os
from pathlib import Path
from subprocess import check_output

import conan_app_launcher as app
from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.layout_entries import AppUiEntry
from PyQt5 import QtCore, QtWidgets

app.qt_app = QtWidgets.QApplication([])


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
    Logger.remove_qt_logger()


def testOpenApp(base_fixture, qtbot):
    from conan_app_launcher.ui import main_ui
    logger = Logger()  # init logger
    app.config_file_path = base_fixture.testdata_path / "app_config.json"
    main_ui = main_ui.MainUi()
    main_ui.show()
    qtbot.addWidget(main_ui)
    qtbot.waitExposed(main_ui, 3000)
    time.sleep(2)  # add this so it stays open a little bit
    tab_name = "Basics"
    app_name = "App2"
    app_ui_obj: AppUiEntry = main_ui._ui.tabs.findChild(
        QtWidgets.QVBoxLayout, name="tab_widgets_" + tab_name + app_name)
    qtbot.mouseClick(app_ui_obj._app_button, QtCore.Qt.LeftButton)
    # TODO need an app which stays open
    Logger.remove_qt_logger()


def testOpenCmdApp(base_fixture):
    # This test only works in linux...
    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path("/usr/bin/sh"), "", True, Path("."))
        parent = QtWidgets.QWidget()
        parent.setObjectName("parent")
        app_ui = AppUiEntry(parent, app_info)
        app_ui.app_clicked()
        time.sleep(2)
        # ckeck pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        cmd_path = r"C:\Windows\System32\cmd.exe"  # currently hardcoded...
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "", True, Path("."))
        parent = QtWidgets.QWidget()
        parent.setObjectName("parent")
        app_ui = AppUiEntry(parent, app_info)
        app_ui.app_clicked()
        # check windowname of process - default shell spawns with path as windowname
        ret = check_output('tasklist /fi "WINDOWTITLE eq %s"' % cmd_path)
        assert "cmd.exe" in ret.decode("utf-8")
        os.system("taskkill /pid " + str(pid))
