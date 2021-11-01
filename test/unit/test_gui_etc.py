"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
from conan_app_launcher.ui import main_window
from PyQt5 import QtCore, QtWidgets


Qt = QtCore.Qt

def testAboutDialog(base_fixture, qtbot):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    root_obj = QtWidgets.QWidget()
    widget = main_window.AboutDialog(root_obj)
    qtbot.addWidget(root_obj)
    widget.show()
    qtbot.waitExposed(widget)

    assert "Conan App Launcher" in widget._text.toPlainText()
    qtbot.mouseClick(widget._button_box.buttons()[0], Qt.LeftButton)
    assert widget.isHidden()

# testBugReport


# test_edit_line_conan