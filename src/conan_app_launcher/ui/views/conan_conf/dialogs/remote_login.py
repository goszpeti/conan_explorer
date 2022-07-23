
from pathlib import Path
from typing import List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import asset_path
from conan_app_launcher.app.logger import Logger
from conans.client.cache.remote_registry import Remote
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QWidget, QListWidgetItem

from .remote_login_dialog_ui import Ui_Dialog

current_dir = Path(__file__).parent


class RemoteLoginDialog(QDialog):
    """
    Dialog mask for login remotes. 
    The password will be stored by Qt obfuscated, but reversible in RAM.
    To fully lock it out, a manual C++ impl. of QLineEdit would be needed.
    After the dialog is closed, it will be overwritten by a long string.
    """

    def __init__(self, parent: Optional[QWidget], flags=Qt.WindowFlags(), remotes: List[Remote]=[]):
        super().__init__(parent=parent, flags=flags)
        self._remotes = remotes
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        for remote in remotes:
            (name, _) = app.conan_api.get_remote_user_info(remote.name)
            if name:
                self._ui.name_line_edit.setText(name)
                break
        # remotes = app.conan_api.get_remotes()
        for remote in remotes:
            item = QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
        self.setWindowIcon(QIcon(str(asset_path / "icons" / "login.png")))
        self._ui.button_box.accepted.connect(self.save)

# TODO  clear_password on cancel?

    def save(self):
        for remote in self._remotes:
            # TODO output? Try catch?
            try:
                app.conan_api.conan.authenticate(self._ui.name_line_edit.text(),
                                                self._ui.password_line_edit.text(), remote.name)
            except Exception as e:
                Logger().error(f"Can't sign in to {remote}: {str(e)}")
                return
            Logger().info(f"Successfully logged in to {remote}")
        self.clear_password()
        self.accept()

    def clear_password(self):
        # This will override the currently stored password. Setting an empty string 
        # or clear will not work, the string will still be in memory!
        long_string = "A" * len(self._ui.password_line_edit.text())
        self._ui.password_line_edit.setText(long_string)
        self._ui.password_line_edit.setText("")
        # run gc to clear all possible dangling Python strings
        import gc
        gc.collect()
