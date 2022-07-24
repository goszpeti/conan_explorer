from .conan_line_edit import ConanRefLineEdit
from .clickable_icon import ClickableIcon
from .toggle import AnimatedToggle

from PyQt5.QtWidgets import QMenu, QMessageBox
from PyQt5.QtCore import Qt

class RoundedMenu(QMenu):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


class WideMessageBox(QMessageBox):
    """ MessageBox with more width """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._width = 150   # default

    def setWidth(self, width):
        self._width = width

    def resizeEvent(self, event):
        _result = super().resizeEvent(event)

        self.setFixedWidth(self._width)

        return _result
