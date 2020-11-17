"""
These tests test the self written qt gui components.
"""


from conan_app_launcher.base import Logger
from conan_app_launcher.ui import main_ui
from PyQt5 import QtCore, QtWidgets


def testAboutDialog(base_fixture, qtbot):
    """
    Test the about dialog separately.
    Check, that the app name is visible and it is hidden after clicking OK:
    """
    logger = Logger()  # init logger
    root_obj = QtWidgets.QWidget()
    widget = main_ui.AboutDialog(root_obj)
    widget.show()
    qtbot.addWidget(widget)
    qtbot.waitForWindowShown(widget)

    assert "Conan App Launcher" in widget._text.text()
    qtbot.mouseClick(widget._button_box.buttons()[0], QtCore.Qt.LeftButton)
    assert widget.isHidden()

# TODO TEST show view channel and version
