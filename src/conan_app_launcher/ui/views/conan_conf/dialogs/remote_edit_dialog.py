
from pathlib import Path
from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import asset_path
from conans.client.cache.remote_registry import Remote
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QWidget

from .remote_edit_dialog_ui import Ui_Dialog
from .remote_login import RemoteLoginDialog

current_dir = Path(__file__).parent

class RemoteEditDialog(QDialog):

    def __init__(self, remote: Remote, new_remote=False, parent: Optional[QWidget]=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self._remote = remote
        self._new_remote = new_remote

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(asset_path / "icons" / "edit.png")))
        # self._ui.login_button.clicked.connect(self.on_login_clicked)
        self._ui.button_box.accepted.connect(self.save)
        
        self._ui.name_line_edit.setText(remote.name)
        self._ui.url_line_edit.setText(remote.url)
        self._ui.verify_ssl_checkbox.setChecked(remote.verify_ssl)

    def save(self):
        new_name = self._ui.name_line_edit.text()
        new_url = self._ui.url_line_edit.text()
        new_verify_ssl = self._ui.verify_ssl_checkbox.isChecked()
        # TODO try catch
        if self._new_remote:
            app.conan_api.conan.remote_add(new_name, new_url, new_verify_ssl)
            self.accept()
            return
        if new_name != self._remote.name:
            app.conan_api.conan.remote_rename(self._remote.name, new_name)
        if new_url != self._remote.url or new_verify_ssl != self._remote.verify_ssl:
            app.conan_api.conan.remote_update(new_name, new_url, new_verify_ssl)

        self.accept()
        
        
    # def on_login_clicked(self):
    #     # TODO
    #     name = self._ui.name_line_edit.text()
        # login_dialog = RemoteLoginDialog(self, remote_names=[self._remote])
        # login_dialog.show()
