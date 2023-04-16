
from pathlib import Path
from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import asset_path
from conans.client.cache.remote_registry import Remote
from conan_app_launcher.app.logger import Logger

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QWidget

from conan_app_launcher.ui.common.theming import get_themed_asset_icon


current_dir = Path(__file__).parent


class RemoteEditDialog(QDialog):

    def __init__(self, remote: Remote, new_remote=False, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        from .remote_edit_dialog_ui import Ui_Dialog
        self._remote = remote
        self._new_remote = new_remote

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(get_themed_asset_icon("icons/edit.svg", True))
        self._ui.button_box.accepted.connect(self.save)

        self._ui.name_line_edit.setText(remote.name)
        self._ui.url_line_edit.setText(remote.url)
        self._ui.verify_ssl_checkbox.setChecked(remote.verify_ssl)

    def save(self):
        """ Save edited remote information by calling the appropriate conan methods. """
        new_name = self._ui.name_line_edit.text()
        new_url = self._ui.url_line_edit.text()
        new_verify_ssl = self._ui.verify_ssl_checkbox.isChecked()
        try:
            # TODO Dedicated functions
            if self._new_remote:
                app.conan_api._conan.remote_add(new_name, new_url, new_verify_ssl)
                self.accept()
                return
            if new_name != self._remote.name:
                app.conan_api._conan.remote_rename(self._remote.name, new_name)
            if new_url != self._remote.url or new_verify_ssl != self._remote.verify_ssl:
                app.conan_api._conan.remote_update(new_name, new_url, new_verify_ssl)
        except Exception as e:
            Logger().error(str(e))
        self.accept()
