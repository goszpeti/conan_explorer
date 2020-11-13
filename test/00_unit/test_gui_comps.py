"""
These tests test the self written qt gui components.
"""


from conan_app_launcher.base import Logger
from conan_app_launcher.ui import main_ui
from PyQt5 import QtCore, QtWidgets


def testAboutDialog(base_fixture, qtbot):
    logger = Logger()  # init logger
    root_obj = QtWidgets.QWidget()
    widget = main_ui.AboutDialog(root_obj)
    widget.show()
    qtbot.addWidget(widget)
    qtbot.waitForWindowShown(widget)

    assert "Conan App Launcher" in widget._text.text()
    qtbot.mouseClick(widget._button_box.buttons()[0], QtCore.Qt.LeftButton)
    assert widget.isHidden()
