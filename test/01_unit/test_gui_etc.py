"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
from pathlib import Path
import platform
import sys
import traceback
from unittest.mock import Mock
from conan_app_launcher.app.crash import bug_dialog_exc_hook
from conan_app_launcher.conan_wrapper.conanV1 import ConanApi
from conan_app_launcher.settings import DEFAULT_INSTALL_PROFILE, FILE_EDITOR_EXECUTABLE
from conan_app_launcher.ui.common.theming import get_user_theme_color
from conan_app_launcher.ui.views.conan_conf.dialogs.remote_login_dialog import RemoteLoginDialog
from test.conftest import TEST_REF, app_qt_fixture, conan_remove_ref

import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
import pytest
from conan_app_launcher.conan_wrapper.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.views import AboutPage
from conan_app_launcher.ui.dialogs import show_bug_reporting_dialog, FileEditorSelDialog
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog
from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit
from conan_app_launcher.conan_wrapper.types import ConanRef, Remote
from PySide6 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt

def test_select_file_editor(app_qt_fixture, base_fixture, mocker):
    """ Test, that the select file editor displays the setting and saves it, if it is valid. """
    # set valid executable first
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, sys.executable)
    
    root_obj = QtWidgets.QWidget()
    dialog = FileEditorSelDialog(root_obj)
    app_qt_fixture.addWidget(root_obj)
    app_qt_fixture.waitExposed(dialog)

    assert dialog._ui.file_edit.text() == sys.executable

    # set invalid path
    dialog._ui.file_edit.setText("unknown")

    # press ok
    dialog._ui.button_box.accepted.emit()

    # setting should change - it could be a system command
    assert app.active_settings.get_string(FILE_EDITOR_EXECUTABLE) == "unknown"

    # set valid path
    app.active_settings.set(FILE_EDITOR_EXECUTABLE, "")
    dialog = FileEditorSelDialog(root_obj)
    dialog._ui.file_edit.setText(sys.executable)
    # press ok
    dialog._ui.button_box.accepted.emit()
    # setting should be changed
    assert app.active_settings.get_string(FILE_EDITOR_EXECUTABLE) == sys.executable

    # try browse button

    dialog = FileEditorSelDialog(root_obj)
    dialog._ui.file_edit.setText("")
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(sys.executable)])
    dialog._ui.browse_button.clicked.emit()
    assert dialog._ui.file_edit.text() == sys.executable

@pytest.mark.conanv2
def test_edit_line_conan(app_qt_fixture, base_fixture, light_theme_fixture):
    """ Test, that the line edit validates on edit
    and displays the local packages instantly and the remote ones after a delay
    """
    conan_remove_ref(TEST_REF)
    root_obj = QtWidgets.QWidget()
    widget = ConanRefLineEdit(root_obj)
    app_qt_fixture.addWidget(root_obj)
    widget.show()
    widget.showEvent(QtGui.QShowEvent())
    app_qt_fixture.waitExposed(widget)
    # test recipe ref without revision
    widget.setText(TEST_REF)
    assert ConanRefLineEdit.VALID_COLOR_LIGHT in widget.styleSheet()
    # test autocompletion (very implicit)
    assert widget._completion_thread
    widget._completion_thread.join(10)
    assert TEST_REF in widget.completer().model().stringList()
    # test package ref with revision
    widget.setText(TEST_REF + ":127af201a4cdf8111e2e08540525c245c9b3b99e")
    assert ConanRefLineEdit.VALID_COLOR_LIGHT in widget.styleSheet()
    # test wrong recipe
    widget.setText("zlib/1.2.8@@")
    assert ConanRefLineEdit.INVALID_COLOR in widget.styleSheet()
    # test validator disabled - color doesn't change on correct
    widget.validator_enabled = False
    widget.setText("zlib/1.2.8")
    assert ConanRefLineEdit.INVALID_COLOR in widget.styleSheet()
    widget.close()

@pytest.mark.conanv2
def test_conan_install_dialog(app_qt_fixture, base_fixture, mocker):
    """ 
    Tests, that the Conan Install dialog can install references, packages and the update and auto_install flag works.
    """
    app.conan_api.init_api()
    app.active_settings.set(DEFAULT_INSTALL_PROFILE, "default")

    root_obj = QtWidgets.QWidget()
    cfr = ConanRef.loads(TEST_REF)

    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)

    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF + ":" + id)
    conan_install_dialog._ui.auto_install_check_box.setCheckState(Qt.CheckState.Checked)
    app_qt_fixture.addWidget(root_obj)
    conan_install_dialog.show()
    app_qt_fixture.waitExposed(conan_install_dialog)

    # check, that there is no option and profile selection and ref line edit is locked
    assert conan_install_dialog._ui.options_widget.isHidden()
    assert conan_install_dialog._ui.set_default_install_profile_button.isHidden()
    assert conan_install_dialog._ui.auto_install_check_box.isHidden()
    assert conan_install_dialog._ui.profile_cbox.isHidden()

    # with update flag
    conan_install_dialog._ui.update_check_box.setCheckState(Qt.CheckState.Checked)
    mock_install_func = mocker.patch(
        'conan_app_launcher.conan_wrapper.conan_worker.ConanWorker.put_ref_in_install_queue')
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF + ":" + id, 
                                                "settings": {}, "profile": "",
                                                "options": {}, "update": True, 
                                                "auto_install": True}

    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # check only ref - new instance needed (other dialog variant)
    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF)
    conan_install_dialog.show()
    app_qt_fixture.waitExposed(conan_install_dialog)

    profile = conan_install_dialog.get_selected_profile()
    assert profile == "default"
    default_options =  {'variant': 'var1', 'shared': "True", 'fPIC2': 'True'}
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {}, "profile": profile,
                                                "options": default_options, "update": False, "auto_install": False}
    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # check ref with autoupdate
    conan_install_dialog._ui.auto_install_check_box.setCheckState(Qt.CheckState.Checked)
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {}, "profile": profile,
                                                "options": {}, "update": False, "auto_install": True}
    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # test option selection
    variant_option = conan_install_dialog._ui.options_widget.topLevelItem(0)
    variant_option.setData(1,0, "MyVariant")
    conan_install_dialog._ui.auto_install_check_box.setCheckState(Qt.CheckState.Unchecked)
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {}, "profile": profile,
                                                "options":  {'variant': 'MyVariant', 'shared': "True", 'fPIC2': 'True'},
                                                  "update": False, "auto_install": False}
    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # Check profile selection

    ## check that profile set default works
    profiles_path = Path(str(app.conan_api._client_cache.default_profile_path)).parent
    new_profile_path = profiles_path / "new_profile"
    new_profile_path.touch()
    conan_install_dialog.load_profiles()

    # default must be fisrt item and has a * after the name
    first_profile = conan_install_dialog._ui.profile_cbox.itemText(0)
    assert first_profile == "default *"
    new_profile_idx = -1
    for i in range(len(app.conan_api.get_profiles())):
        if conan_install_dialog._ui.profile_cbox.itemText(i) == "new_profile":
            new_profile_idx = i
            break
    assert new_profile_idx > 0 # not the default profile
    # select this 
    conan_install_dialog._ui.profile_cbox.setCurrentIndex(new_profile_idx)
    conan_install_dialog.on_set_default_install_profile()

    assert app.active_settings.get_string(DEFAULT_INSTALL_PROFILE) == "new_profile"

    ## remove default selected profile and re-init
    os.remove(new_profile_path)
    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF)
    # noc crash and the first item is default, but with no * (currently no def. inst. prof. set)
    assert conan_install_dialog._ui.profile_cbox.itemText(0) == "default"

    conan_install_dialog.close()

def test_about_dialog(app_qt_fixture, base_fixture):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = AboutPage(root_obj, None)
    app_qt_fixture.addWidget(root_obj)
    widget.show()
    app_qt_fixture.waitExposed(widget)

    assert conan_app_launcher.APP_NAME in widget._ui.about_label.text()


def test_bug_dialog(qtbot, base_fixture, mocker):
    """ Test, that the report generates the dialog correctly and fills out the info """

    # generate a traceback by raising an error
    try:
        raise RuntimeError
    except:
        exc_info = sys.exc_info()

    # mock away dialog OK
    mocker.patch.object(QtWidgets.QDialog, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Ok)

    with pytest.raises(SystemExit) as excinfo:
        # call hook manually
        bug_dialog_exc_hook(*exc_info)
    # check that we got the correct exit value, so the dialog didn't crash
    assert excinfo.value.args == (1,)

    # now check the dialog itself by calling it directly
    dialog = show_bug_reporting_dialog(exc_info[1], exc_info[2])
    browser: QtWidgets.QTextBrowser = dialog.findChild(QtWidgets.QTextBrowser)
    assert "\n".join(traceback.format_tb(exc_info[2], limit=None)) in browser.toPlainText()


def test_get_accent_color(mocker):
    """
    Test, that get_user_theme_color returns black on default and the color on Windows
    in the format #RRGGBB
    """
    if platform.system() == "Windows":
        # Use 4279313508, which is ff112464 -> 642411 (dark red)
        mocker.patch("winreg.QueryValueEx", return_value=["4279313508"])
        color = get_user_theme_color()
        assert color == "#642411"
        # Test invalid registry access
        mocker.patch("winreg.QueryValueEx", side_effect=Exception('mocked error'))
        color = get_user_theme_color()
        assert color == "#000000"
        # Test invalid registry value
        mocker.patch("winreg.QueryValueEx", return_value=["DUMMY"])
        color = get_user_theme_color()
        assert color == "#000000"

    elif platform.system() == "Linux":
        color = get_user_theme_color()
        assert color == "#000000"

def test_remote_url_groups(base_fixture, mocker):
    """ Test, that url groups for remotes are discovered (used in login dialog)
    Currently only for artifactory.
    """
    remote = Remote("test_arti1", 
                    "http://mydomain.com/artifactory/api/conan/conan1", False, False)
    remote2 = Remote("test_arti2", 
                    "http://mydomain.com/artifactory/api/conan/conan2", False, False)
    mocker.patch.object(ConanApi, 'get_remotes', return_value=[remote, remote2])
    remotes = app.conan_api.get_remotes_from_same_server(remote)
    assert remote2 in remotes 
    assert remote in remotes 

def test_multi_remote_login_dialog(app_qt_fixture, base_fixture, mocker):
    """ Test, that on remote login dialog selecting and deselecting remotes work """
    app.conan_api.init_api()
    app.active_settings.set(DEFAULT_INSTALL_PROFILE, "default")
    remote1 = Remote("test_arti1", 
                    "http://mydomain.com/artifactory/api/conan/conan1", False, False)
    remote2 = Remote("test_arti2", 
                    "http://mydomain.com/artifactory/api/conan/conan2", False, False)
    remote3 = Remote("test_arti3", 
                    "http://mydomain.com/artifactory/api/conan/conan3", False, False)
    root_obj = QtWidgets.QWidget()
    mocker.patch.object(ConanApi, 'get_remotes', return_value=[remote1, remote2, remote3])
    login_cmd: Mock = mocker.patch.object(ConanApi, 'login_remote')


    dialog = RemoteLoginDialog([remote1, remote2, remote3], root_obj)
    username = "user"
    password = "pw"
    dialog._ui.name_line_edit.setText(username)
    dialog._ui.password_line_edit.setText(password)

    app_qt_fixture.addWidget(root_obj)
    dialog.show()
    app_qt_fixture.waitExposed(dialog)
    # uncheck remote3
    dialog._ui.remote_list.item(2).setCheckState(Qt.CheckState.Unchecked)
    # Press Ok in dialog
    dialog.on_ok()
    calls = [mocker.call("test_arti1", username, password),
            mocker.call("test_arti2", username, password)]
    login_cmd.assert_has_calls(calls, any_order=True)

    dialog.close()
