"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
import traceback
import pytest
from conan_app_launcher.ui.modules.conan_search import ConanSearchDialog
from conan_app_launcher.ui.modules.about_dialog import AboutDialog
from conan_app_launcher.ui.common.bug_dialog import show_bug_dialog_exc_hook, bug_reporting_dialog
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt


def test_edit_line_conan():
    """ Test, that the line edit validates on edit 
    and displays the local packages instantly and the remote ones after a delay
    """
    # TODO


def test_conan_search_dialog(base_fixture, qtbot):
    root_obj = QtWidgets.QWidget()
    widget = ConanSearchDialog(root_obj)

    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)
    from pytestqt.plugin import _qapp_instance
    while True:
       _qapp_instance.processEvents()


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

