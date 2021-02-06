"""
These tests test the self written qt gui components.
"""
import platform
import sys
from pathlib import Path

from conan_app_launcher.components.config_file import AppConfigEntry, AppType
from conan_app_launcher.ui import main_window
from conan_app_launcher.ui.app_grid.app_link import AppLink
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog

from PyQt5 import QtCore, QtWidgets
Qt = QtCore.Qt


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


def testEditAppDialog(base_fixture, qtbot):
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
    sig = QtCore.pyqtSignal()
    root_obj.setObjectName("parent")
    edit_app.EditAppDialog(app_info, sig, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    # qtbot.waitForWindowShown(root_obj)
    # qtbot.mouseClick(app_ui._app_button, Qt.LeftButton)
    # sleep(5)  # wait for terminal to spawn
