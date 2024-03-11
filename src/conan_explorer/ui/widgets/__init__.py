from .conan_line_edit import ConanRefLineEdit
from .clickable_icon import ClickableIcon
from .toggle import AnimatedToggle
from .text_broswer import PlainTextPasteBrowser

from PySide6.QtWidgets import QMessageBox

class WideMessageBox(QMessageBox):
    """ MessageBox with more width """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._width = 600   # default

    def setWidth(self, width):
        self._width = width

    def resizeEvent(self, event):
        _result = super().resizeEvent(event)

        self.setFixedWidth(self._width)
        return _result
