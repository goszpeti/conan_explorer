"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
from datetime import datetime, timedelta
from test.conftest import TEST_REF, conan_remove_ref

import conan_explorer  # for mocker
import conan_explorer.app as app
import pytest
from conan_explorer.conan_wrapper.conan_worker import ConanWorkerElement
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer.settings import DEFAULT_INSTALL_PROFILE
from conan_explorer.ui.dialogs.conan_install import ConanInstallDialog
from conan_explorer.ui.dialogs.pkg_diff.diff import PkgDiffDialog
from conan_explorer.ui.widgets.conan_line_edit import ConanRefLineEdit
from PySide6 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
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
    # is abc ordered, so this does not work always...
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


def check_dict_value_in_text(text, dict_to_check):
    for key, value in dict_to_check.items():
        assert f"{key}: {value}" in text

@pytest.mark.conanv2
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

