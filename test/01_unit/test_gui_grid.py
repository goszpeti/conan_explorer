"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
import os
import platform
import sys
import tempfile
from pathlib import Path
from subprocess import check_output
from time import sleep

import conan_app_launcher.app as app
import pytest
from conan_app_launcher import TEMP_ICON_DIR_NAME
from conan_app_launcher.settings import DISPLAY_APP_USERS
from conan_app_launcher.ui.data import UiApplicationConfig, UiTabConfig
from conan_app_launcher.ui.model import UiApplicationModel
from conan_app_launcher.ui.modules.app_grid.app_link import AppLink
from conan_app_launcher.ui.modules.app_grid.common.app_edit_dialog import EditAppDialog
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkConfig, UiAppLinkModel
from conans.model.ref import ConanFileReference as CFR
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt

TEST_REF = "zlib/1.2.11@_/_"


def test_EditAppDialog_display_values(base_fixture, qtbot):
    """
    Test, if the already existent app data is displayed correctly in the dialog.
    """
    app_info = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
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


def test_EditAppDialog_save_values(base_fixture, qtbot, mocker):
    """
    Test, if the entered data is written correctly.
    """

    app_info = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                               executable="bin/myexec", is_console_application=True,
                               icon="//myicon.ico")
    app_info.executable = sys.executable
    
    app_config = UiApplicationConfig(tabs=[UiTabConfig(apps=[app_info])])
    from conan_app_launcher.ui.modules.app_grid.model import UiTabModel

    app_model = UiApplicationModel().load(app_config)

    model = app_model.tabs[0].apps[0]
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = EditAppDialog(model, root_obj)
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
    app.conan_worker.finish_working()

    # the caller must call save_data manually

    mock_version_func = mocker.patch(
        'conan_app_launcher.components.conan_worker.ConanWorker.put_ref_in_version_queue')
    mock_install_func = mocker.patch(
        'conan_app_launcher.components.conan_worker.ConanWorker.put_ref_in_install_queue')
    diag.save_data()

    # assert that all infos where saved
    assert diag._ui.name_line_edit.text() == model.name
    assert diag._ui.conan_ref_line_edit.text() == TEST_REF  # internal representation will strip @_/_
    assert diag._ui.exec_path_line_edit.text() == model.executable
    assert diag._ui.is_console_app_checkbox.isChecked() == model.is_console_application
    assert diag._ui.icon_line_edit.text() == model.icon
    assert diag._ui.args_line_edit.text() == model.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()

    for opt in model.conan_options:
        assert f"{opt}={model.conan_options[opt]}" in conan_options_text

    vt = diag._ui.conan_ref_line_edit._validator_thread
    if vt and vt.is_alive():
        vt.join()
    app.conan_worker.finish_working()

    # check, that the package info and the available versions are updated

    mock_version_func.assert_called()
    mock_install_func.assert_called()

def test_AppLink_open(base_fixture, qtbot):
    """
    Test, if clicking on an app_button in the gui opens the app. Also check the icon.
    The set process is expected to be running.
    """
    app_config = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                               is_console_application=True, executable=sys.executable)
    app_model = UiAppLinkModel().load(app_config, None)
    app_model.set_package_info(Path(sys.executable).parent)

    root_obj = QtWidgets.QWidget()
    root_obj.setObjectName("parent")
    app_ui = AppLink(root_obj, app_model)
    app_ui.load()
    root_obj.setFixedSize(100, 200)
    root_obj.show()
    qtbot.addWidget(root_obj)

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


def test_AppLink_icon_update_from_executable(base_fixture, qtbot):
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path. Use python executable for testing.
    """
    if not platform.system() == "Windows":
        pytest.skip()
    app_config = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                                 is_console_application=True, executable=sys.executable)
    app_model = UiAppLinkModel().load(app_config, None)
    app_model.set_package_info(Path(sys.executable).parent)

    root_obj = QtWidgets.QWidget()
    root_obj.setObjectName("parent")
    app_ui = AppLink(root_obj, app_model)
    app_ui.load()

    icon = app_ui.model.get_icon_path()
    # CI returns dos style short path, which I don't how to resolve... so workaround:
    assert "temp/" + TEMP_ICON_DIR_NAME in str(icon.parent.as_posix()).lower()
    assert "python" in icon.name
    assert not app_ui._app_button._greyed_out


def test_AppLink_cbox_switch(base_fixture, ui_config_fixture, qtbot):
    """
    Test, that changing the version resets the channel and user correctly
    """
    # all versions have different user and channel names, so we can distinguish them
    conanfile = str(base_fixture.testdata_path / "conan" / "conanfile_custom.py")
    os.system(f"conan create {conanfile} switch_test/1.0.0@user1/channel1")
    os.system(f"conan create {conanfile} switch_test/1.0.0@user1/channel2")
    os.system(f"conan create {conanfile} switch_test/1.0.0@user2/channel3")
    os.system(f"conan create {conanfile} switch_test/1.0.0@user2/channel4")
    os.system(f"conan create {conanfile} switch_test/2.0.0@user3/channel5")
    os.system(f"conan create {conanfile} switch_test/2.0.0@user3/channel6")
    os.system(f"conan create {conanfile} switch_test/2.0.0@user4/channel7")
    os.system(f"conan create {conanfile} switch_test/2.0.0@user4/channel8")

    # loads it into cache
    app.conan_api.search_recipe_in_remotes(CFR.loads("switch_test/1.0.0@user1/channel1"))
    # need cache
    app.active_settings.set(DISPLAY_APP_USERS, True)

    #app_info._executable = Path(sys.executable)
    app_config = UiAppLinkConfig(name="test", conan_ref="switch_test/1.0.0@user1/channel1",
                                 is_console_application=True, executable="")
    app_model = UiAppLinkModel().load(app_config, None)
    root_obj = QtWidgets.QWidget()
    root_obj.setFixedSize(100, 200)
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    app_link = AppLink(root_obj, app_model)
    app_link.load()
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # check initial state
    assert app_link._app_version_cbox.count() == 2
    assert app_link._app_version_cbox.itemText(0) == "1.0.0"
    assert app_link._app_version_cbox.itemText(1) == "2.0.0"
    assert app_link._app_user_cbox.count() == 2
    assert app_link._app_user_cbox.itemText(0) == "user1"
    assert app_link._app_user_cbox.itemText(1) == "user2"
    assert app_link._app_channel_cbox.count() == 2
    assert app_link._app_channel_cbox.itemText(0) == "channel1"
    assert app_link._app_channel_cbox.itemText(1) == "channel2"

    # now change version to 2.0.0 -> user can change to default, channel should go to NA
    # this is done, so that the user can select it and not autinstall something random
    app_link._app_version_cbox.setCurrentIndex(1)
    assert app_link._app_version_cbox.count() == 2
    assert app_link._app_version_cbox.itemText(0) == "1.0.0"
    assert app_link._app_version_cbox.itemText(1) == "2.0.0"
    assert app_link._app_user_cbox.count() == 2
    assert app_link._app_user_cbox.itemText(0) == "user3"
    assert app_link._app_user_cbox.itemText(1) == "user4"
    assert app_link._app_channel_cbox.count() == 3
    assert app_link._app_channel_cbox.itemText(0) == "NA"
    assert app_link._app_channel_cbox.currentIndex() == 0
    assert app_link._app_channel_cbox.itemText(1) == "channel5"
    assert app_link._app_channel_cbox.itemText(2) == "channel6"

    # check that reference and executable has updated
    assert app_model.conan_ref == "switch_test/2.0.0@user3/NA"
    assert app_model.get_executable_path() == Path("NULL")

    # change user
    app_link._app_channel_cbox.setCurrentIndex(1)
    # setting a channel removes NA entry and entry becomes -1
    assert app_link._app_channel_cbox.itemText(0) == "channel5"
    assert app_link._app_channel_cbox.itemText(1) == "channel6"
    assert app_link._app_channel_cbox.currentIndex() == 0
    # conan worker currently not integrated -> no pkg path update
    # assert app_model._package_folder.exists()

    # now change back to 1.0.0 -> user can change to default, channel should go to NA
    app_link._app_version_cbox.setCurrentIndex(0)
    assert app_link._app_version_cbox.count() == 2
    assert app_link._app_version_cbox.itemText(0) == "1.0.0"
    assert app_link._app_version_cbox.itemText(1) == "2.0.0"
    assert app_link._app_user_cbox.count() == 2
    assert app_link._app_user_cbox.itemText(0) == "user1"
    assert app_link._app_user_cbox.itemText(1) == "user2"
    assert app_link._app_channel_cbox.count() == 3
    assert app_link._app_channel_cbox.itemText(0) == "NA"
    assert app_link._app_channel_cbox.currentIndex() == 0
    assert app_link._app_channel_cbox.itemText(1) == "channel1"
    assert app_link._app_channel_cbox.itemText(2) == "channel2"
