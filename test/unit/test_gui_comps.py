"""
These tests test the self written qt gui components.
"""
import platform
import sys
import os
from subprocess import check_output
from time import sleep
from pathlib import Path


from conan_app_launcher.main import load_base_components
from conan_app_launcher.components.config_file import AppConfigEntry, AppType, OptionType
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.app_link import AppLink
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog

from PyQt5 import QtCore, QtWidgets
Qt = QtCore.Qt


class pyqtSignal():
    def connect(self, *args):
        pass

    def emit(self, *args):
        pass


def testAboutDialog(base_fixture, qtbot):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = main_window.AboutDialog(root_obj)
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitForWindowShown(widget)

    assert "Conan App Launcher" in widget._text.toPlainText()
    qtbot.mouseClick(widget._button_box.buttons()[0], Qt.LeftButton)
    assert widget.isHidden()


def testEditAppDialogNewAppLink(base_fixture, qtbot):
    """ Test, if a new dialog on empty AppData will ..."""


def testEditAppDialogFillValues(base_fixture, qtbot):
    """
    Test, if the already existant app data is displayed correctly in the dialog.
    """
    app_data: AppType = {"name": "test", "conan_ref": "abcd/1.0.0@usr/stable",
                         "executable": "bin/myexec",
                         "console_application": True, "icon": "//myicon.ico"}
    app_info = AppConfigEntry(app_data)
    app_info.conan_options = {"a": "b", "c": "True", "d": "10"}

    if platform.system() == "Windows":
        assert app_info.icon.is_file()
        assert app_info.icon.suffix == ".png"

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    sig = QtCore.pyqtSignal()
    root_obj.setObjectName("parent")
    diag = EditAppDialog(app_info, sig, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitForWindowShown(root_obj)

    # assert values
    assert diag._ui.name_line_edit.text() == app_info.name
    assert diag._ui.conan_ref_line_edit.text() == str(app_info.conan_ref)
    assert diag._ui.exec_path_line_edit.text() == app_data.get("executable")
    assert diag._ui.is_console_app_checkbox.isChecked() == app_info.is_console_application
    assert diag._ui.icon_line_edit.text() == app_data.get("icon")
    assert diag._ui.args_line_edit.text() == app_info.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()
    for opt in app_info.conan_options:
        assert f"{opt}={app_info.conan_options[opt]}" in conan_options_text

    # modify smth
    diag._ui.name_line_edit.setText("NewName")

    # press cancel - no values should be saved
    qtbot.mouseClick(diag.button_box.buttons()[1], Qt.LeftButton)

    assert app_info.name == "test"


def testEditAppDialogReadValues(base_fixture, qtbot):
    """
    Test, if the entered/modified/untouched data is written correctly after pressing OK.
    """
    app_data: AppType = {"name": "test", "conan_ref": "abcd/1.0.0@usr/stable",
                         "executable": "", "console_application": True, "icon": ""}
    app_info = AppConfigEntry(app_data)
    app_info._executable = Path(sys.executable)

    if platform.system() == "Windows":
        assert app_info.icon.is_file()
        assert app_info.icon.suffix == ".png"

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    sig = QtCore.pyqtSignal()
    root_obj.setObjectName("parent")
    EditAppDialog(app_info, sig, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitForWindowShown(root_obj)

    # qtbot.mouseClick(app_ui._app_button, Qt.LeftButton)
    # sleep(5)  # wait for terminal to spawn


def testAppLinkOpen(base_fixture, qtbot):
    """
    Test, if clicking on an app_button in the gui opens the app. Also check the icon.
    The set process is expected to be running.
    """
    app_data: AppType = {"name": "test", "conan_ref": "abcd/1.0.0@usr/stable",
                         "executable": "", "console_application": True, "icon": ""}
    app_info = AppConfigEntry(app_data)
    app_info._executable = Path(sys.executable)

    if platform.system() == "Windows":
        assert app_info.icon.is_file()
        assert app_info.icon.suffix == ".png"

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    sig = pyqtSignal()
    app_ui = AppLink(root_obj, app_info, sig, sig)
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


def testAppLinkVersionAndChannelSwitch(base_fixture, qtbot):
    """
    TODO Implmement
    """
    app_data: AppType = {"name": "test", "conan_ref": "abcd/1.0.0@usr/stable",
                         "executable": "", "console_application": True, "icon": ""}
    app_info = AppConfigEntry(app_data)
    app_info._executable = Path(sys.executable)

    if platform.system() == "Windows":
        assert app_info.icon.is_file()
        assert app_info.icon.suffix == ".png"

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    sig = pyqtSignal()
    app_ui = AppLink(root_obj, app_info, sig, sig)
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


# testNewAppLink()

# testEditPackageReference()
