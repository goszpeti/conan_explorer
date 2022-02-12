"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
from test.conftest import TEST_REF
from time import time
import traceback
import pytest
import os
import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
from conans.model.ref import ConanFileReference

from conan_app_launcher.ui.modules.conan_search import ConanSearchDialog
from conan_app_launcher.ui.modules.about_dialog import AboutDialog
from conan_app_launcher.ui.modules.conan_install import ConanInstallDialog
from conan_app_launcher.ui.common.conan_line_edit import ConanRefLineEdit
from conan_app_launcher.ui.common.bug_dialog import show_bug_dialog_exc_hook, bug_reporting_dialog
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
    mocker.patch('conan_app_launcher.core.conan.ConanApi.install_package')
    widget.button_box.accepted.emit()

    conan_app_launcher.core.conan.ConanApi.install_package.assert_called_once()
    assert widget.pkg_installed == id

    # check only ref

    widget.pkg_installed = ""
    widget.conan_ref_line_edit.setText(TEST_REF)

    import conans
    mocker.patch('conans.client.conan_api.ConanAPIV1.install_reference', return_value={
                 "error": False, "installed": [{"packages": [{"id": id}]}]})
    widget.button_box.accepted.emit()
    conans.client.conan_api.ConanAPIV1.install_reference.assert_called_once_with(
        cfr, update=True)
    assert widget.pkg_installed == id

    # check ref with autoupdate
    widget.pkg_installed = ""
    widget.auto_install_check_box.setCheckState(Qt.Checked)
    mocker.patch('conan_app_launcher.core.conan.ConanApi.install_best_matching_package',
                 return_value=(id, pkg_path))
    widget.button_box.accepted.emit()
    conan_app_launcher.core.conan.ConanApi.install_best_matching_package.assert_called_once_with(
        cfr, update=True)
    assert widget.pkg_installed == id


def test_conan_search_dialog(base_fixture, qtbot):
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
        time.sleep(1)
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
    # check installed pkg ist highlited

    # check context menu actions
    # check copy recipe ref
    # check copy id ref
    # check install
    # check show conanfile
    # check check open in local pkg explorer

    # found_tst_pkg = False
    # for pkg in model.root_item.child_items:
    #     if pkg.item_data[0] == str(cfr):
    #         found_tst_pkg = True
    #         # check it's child
    #         assert model.get_quick_profile_name(pkg.child(0)) in [
    #             "Windows_x64_vs16_release", "Linux_x64_gcc9_release"]
    # from pytestqt.plugin import _qapp_instance
    # while True:
    #    _qapp_instance.processEvents()


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
