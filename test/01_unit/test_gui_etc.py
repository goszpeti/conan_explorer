"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
from datetime import datetime, timedelta
import os
import platform
import sys
import traceback
from pathlib import Path
from conan_explorer.ui.dialogs.pkg_diff.diff import ConfigDiffHighlighter, PkgDiffDialog
from conan_explorer.ui.views.conan_conf.editable_controller import ConanEditableController
from conan_explorer.ui.views.conan_conf.remotes_controller import ConanRemoteController
from test.conftest import TEST_REF, PathSetup, conan_remove_ref
from unittest.mock import Mock

import pytest
from pytest_check import check
from PySide6 import QtCore, QtGui, QtWidgets

import conan_explorer  # for mocker
import conan_explorer.app as app
from conan_explorer import conan_version
from conan_explorer.app import bug_dialog_exc_hook
from conan_explorer.conan_wrapper.conan_worker import ConanWorkerElement
from conan_explorer.conan_wrapper.conanV1 import ConanApi
from conan_explorer.conan_wrapper.types import ConanPkg, ConanRef, Remote
from conan_explorer.settings import DEFAULT_INSTALL_PROFILE, FILE_EDITOR_EXECUTABLE
from conan_explorer.ui.common.theming import get_user_theme_color
from conan_explorer.ui.dialogs import FileEditorSelDialog, show_bug_reporting_dialog
from conan_explorer.ui.dialogs.conan_install import ConanInstallDialog
from conan_explorer.ui.views import AboutPage
from conan_explorer.ui.views.conan_conf.dialogs.editable_edit_dialog import \
    EditableEditDialog
from conan_explorer.ui.views.conan_conf.dialogs.remote_login_dialog import \
    RemoteLoginDialog
from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit

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
        'conan_explorer.conan_wrapper.conan_worker.ConanWorker.put_ref_in_install_queue')
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
    profiles_path = app.conan_api.get_profiles_path()
    new_profile_path = profiles_path / "new_profile"
    new_profile_path.touch()
    conan_install_dialog.load_profiles()
    # default must be first item and has a * after the name
    # TODO: is abc ordered, so this does not work always...
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

def test_install_dialog_diff_open_on_failure_to_install(app_qt_fixture, base_fixture, mocker):
    """ 
    Tests, that the Conan Install dialog spawns a Pkg diff dialog with the 
    all the refs loaded from the server.
    """
    app.conan_api.init_api()
    app.active_settings.set(DEFAULT_INSTALL_PROFILE, "default")

    root_obj = QtWidgets.QWidget()
    
    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF)

    variant_option = conan_install_dialog._ui.options_widget.topLevelItem(0)
    variant_option.setData(1, 0, "MyVariant")

    mocker.patch.object(QtWidgets.QMessageBox, 'exec',
                        return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    conan_install_dialog._ui.button_box.accepted.emit()

    # wait for dialog to pop up
    from pytestqt.plugin import _qapp_instance
    start_time = datetime.now() 
    while (len(root_obj.children()) < 2 and
        datetime.now() - start_time < timedelta(seconds=20)):
         _qapp_instance.processEvents()

    # pkg diff dialog is now child of root object
    pkg_diff_dlg: PkgDiffDialog = root_obj.children()[1]
    assert pkg_diff_dlg.isVisible()

    # check wanted ref item is first and has * in name
    assert "* User input" == pkg_diff_dlg._ui.pkgs_list_widget.item(0).data(0)
    assert 5 == pkg_diff_dlg._ui.pkgs_list_widget.count()
    # check that it is displayed in the left window
    left_content = pkg_diff_dlg._ui.left_text_browser.toPlainText()
    check_dict_value_in_text(
        left_content, conan_install_dialog._conan_selected_install['options'])

    pkg_diff_dlg.close()


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

    assert conan_explorer.APP_NAME in widget._ui.about_label.text()


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
    ConanApiActual = ConanApi
    if conan_version.major == 2:
        from conan_explorer.conan_wrapper.conanV2 import ConanApi as ConanApiV2
        ConanApiActual = ConanApiV2
    mocker.patch.object(ConanApiActual, 'get_remotes', return_value=[remote, remote2])
    remotes = app.conan_api.get_remotes_from_same_server(remote)
    assert remote2 in remotes 
    assert remote in remotes 

@pytest.mark.conanv2
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
    ConanApiActual = ConanApi
    if conan_version.major == 2:
        from conan_explorer.conan_wrapper.conanV2 import ConanApi as ConanApiV2
        ConanApiActual = ConanApiV2
    mocker.patch.object(ConanApiActual, 'get_remotes',
                        return_value=[remote1, remote2, remote3])
    login_cmd: Mock = mocker.patch.object(ConanApiActual, 'login_remote')
    controller = ConanRemoteController(QtWidgets.QTreeView(), None)
    dialog = RemoteLoginDialog([remote1, remote2, remote3], controller, root_obj)
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

@pytest.mark.conanv2
def test_editable_dialog(app_qt_fixture, base_fixture: PathSetup, mocker):
    """ Test, that the editable dialog works adding and editing """
    app.conan_api.init_api()
    root_obj = QtWidgets.QWidget()
    editable_controller = ConanEditableController(QtWidgets.QTreeView())
    dialog = EditableEditDialog(None, editable_controller, root_obj)

    new_ref = "example/9.9.9@editable/testing1"
    new_ref_obj = ConanRef.loads(new_ref)
    app.conan_api.remove_editable(new_ref_obj) # remove, if somehow already there
    app.conan_api.remove_editable(ConanRef.loads(new_ref + "new"))

    app_qt_fixture.addWidget(root_obj)
    dialog.show()
    app_qt_fixture.waitExposed(dialog)

    dialog._ui.name_line_edit.setText(new_ref)

    new_editable_path = base_fixture.testdata_path / "conan"
    if conan_version.major == 2:
        new_editable_path /= "conanfileV2.py"
    new_output_folder_path = base_fixture.testdata_path / "conan" / "build"

    # check browse buttons
    mocker.patch.object(QtWidgets.QFileDialog, 'exec',
                        return_value=QtWidgets.QDialog.DialogCode.Accepted)
    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(new_output_folder_path)])
    dialog._ui.output_folder_browse_button.click()
    assert Path(dialog._ui.output_folder_line_edit.text()) == new_output_folder_path


    mocker.patch.object(QtWidgets.QFileDialog, 'selectedFiles',
                        return_value=[str(new_editable_path)])
    dialog._ui.path_browse_button.click()
    assert Path(dialog._ui.path_line_edit.text()) == new_editable_path

    dialog.save()

    if conan_version.major == 1:
        assert app.conan_api.get_editables_package_path(new_ref_obj).parent == new_editable_path
    if conan_version.major == 2:
        assert app.conan_api.get_editables_package_path(new_ref_obj) == new_editable_path

    assert app.conan_api.get_editables_output_folder(
        new_ref_obj) == new_output_folder_path

    ### check on erronous input - values should remain the same
    # check wrong ref -> old one should remain
    dialog._ui.name_line_edit.setText("lalala")
    dialog.save()
    assert new_ref_obj in app.conan_api.get_editable_references()
    dialog._ui.name_line_edit.setText(new_ref)

    # check wrong path
    dialog._ui.path_line_edit.setText("INVALID")
    dialog.save()
    assert new_ref_obj in app.conan_api.get_editable_references()
    if conan_version.major == 1:
        assert app.conan_api.get_editables_package_path(new_ref_obj).parent == new_editable_path
    if conan_version.major == 2:
        assert app.conan_api.get_editables_package_path(new_ref_obj) == new_editable_path
    dialog._ui.path_line_edit.setText(str(new_editable_path))

    # check changing the output path of an already existing editable
    dialog._ui.output_folder_line_edit.setText(str(base_fixture.testdata_path / "conan" / "build_new"))
    dialog.save()
    assert base_fixture.testdata_path / "conan" / "build_new" == app.conan_api.get_editables_output_folder(new_ref_obj)

    # check changing the ref of an already existing editable
    editable_controller._select_editable(new_ref)
    dialog._editable = editable_controller.get_selected_editable()
    dialog._ui.name_line_edit.setText(new_ref + "new")
    dialog.save()
    assert ConanRef.loads(new_ref + "new") in app.conan_api.get_editable_references()
    assert new_ref_obj not in app.conan_api.get_editable_references()

def check_dict_value_in_text(text, dict_to_check):
    for key, value in dict_to_check.items():
        assert f"{key}: {value}" in text

def check_color_in_document(doc, word_to_check, color):
    idx = doc.toPlainText().find(word_to_check)
    format_ranges = doc.findBlock(idx).layout().formats()
    for format_range in format_ranges:
        with check:
            assert format_range.format.background().color() == color

@pytest.mark.conanv2
def test_conan_diff_dialog(app_qt_fixture, base_fixture: PathSetup, mocker):
    """ Test, that the diff dialog works """
    root_obj = QtWidgets.QWidget()
    server_ref_1: ConanPkg = {'id': '02356509d9a0879a1cecc67cf273cd8d7638a142', 
        'options': {'fPIC2': 'True', 'shared': 'True', 'variant': 'var1'}, 
        'settings': {'arch': 'x86_64',
        'build_type': 'Release', 'compiler': 'gcc', 'compiler.libcxx': 'libstdc++11', 
        'compiler.version': '9', 'os': 'Linux'}, 'requires': [], 'outdated': False}
    server_ref_2: ConanPkg = {'id': '7836e0c4e7632db749e0dafcb4aed62ba225b99b', 
        'options': {'fPIC2': 'True', 'shared': 'True', 'variant': 'var1'}, 
        'settings': {'arch': 'x86_64',
        'build_type': 'Release', 'compiler': 'Visual Studio', 'compiler.runtime': 'MD', 
        'compiler.version': '16', 'os': 'Windows'}, 'requires': [], 'outdated': False}

    #conan.get_remote_pkgs_from_ref(ConanRef.loads(TEST_REF), None)
    wanted_ref: ConanPkg = {  # add default options
        'id': 'MyId', 'options': {"shared": "False", "variant": "var1", "fPIC2": "True"},
        'settings': {'arch_build': 'x86_64', 'os_build': 'Linux', "build_type": "Release"},
        'requires': [], 'outdated': False}
    dialog = PkgDiffDialog(root_obj)
    dialog.add_diff_item(wanted_ref)
    dialog.add_diff_item(server_ref_1)
    dialog.add_diff_item(server_ref_2)
    dialog.show()
    app_qt_fixture.waitExposed(dialog)

    # check wanted ref item is first and has * in name
    assert "* MyId" == dialog._ui.pkgs_list_widget.item(0).data(0)

    # check that it is displayed in the left window
    left_content = dialog._ui.left_text_browser.toPlainText()
    assert "id:" not in left_content # hide id
    check_dict_value_in_text(left_content, wanted_ref["options"])
    check_dict_value_in_text(left_content, wanted_ref["settings"])

    # check that 2nd item is selected per default and is dispalyed in right window
    assert dialog._ui.pkgs_list_widget.currentRow() == 1
    right_content = dialog._ui.right_text_browser.toPlainText()

    check_dict_value_in_text(right_content, server_ref_1["options"])
    check_dict_value_in_text(right_content, server_ref_1["settings"])

    ### check the diff colors ###
    # use colors from the class
    rem_color = ConfigDiffHighlighter.DIFF_REMOVED_COLOR
    mod_color = ConfigDiffHighlighter.DIFF_MODIFIED_COLOR
    new_color = ConfigDiffHighlighter.DIFF_NEW_COLOR

    # check that shared is orange in both
    check_color_in_document(dialog._ui.left_text_browser.document(), "shared", mod_color)
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "shared", mod_color)

    # check that arch_build and os_build is red in left
    check_color_in_document(
        dialog._ui.left_text_browser.document(), "arch_build", rem_color)
    check_color_in_document(
        dialog._ui.left_text_browser.document(), "os_build", rem_color)

    # check that arch, compiler, c.version and os is green in right
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "arch", new_color)
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "compiler", new_color)
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "compiler.version", new_color)
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "os", new_color)

    # check selecting the 3rd ref changes and redraws right window
    dialog._ui.pkgs_list_widget.setCurrentRow(2)
    assert "Windows" in dialog._ui.right_text_browser.toPlainText()
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "compiler.runtime", new_color)

    # check that select ref sets the * and changes the left window
    dialog._set_ref_item()
    assert "* " + server_ref_2["id"] == dialog._ui.pkgs_list_widget.item(0).data(0)

    # check that there are no diffs marked, when comparing against themselves
    dialog._ui.pkgs_list_widget.setCurrentRow(0)
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "shared", QtGui.QColor("black"))
    check_color_in_document(
        dialog._ui.right_text_browser.document(), "os", QtGui.QColor("black"))
    
    # from pytestqt.plugin import _qapp_instance
    # while True:
    #     _qapp_instance.processEvents()

