"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
from time import time
import traceback
import pytest
import os

from conan_app_launcher.ui.modules.conan_search import ConanSearchDialog
from conan_app_launcher.ui.modules.about_dialog import AboutDialog
from conan_app_launcher.ui.modules.conan_install import ConanInstallDialog
from conan_app_launcher.ui.common.conan_line_edit import ConanRefLineEdit
from conan_app_launcher.ui.common.bug_dialog import show_bug_dialog_exc_hook, bug_reporting_dialog
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt
from test.conftest import TEST_REF

def test_edit_line_conan(base_fixture, qtbot):
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
    assert "Green" in widget.styleSheet()
    # test package ref with revision
    widget.setText(TEST_REF + ":127af201a4cdf8111e2e08540525c245c9b3b99e")
    assert "Green" in widget.styleSheet()
    # test wrong recipe
    widget.setText("zlib/1.2.8@@")
    assert "Coral" in widget.styleSheet()
    # test validator disabled - color doesn't change on correct
    widget.validator_enabled = False
    widget.setText("zlib/1.2.8")
    assert "Coral" in widget.styleSheet()
    # test autocompletion (very implicit)
    widget._completion_thread.join()
    assert TEST_REF in widget._remote_refs

def test_conan_install_dialog(base_fixture, qtbot):
    root_obj = QtWidgets.QWidget()
    widget = ConanInstallDialog(root_obj, TEST_REF + ":127af201a4cdf8111e2e08540525c245c9b3b99e")
    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)
    # TODO mock away conan calls
    # from pytestqt.plugin import _qapp_instance
    # while True:
    #    _qapp_instance.processEvents()


def test_conan_search_dialog(base_fixture, qtbot):
    from pytestqt.plugin import _qapp_instance
    root_obj = QtWidgets.QWidget()
    widget = ConanSearchDialog(root_obj)

    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)

    widget._ui.search_line.setText("zlib")
    widget._ui.search_button.clicked.emit()

    while not widget._pkg_result_loader.load_thread:
        time.sleep(1)
    while not widget._pkg_result_loader.load_thread.isFinished():
       _qapp_instance.processEvents()

    model = widget._pkg_result_model
    assert model
    assert widget._ui.search_results_tree_view.findChildren(QtCore.QObject)
    assert widget._ui.search_results_tree_view.model().columnCount() == 3

    #model.root_item.item_data[0] == "Packages"
    #model.root_item.child_count() == widget._ui.package_select_view.model().rowCount()

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

