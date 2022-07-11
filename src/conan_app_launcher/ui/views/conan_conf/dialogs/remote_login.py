
from pathlib import Path
from typing import Optional

from conan_app_launcher import asset_path
from conan_app_launcher.ui.views.app_grid.model import UiTabModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtGui import QIcon

from .remote_login_dialog_ui import Ui_Dialog

current_dir = Path(__file__).parent


class RemoteLoginDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(asset_path / "icons" / "edit.png")))
        self._ui.button_box.accepted.connect(self.save)

    def save(self):
        self.accept()

