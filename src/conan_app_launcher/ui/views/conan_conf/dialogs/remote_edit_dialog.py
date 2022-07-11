
from pathlib import Path
from typing import Optional

from conan_app_launcher import asset_path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtGui import QIcon

from .remote_edit_dialog_ui import Ui_Dialog
from .remote_login import RemoteLoginDialog
current_dir = Path(__file__).parent


class RemoteEditDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(asset_path / "icons" / "edit.png")))
        self._ui.login_button.clicked.connect(self.on_login_clicked)
        self._ui.button_box.accepted.connect(self.save)

    def save(self):
        self.accept()
        
    def on_login_clicked(self):
        login_dialog = RemoteLoginDialog(self)
        login_dialog.show()
