from .conan_line_edit import ConanRefLineEdit
from .clickable_icon import ClickableIcon
from .toggle import AnimatedToggle

from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt

class RoundedMenu(QMenu):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
