"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import platform
import time
import os
import tempfile

from pathlib import Path
from subprocess import check_output

import conan_app_launcher as app
from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.layout_entries import AppUiEntry
from PyQt5 import QtCore, QtWidgets
from conan_app_launcher.settings import *

app.qt_app = QtWidgets.QApplication([])


def testDebugDisabledForRelease():
    assert app.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testAboutDialog(base_fixture, qtbot):
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


def testSelectConfigFileDialog(base_fixture, qtbot, mocker):
    from conan_app_launcher.ui import main_ui
    logger = Logger()  # init logger
    temp_dir = tempfile.gettempdir()
    temp_ini_path = os.path.join(temp_dir, "config.ini")

    settings = Settings(ini_file=Path(temp_ini_path))

    main_ui = main_ui.MainUi(settings)
    main_ui.show()
    qtbot.addWidget(main_ui)
    qtbot.waitExposed(main_ui, 3000)
    selection = "C:/new_config.json"
    #mocker.patch.object(QtWidgets.QMessageBox, 'question', return_value=QtWidgets.QMessageBox.Yes)
    mocker.patch.object(QtWidgets.QFileDialog, 'exec_',
                        return_value=QtWidgets.QDialog.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[selection])

    main_ui._ui.menu_open_config_file_action.trigger()
    time.sleep(3)
    assert settings.get(LAST_CONFIG_FILE) == selection
    app.conan_worker.finish_working()
    Logger.remove_qt_logger()


def testMultipleAppsUngreying(base_fixture):
    pass


def testTabsCleanupOnLoadNewConfigFile(base_fixture):
    pass


def testStartupWithExistingConfigAndOpenMenu(base_fixture, qtbot):
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
    app.conan_worker.finish_working()
    Logger.remove_qt_logger()


def testOpenApp(base_fixture):
    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable", Path("/usr/bin/sh"), "", "", True, Path("."))
        parent = QtWidgets.QWidget()
        parent.setObjectName("parent")
        app_ui = AppUiEntry(parent, app_info)
        app_ui.app_clicked()
        time.sleep(5)  # wait for terminal to spawn
        # check pid of created process
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        cmd_path = r"C:\Windows\System32\cmd.exe"  # currently hardcoded...
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable",
                            Path(cmd_path), "", "", True, Path("."))
        parent = QtWidgets.QWidget()
        parent.setObjectName("parent")
        app_ui = AppUiEntry(parent, app_info)
        app_ui.app_clicked()
        time.sleep(2)  # wait for terminal to spawn

        # check windowname of process - default shell spawns with path as windowname
        ret = check_output('tasklist /fi "WINDOWTITLE eq %s"' % cmd_path)
        assert "cmd.exe" in ret.decode("utf-8")
        lines = ret.decode("utf-8").splitlines()
        line = lines[3].replace(" ", "")
        pid = line.split("cmd.exe")[1].split("Console")[0]
        os.system("taskkill /PID " + pid)
