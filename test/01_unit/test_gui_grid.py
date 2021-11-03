"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
import os
import platform
import sys
from subprocess import check_output
from time import sleep

from PyQt5 import QtCore, QtWidgets
from conan_app_launcher.ui.modules.app_grid.app_link import AppLink
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkConfig, UiAppLinkModel
from conan_app_launcher.ui.modules.app_grid.common.app_edit_dialog import EditAppDialog
from conans.model.ref import ConanFileReference as CFR

Qt = QtCore.Qt

TEST_REF = "zlib/1.2.11@_/_"


def test_EditAppDialog_display_values(base_fixture, qtbot):
    """
    Test, if the already existent app data is displayed correctly in the dialog.
    """
    app_info = UiAppLinkConfig(name="test", conan_ref=CFR.loads("abcd/1.0.0@usr/stable"),
                               executable = "bin/myexec", is_console_application=True,
                               icon="//myicon.ico", conan_options={"a": "b", "c": "True", "d": "10"})
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = EditAppDialog(app_info, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # assert values
    assert diag._ui.name_line_edit.text() == app_info.name
    assert diag._ui.conan_ref_line_edit.text() == str(app_info.conan_ref)
    assert diag._ui.exec_path_line_edit.text() == app_info.executable
    assert diag._ui.is_console_app_checkbox.isChecked() == app_info.is_console_application
    assert diag._ui.icon_line_edit.text() == app_info.icon
    assert diag._ui.args_line_edit.text() == app_info.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()
    for opt in app_info.conan_options:
        assert f"{opt}={app_info.conan_options[opt]}" in conan_options_text
    # modify smth
    diag._ui.name_line_edit.setText("NewName")

    # press cancel - no values should be saved
    qtbot.mouseClick(diag.button_box.buttons()[1], Qt.LeftButton)

    assert app_info.name == "test"


def test_EditAppDialog_save_values(base_fixture, qtbot):
    """
    Test, if the entered data is written correctly.
    """
    app_info = UiAppLinkConfig(name="test", conan_ref=CFR.loads("abcd/1.0.0@usr/stable"),
                               executable="bin/myexec", is_console_application=True,
                               icon="//myicon.ico")
    app_info.executable = sys.executable

    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = EditAppDialog(app_info, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # edit dialog
    diag._ui.name_line_edit.setText("NewName")
    diag._ui.conan_ref_line_edit.setText(TEST_REF)
    diag._ui.exec_path_line_edit.setText("include/zlib.h")
    diag._ui.is_console_app_checkbox.setChecked(True)
    diag._ui.icon_line_edit.setText("//Myico.ico")
    diag._ui.args_line_edit.setText("--help -kw=value")
    diag._ui.conan_opts_text_edit.setText("a=b\nb=c")

    # the caller must call save_data manually
    diag.save_data()

    # assert that all infos where saved
    assert diag._ui.name_line_edit.text() == app_info.name
    assert diag._ui.conan_ref_line_edit.text() == "zlib/1.2.11@_/_" # internal representation will strip @_/_
    assert diag._ui.exec_path_line_edit.text() == app_info.executable
    assert diag._ui.is_console_app_checkbox.isChecked() == app_info.is_console_application
    assert diag._ui.icon_line_edit.text() == app_info.icon
    assert diag._ui.args_line_edit.text() == app_info.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()

    for opt in app_info.conan_options:
        assert f"{opt}={app_info.conan_options[opt]}" in conan_options_text

def test_AppLink_open(base_fixture, qtbot):
    """
    Test, if clicking on an app_button in the gui opens the app. Also check the icon.
    The set process is expected to be running.
    """
    app_config = UiAppLinkConfig(name="test", conan_ref=CFR.loads("abcd/1.0.0@usr/stable"),
                               is_console_application=True, executable=sys.executable)
    app_model = UiAppLinkModel().load(app_config, None)
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    app_ui = AppLink(root_obj, app_model)
    app_ui.load()
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)
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


def test_AppLink_icon_update_from_executable():
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path. Use python executable for testing.
    """
    # TODO
