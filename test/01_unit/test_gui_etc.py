"""
Test the self written qt gui base, which can be instantiated without
using the whole application (standalone).
"""
import os
import platform
import sys
import traceback
from conan_app_launcher.ui.common.theming import get_user_theme_color
from test.conftest import TEST_REF, app_qt_fixture

import conan_app_launcher  # for mocker
import conan_app_launcher.app as app
import pytest
from conan_app_launcher.core.conan_worker import ConanWorkerElement
from conan_app_launcher.ui.views.about_page import AboutPage
from conan_app_launcher.ui.dialogs.bug_dialog import (bug_reporting_dialog,
                                                      show_bug_dialog_exc_hook)
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog
from conan_app_launcher.ui.widgets.conan_line_edit import ConanRefLineEdit
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_edit_line_conan(app_qt_fixture, base_fixture, light_theme_fixture):
    """ Test, that the line edit validates on edit
    and displays the local packages instantly and the remote ones after a delay
    """
    os.system(f"conan remove {TEST_REF} -f")
    root_obj = QtWidgets.QWidget()
    widget = ConanRefLineEdit(root_obj)
    app_qt_fixture.addWidget(root_obj)
    widget.show()
    app_qt_fixture.waitExposed(widget)
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
    widget._completion_thread.join(10)
    assert TEST_REF in widget._remote_refs
    widget.close()


def test_conan_install_dialog(app_qt_fixture, base_fixture, mocker):
    """ 
    Tests, that the Conan Install dialog can install references, packages and the update and auto_install flag works.
    """
    app.conan_api.init_api()

    root_obj = QtWidgets.QWidget()
    cfr = ConanFileReference.loads(TEST_REF)

    # first with ref + id in constructor
    id, pkg_path = app.conan_api.install_best_matching_package(cfr)

    conan_install_dialog = ConanInstallDialog(root_obj, TEST_REF + ":" + id)
    app_qt_fixture.addWidget(root_obj)
    conan_install_dialog.show()
    app_qt_fixture.waitExposed(conan_install_dialog)

    # with update flag
    conan_install_dialog._ui.update_check_box.setCheckState(Qt.Checked)
    mock_install_func = mocker.patch(
        'conan_app_launcher.core.conan_worker.ConanWorker.put_ref_in_install_queue')
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF + ":" + id, "settings": {},
                                                "options": {}, "update": True, "auto_install": True}

    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # check only ref
    conan_install_dialog._ui.update_check_box.setCheckState(Qt.Unchecked)
    conan_install_dialog._ui.conan_ref_line_edit.setText(TEST_REF)
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": False, "auto_install": True}
    mock_install_func.assert_called_with(conan_worker_element, conan_install_dialog.emit_conan_pkg_signal_callback)

    # check ref without autoupdate
    conan_install_dialog._ui.auto_install_check_box.setCheckState(Qt.Unchecked)
    conan_install_dialog._ui.button_box.accepted.emit()
    conan_worker_element: ConanWorkerElement = {"ref_pkg_id": TEST_REF, "settings": {},
                                                "options": {}, "update": True, "auto_install": False}
    conan_install_dialog.close()


def test_about_dialog(app_qt_fixture, base_fixture):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = AboutPage(root_obj)
    app_qt_fixture.addWidget(root_obj)
    widget.show()
    app_qt_fixture.waitExposed(widget)

    assert "Conan App Launcher" in widget._text.text()


def test_bug_dialog(qtbot, base_fixture, mocker):
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

