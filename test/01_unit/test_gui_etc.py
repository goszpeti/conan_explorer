"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
import traceback
from test.conftest import TEST_REF
from time import sleep

import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
import pytest
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.dialogs.bug_dialog import (bug_reporting_dialog,
                                                     show_bug_dialog_exc_hook)
from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit
from conan_app_launcher.ui.dialogs.about_dialog import AboutDialog
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog
from conan_app_launcher.ui.dialogs.conan_search import ConanSearchDialog
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
    root_obj = QtWidgets.QWidget()
    cfr = ConanFileReference.loads(TEST_REF)

    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)

    widget = ConanInstallDialog(root_obj, TEST_REF + ":" + id)
    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)

    # with update flag
    widget.update_check_box.setCheckState(Qt.Checked)
    mock_install_func = mocker.patch(
        'conan_app_launcher.core.conan_worker.ConanWorker.put_ref_in_install_queue')
    widget.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF + ":" + id, "settings": {},
                                                "options": {}, "update": True, "auto_install": False}

    mock_install_func.assert_called_with(conan_worker_element, None)

    # check only ref

    widget.conan_ref_line_edit.setText(TEST_REF)
    widget.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": True, "auto_install": False}
    mock_install_func.assert_called_with(conan_worker_element, None)

    # check ref with autoupdate
    widget.auto_install_check_box.setCheckState(Qt.Checked)
    widget.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": True, "auto_install": True}


def test_conan_search_dialog(base_fixture, qtbot, mock_clipboard, mocker):
    cfr = ConanFileReference.loads(TEST_REF)
    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)
    from pytestqt.plugin import _qapp_instance
    root_obj = QtWidgets.QWidget()
    widget = ConanSearchDialog(root_obj)

    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)

    # enter short search term -> search button disabled
    widget._ui.search_line.setText("ex")
    assert not widget._ui.search_button.isEnabled()

    # search for the test ref name: example -> 2 versions

    widget._ui.search_line.setText("example")
    assert widget._ui.search_button.isEnabled()
    widget._ui.search_button.clicked.emit()

    # wait for loading
    while not widget._pkg_result_loader.load_thread:
        sleep(1)
    while not widget._pkg_result_loader.load_thread.isFinished():
        _qapp_instance.processEvents()

    # assert basic view
    model = widget._pkg_result_model
    assert model
    assert widget._ui.search_results_tree_view.findChildren(QtCore.QObject)
    assert widget._ui.search_results_tree_view.model().columnCount() == 3  # fixed 3 coloumns

    assert model.root_item.item_data[0] == "Packages"
    assert model.root_item.child_count() == 3

    # expand package -> assert number of packages and itemdata
    # check installed ref ist highlighted

    ref_item = model.get_item_from_ref(TEST_REF)
    assert ref_item
    assert ref_item.is_installed
    index = model.get_index_from_item(ref_item)
    proxy_view_model = widget._ui.search_results_tree_view.model()
    ref_view_index = proxy_view_model.mapFromSource(index)
    widget._ui.search_results_tree_view.expand(ref_view_index)

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
    sel_model = widget._ui.search_results_tree_view.selectionModel()
    sel_model.select(ref_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    widget.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF)

    # check copy id ref
    # select id
    sel_model.select(pkg_view_index, QtCore.QItemSelectionModel.ClearAndSelect)
    widget.on_copy_ref_requested()
    mock_clipboard.setText.assert_called_with(TEST_REF + ":" + id)

    # check install
    # TODO

    # check show conanfile
    # TODO

    # check check open in local pkg explorer
    # TODO

    widget.hide()


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

    # qtbot.addWidget(main_gui)
    # qtbot.waitExposed(main_gui, timeout=3000)
    import sys

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
