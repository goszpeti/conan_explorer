from conan_app_launcher import AUTHOR, REPO_URL, __version__, asset_path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFrame, QLabel, QSizePolicy, QSpacerItem,
                             QVBoxLayout, QWidget)
from conan_app_launcher.ui.fluent_window.plugins import PluginInterface

from .plugins_ui import Ui_Form

class PluginsPage(PluginInterface):

    def __init__(self, parent):
        super().__init__(parent)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
