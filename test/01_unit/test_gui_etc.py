"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
import sys
import traceback
from test.conftest import TEST_REF
from time import sleep

import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
import pytest
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.dialogs.about_dialog import AboutDialog
from conan_app_launcher.ui.dialogs.bug_dialog import (bug_reporting_dialog,
                                                      show_bug_dialog_exc_hook)
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog
from conan_app_launcher.ui.dialogs.conan_search import ConanSearchDialog
from conan_app_launcher.ui.main_window import MainWindow
from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_edit_line_conan(base_fixture, light_theme_fixture, qtbot):
    """ Test, that the line edit validates on edit
    and displays the local packages instantly and the remote ones after a delay
    """
    os.system(f"conan remove {TEST_REF} -f")
    root_obj = QtWidgets.QWidget()
    widget = ConanRefLineEdit(root_obj)
    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)
    # test recipe ref without revision
    widget.setText(TEST_REF)
    assert ConanRefLineEdit.VALID_COLOR_LIGHT in widget.styleSheet()
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
    # test autocompletion (very implicit)
    widget._completion_thread.join()
    assert TEST_REF in widget._remote_refs


def test_conan_install_dialog(base_fixture, qtbot, mocker):
    """ 
    Tests, that the Conan Install dialog can install references, packages and the update and auto_install flag works.
    """
    root_obj = QtWidgets.QWidget()
    cfr = ConanFileReference.loads(TEST_REF)

    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)

    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF + ":" + id)
    qtbot.addWidget(root_obj)
    conan_install_dialog.show()
    qtbot.waitExposed(conan_install_dialog)

    # with update flag
    conan_install_dialog.update_check_box.setCheckState(Qt.Checked)
    mock_install_func = mocker.patch(
        'conan_app_launcher.core.conan_worker.ConanWorker.put_ref_in_install_queue')
    conan_install_dialog.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF + ":" + id, "settings": {},
                                                "options": {}, "update": True, "auto_install": False}

    mock_install_func.assert_called_with(conan_worker_element, None)

    # check only ref
    conan_install_dialog.update_check_box.setCheckState(Qt.Unchecked)
    conan_install_dialog.conan_ref_line_edit.setText(TEST_REF)
    conan_install_dialog.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": False, "auto_install": False}
    mock_install_func.assert_called_with(conan_worker_element, None)

    # check ref with autoupdate
    conan_install_dialog.auto_install_check_box.setCheckState(Qt.Checked)
    conan_install_dialog.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": True, "auto_install": True}


def test_conan_search_dialog(base_fixture, qtbot, mock_clipboard, mocker):
    """ Tests, that the Conan search dialog:
    - search button does not work under 3 characters
    - can find the test packages from the name
    - installed packages/pkgs have the correct internal flag
    - After item expansion, the pkgs are shown
    Context menu actions work:
    - Copy ref and pkg
    - Install dialog call
    - Show conanfile call
    - Show in Local Package Explorer
    """
    cfr = ConanFileReference.loads(TEST_REF)
    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    from pytestqt.plugin import _qapp_instance
    root_obj = QtWidgets.QWidget()
    search_dialog = ConanSearchDialog(root_obj, MainWindow(_qapp_instance))

    qtbot.addWidget(root_obj)
    search_dialog.show()
    qtbot.waitExposed(search_dialog)

    # enter short search term -> search button disabled
    search_dialog._ui.search_line.setText("ex")
    assert not search_dialog._ui.search_button.isEnabled()

    # search for the test ref name: example -> 2 versions
    search_dialog._ui.search_line.setText("example")
    assert search_dialog._ui.search_button.isEnabled()
    search_dialog._ui.search_button.clicked.emit()

    # wait for loading
    search_dialog._pkg_result_loader.wait_for_finished()

    # assert basic view
    model = search_dialog._pkg_result_model
    assert model
    assert search_dialog._ui.search_results_tree_view.findChildren(QtCore.QObject)
    assert search_dialog._ui.search_results_tree_view.model().columnCount() == 3  # fixed 3 coloumns

    assert model.root_item.item_data[0] == "Packages"
    assert model.root_item.child_count() == 3

    # expand package -> assert number of packages and itemdata
    # check installed ref ist highlighted

    ref_item = model.get_item_from_ref(TEST_REF)
    assert ref_item
    assert ref_item.is_installed
    index = model.get_index_from_item(ref_item)
    proxy_view_model = search_dialog._ui.search_results_tree_view.model()
    ref_view_index = proxy_view_model.mapFromSource(index)
    search_dialog._ui.search_results_tree_view.expand(ref_view_index)

    while not ref_item.child_items:
        _qapp_instance.processEvents()
    # check in child items that installed pkg id is highlighted
    pkg_found = False
    for child_item in ref_item.child_items:
        if child_item.get_conan_ref() == TEST_REF + ":" + id:
            pkg_found = True
            assert child_item.is_installed
            break
    assert pkg_found
    pkg_view_index = proxy_view_model.mapFromSource(model.get_index_from_item(child_item))

    # check context menu actions
    # check copy recipe ref
    # select ref
    sel_model = search_dialog._ui.search_results_tree_view.selectionModel()
    sel_model.select(ref_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    search_dialog.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF)

    # check copy id ref
    # select id
    sel_model.select(pkg_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    search_dialog.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF + ":" + id)

    # check install
    mock_install_dialog = mocker.patch(
        "conan_app_launcher.ui.dialogs.conan_search.conan_search.ConanInstallDialog")
    search_dialog.on_install_pkg_requested()
    mock_install_dialog.assert_called_with(search_dialog, TEST_REF + ":" + id, search_dialog._main_window.conan_pkg_installed)

    # check show conanfile
    mock_open_file = mocker.patch(
        "conan_app_launcher.ui.dialogs.conan_search.conan_search.open_file")
    search_dialog.on_show_conanfile_requested()
    conanfile = app.conan_api.get_export_folder(cfr) / "conanfile.py"
    mock_open_file.assert_called_with(conanfile)

    # check check open in local pkg explorer
    search_dialog.on_show_in_pkg_exp()
    assert id == search_dialog._main_window.local_package_explorer.get_selected_conan_pkg_info().get("id", "")

    search_dialog.hide()


def test_about_dialog(base_fixture, qtbot):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = AboutDialog(root_obj)
    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)

    assert "Conan App Launcher" in widget._text.text()
    qtbot.mouseClick(widget._button_box.buttons()[0], Qt.LeftButton)
    assert widget.isHidden()


def test_bug_dialog(base_fixture, qtbot, mocker):
    """ Test, that the report generates the dialog correctly and fills out the info """

    # generate a traceback by raising an error
    try:
        raise RuntimeError
    except:
        exc_info = sys.exc_info()

    # mock away dialog OK
    mocker.patch.object(QtWidgets.QMessageBox, 'exec_',
                        return_value=QtWidgets.QMessageBox.Ok)

    with pytest.raises(SystemExit) as excinfo:
        # call hook manually
        show_bug_dialog_exc_hook(*exc_info)
    # check that we got the correct exit value, so the dialog didn't crash
    assert excinfo.value.args == (1,)

    # now check the dialog itself by calling it directly
    dialog = bug_reporting_dialog(exc_info[1], exc_info[2])
    assert dialog.text()
    assert "\n".join(traceback.format_tb(exc_info[2], limit=None)) in dialog.detailedText()
