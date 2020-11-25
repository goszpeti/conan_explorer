"""
These tests test the self written qt gui components.
"""
import platform
import os
import sys
from subprocess import check_output
from time import sleep
from pathlib import Path

from conan_app_launcher.base import Logger
from conan_app_launcher.components import AppEntry
from conan_app_launcher.ui import main_ui
from conan_app_launcher.ui.layout_entries import AppUiEntry

from PyQt5 import QtCore, QtWidgets
Qt = QtCore.Qt


def testAboutDialog(base_fixture, qtbot):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = main_ui.AboutDialog(root_obj)
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitForWindowShown(widget)

    assert "Conan App Launcher" in widget._text.text()
    qtbot.mouseClick(widget._button_box.buttons()[0], Qt.LeftButton)
    assert widget.isHidden()


def testOpenApp(base_fixture, qtbot):
    """
    Test, if clicking on an app_button in the gui opens the app. Also check the icon.
    The set process is expected to be running.
    """
    app_info = None
    if platform.system() == "Linux":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable", {},
                            Path(sys.executable), "", "", True, Path("."))
    elif platform.system() == "Windows":
        app_info = AppEntry("test", "abcd/1.0.0@usr/stable", {},
                            Path(sys.executable), "", "", True, Path("."))

    assert app_info.icon.is_file()
    assert app_info.icon.suffix == ".png"

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    app_ui = AppUiEntry(root_obj, app_info)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitForWindowShown(root_obj)
    qtbot.mouseClick(app_ui._app_button, Qt.LeftButton)
    sleep(5)  # wait for terminal to spawn
    # check pid of created process
    if platform.system() == "Linux":
        ret = check_output(["xwininfo", "-name", "Terminal"]).decode("utf-8")
        assert "Terminal" in ret
        os.system("pkill --newest terminal")
    elif platform.system() == "Windows":
        # check windowname of process - default shell spawns with path as windowname
        ret = check_output(f'tasklist /fi "WINDOWTITLE eq {str(sys.executable)}"')
        assert "python.exe" in ret.decode("utf-8")
        lines = ret.decode("utf-8").splitlines()
        line = lines[3].replace(" ", "")
        pid = line.split("python.exe")[1].split("Console")[0]
        os.system("taskkill /PID " + pid)
