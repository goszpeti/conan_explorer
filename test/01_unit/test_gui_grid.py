"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
from email.generator import Generator
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Callable
import pytest
from pytest_mock import MockerFixture
from conan_app_launcher.settings import AUTO_INSTALL_QUICKLAUNCH_REFS, GUI_STYLE_MATERIAL
from test.conftest import TEST_REF, PathSetup, check_if_process_running

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.ui.config import UiAppGridConfig, UiTabConfig
from conan_app_launcher.ui.model import UiApplicationModel
from conan_app_launcher.ui.views.app_grid.app_link import ListAppLink, ListAppLink
from conan_app_launcher.ui.views.app_grid.dialogs.app_edit_dialog import \
    AppEditDialog
from conan_app_launcher.ui.views.app_grid.model import (UiAppGridModel,
                                                          UiAppLinkConfig,
                                                          UiAppLinkModel)
from conan_app_launcher.core.conan_common import ConanFileReference as CFR
from PySide6 import QtCore, QtWidgets

Qt = QtCore.Qt


@pytest.mark.conanv2
def test_applink_word_wrap(qtbot, base_fixture: PathSetup):
    """ Check custom word wrap of App Link"""

    # max length > actual length -> no change
    assert ListAppLink.word_wrap("New Link", 10) == "New Link"

    # max length < actual length with one word
    assert ListAppLink.word_wrap("VeryLongAppLinkNametoTestColumnCalculation",
                                 10) == "VeryLongAp\npLinkNamet\noTestColum\nnCalculati\non"

    # max length < actual length with two words
    assert ListAppLink.word_wrap("VeryLongAppLinkNametoTestColumnCalculation 111111",
                                 10) == "VeryLongAp\npLinkNamet\noTestColum\nnCalculati\non 111111"


@pytest.mark.conanv2
def test_AppEditDialog_display_values(qtbot, base_fixture: PathSetup):
    """
    Test, if the already existent app data is displayed correctly in the dialog.
    """
    app.conan_api.init_api()
    app_info = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                               executable="bin/myexec", is_console_application=True,
                               icon="//myicon.ico", conan_options={"a": "b", "c": "True", "d": "10"})
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = AppEditDialog(app_info, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # assert values
    assert diag._ui.name_line_edit.text() == app_info.name
    assert diag._ui.conan_ref_line_edit.text() == str(app_info.conan_ref)
    assert diag._ui.execpath_line_edit.text() == app_info.executable
    assert diag._ui.is_console_app_checkbox.isChecked() == app_info.is_console_application
    assert diag._ui.icon_line_edit.text() == app_info.icon
    assert diag._ui.args_line_edit.text() == app_info.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()
    for opt in app_info.conan_options:
        assert f"{opt}={app_info.conan_options[opt]}" in conan_options_text
    # modify smth
    diag._ui.name_line_edit.setText("NewName")

    # press cancel - no values should be saved
    qtbot.mouseClick(diag._ui.button_box.buttons()[1], Qt.MouseButton.LeftButton)

    assert app_info.name == "test"


@pytest.mark.conanv2
def test_AppEditDialog_browse_buttons(qtbot, base_fixture: PathSetup, mocker):
    """
    Test, if the browse executable and icon button works:
    - buttons are always enabled (behavior change from conditional disable)
    - opens the dialog in the package folder
    - resolves the correct relative path for executables and forbids non-package-folder paths
    - resolves the correct relative path for executables and sets non-package-folder paths to the abs. path
    """
    os.system(f"conan install {TEST_REF}") # need local package

    app.conan_api.init_api()

    app_info = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                               executable="bin/myexec", is_console_application=True,
                               icon="//myicon.ico", conan_options={})
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = AppEditDialog(app_info, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # assert buttons are enabled - UPDATE: buttons are not disabled
    assert diag._ui.executable_browse_button.isEnabled()
    assert diag._ui.icon_browse_button.isEnabled()

    # enter an installed reference
    diag._ui.conan_ref_line_edit.setText(TEST_REF)
    assert diag._ui.executable_browse_button.isEnabled()
    assert diag._ui.icon_browse_button.isEnabled()

    # click executable button
    # positive test
    if platform.system() == "Windows":
        exe_rel_path = "bin\\python.exe"
    else:
        exe_rel_path = "bin/python"
    _, temp_package_path = app.conan_api.get_best_matching_package_path(
        CFR.loads(diag._ui.conan_ref_line_edit.text()), diag.resolve_conan_options())
    selection = temp_package_path / exe_rel_path
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(selection)])
    diag._ui.executable_browse_button.clicked.emit()
    assert diag._ui.execpath_line_edit.text() == exe_rel_path.replace("\\", "/")

    # negative test
    selection = base_fixture.testdata_path / "nofile.json"
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(selection)])
    
    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.DialogCode.Accepted)
    diag._ui.executable_browse_button.clicked.emit()
    # entry not changed
    assert diag._ui.execpath_line_edit.text() == exe_rel_path.replace("\\", "/")

    # open button 
    # absolute
    icon_path = app.asset_path / "icons" / GUI_STYLE_MATERIAL/  "about.svg"
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(icon_path)])
    diag._ui.icon_browse_button.clicked.emit()
    assert diag._ui.icon_line_edit.text() == str(icon_path)

    # relative to package
    icon_pkg_path = temp_package_path / "icon.svg"
    # copy icon to pkg
    shutil.copyfile(str(icon_path), str(icon_pkg_path))

    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(icon_pkg_path)])
    diag._ui.icon_browse_button.clicked.emit()
    assert diag._ui.icon_line_edit.text() == "icon.svg"
    os.unlink(str(icon_pkg_path))
    diag._ui.conan_ref_line_edit._completion_thread.join(1)
    root_obj.close()


@pytest.mark.conanv2
def test_AppEditDialog_save_values(qtbot, base_fixture: PathSetup, mocker):
    """
    Test, if the entered data is written correctly.
    """
    app.conan_api.init_api()
    app.active_settings.set(AUTO_INSTALL_QUICKLAUNCH_REFS, True)

    app_info = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                               executable="bin/myexec", is_console_application=True,
                               icon="//myicon.ico")
    app_info.executable = sys.executable

    app_config = UiAppGridConfig(tabs=[UiTabConfig(apps=[app_info])])

    app_model = UiAppGridModel().load(app_config, UiApplicationModel())

    model = app_model.tabs[0].apps[0]
    root_obj = QtWidgets.QWidget()
    qtbot.addWidget(root_obj)
    root_obj.setObjectName("parent")
    diag = AppEditDialog(model, root_obj)
    root_obj.setFixedSize(100, 200)
    root_obj.show()

    qtbot.waitExposed(root_obj)

    # edit dialog
    diag._ui.name_line_edit.setText("NewName")
    diag._ui.conan_ref_line_edit.setText(TEST_REF)
    diag._ui.execpath_line_edit.setText("include/zlib.h")
    diag._ui.is_console_app_checkbox.setChecked(True)
    diag._ui.icon_line_edit.setText("//Myico.ico")
    diag._ui.args_line_edit.setText("--help -kw=value")
    diag._ui.conan_opts_text_edit.setText("a=b\nb=c")
    app.conan_worker.finish_working()

    # the caller must call save_data manually

    mock_version_func = mocker.patch(
        'conan_app_launcher.core.conan_worker.ConanWorker.put_ref_in_version_queue')
    mock_install_func = mocker.patch(
        'conan_app_launcher.core.conan_worker.ConanWorker.put_ref_in_install_queue')
    diag.save_data()

    # assert that all infos where saved
    assert diag._ui.name_line_edit.text() == model.name
    assert diag._ui.conan_ref_line_edit.text() == TEST_REF  # internal representation will strip @_/_
    assert diag._ui.execpath_line_edit.text() == model.executable
    assert diag._ui.is_console_app_checkbox.isChecked() == model.is_console_application
    assert diag._ui.icon_line_edit.text() == model.icon
    assert diag._ui.args_line_edit.text() == model.args
    conan_options_text = diag._ui.conan_opts_text_edit.toPlainText()

    for opt in model.conan_options:
        assert f"{opt}={model.conan_options[opt]}" in conan_options_text

    vt = diag._ui.conan_ref_line_edit._completion_thread
    if vt and vt.is_alive():
        vt.join()
    app.conan_worker.finish_working()

    # check, that the package info and the available versions are updated

    mock_version_func.assert_called()
    mock_install_func.assert_called()
    diag._ui.conan_ref_line_edit._completion_thread.join(1)


@pytest.mark.conanv2
def test_AppLink_open(qtbot, base_fixture: PathSetup):
    """
    Test, if clicking on an app_button in the gui opens the app. Also check the icon.
    The set process is expected to be running.
    """
    app.conan_api.init_api()

    app_config = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                                 is_console_application=True, executable=Path(sys.executable).name)
    app_model = UiAppLinkModel().load(app_config, None)
    app_model.set_package_folder(Path(sys.executable).parent)

    root_obj = QtWidgets.QWidget()
    root_obj.setObjectName("parent")
    app_link = ListAppLink(root_obj, None, app_model)
    app_link.load()
    root_obj.setFixedSize(100, 200)
    root_obj.show()
    qtbot.addWidget(root_obj)

    qtbot.waitExposed(root_obj)
    qtbot.mouseClick(app_link._ui.app_button, Qt.MouseButton.LeftButton)
    # check pid of created process
    process_name = ""
    if platform.system() == "Linux":
        process_name = "x-terminal-emulator"
    elif platform.system() == "Windows":
        process_name = "cmd"
    
    assert check_if_process_running(process_name, cmd_contains=["conan_app_launcher"], kill=True, cmd_narg=2)


@pytest.mark.conanv2
def test_AppLink_icon_update_from_executable(qtbot, base_fixture: PathSetup):
    """
    Test, that an extracted icon from an exe is displayed after loaded and then retrived from cache.
    Check, that the icon has the temp path. Use python executable for testing.
    """
    app.conan_api.init_api()

    app_config = UiAppLinkConfig(name="test", conan_ref="abcd/1.0.0@usr/stable",
                                 is_console_application=True, executable="python")
    app_model = UiAppLinkModel().load(app_config, None)
    app_model.set_package_folder(Path(sys.executable).parent)

    root_obj = QtWidgets.QWidget()
    root_obj.setObjectName("parent")
    app_link = ListAppLink(root_obj, None, app_model)
    app_link.load()

    assert not app_link.model.get_icon().isNull()
    assert not app_link._ui.app_button._greyed_out

