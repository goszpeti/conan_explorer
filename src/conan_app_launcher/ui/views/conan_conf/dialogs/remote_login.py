
from pathlib import Path
from typing import Optional
import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.app.logger import Logger

from conan_app_launcher import asset_path
from conan_app_launcher.ui.views.app_grid.model import UiTabModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtGui import QIcon

from .remote_login_dialog_ui import Ui_Dialog

current_dir = Path(__file__).parent


class RemoteLoginDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], flags=Qt.WindowFlags(), remote_names=[]):
        super().__init__(parent=parent, flags=flags)
        self._remote_names = remote_names
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        for remote in remote_names:
            (name, _) = app.conan_api.get_remote_user_info(remote)
            if name:
                self._ui.name_line_edit.setText(name)
                break
        self.setWindowIcon(QIcon(str(asset_path / "icons" / "edit.png")))
        self._ui.button_box.accepted.connect(self.save)

    def save(self):
        for remote in self._remote_names:
            # TODO output? Try catch?
            try:
                app.conan_api.conan.authenticate(self._ui.name_line_edit.text(),
                                                self._ui.password_line_edit.text(), remote)
            except Exception as e:
                Logger().error(f"Can't sign in to {remote}: {str(e)}")
                return
            Logger().info(f"Successfully logged in to {remote}")

        self.accept()

