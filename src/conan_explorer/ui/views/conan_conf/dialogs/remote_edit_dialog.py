
from pathlib import Path
from typing import Optional

import conan_explorer.app as app  # using global module pattern
from conans.client.cache.remote_registry import Remote
from conan_explorer.app.logger import Logger

from PySide6.QtWidgets import QDialog, QWidget

from conan_explorer.ui.common.theming import get_themed_asset_icon

class RemoteEditDialog(QDialog):

    def __init__(self, remote: Optional[Remote], parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        from .remote_edit_dialog_ui import Ui_Dialog
        self._new_remote = False
        if remote is None:
            remote = Remote("New", "", True, False)
            self._new_remote = True
        self._remote = remote

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
            if self._new_remote:
                app.conan_api.add_remote(new_name, new_url, new_verify_ssl)
                self.accept()
                return
            if new_name != self._remote.name:
                app.conan_api.rename_remote(self._remote.name, new_name)
            if new_url != self._remote.url or new_verify_ssl != self._remote.verify_ssl:
                app.conan_api.update_remote(new_name, new_url, new_verify_ssl, self._remote.disabled, None)
        except Exception as e:
            Logger().error(str(e))
        self.accept()
