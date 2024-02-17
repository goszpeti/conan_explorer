
from typing import Optional

from PySide6.QtWidgets import QDialog, QWidget

from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import Remote
from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.conan_conf.remotes_controller import \
    ConanRemoteController


class RemoteEditDialog(QDialog):

    def __init__(self, remote: Optional[Remote], remotes_controller: ConanRemoteController, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        from .remote_edit_dialog_ui import Ui_Dialog
        self._new_remote = False
        self._remotes_controller = remotes_controller
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
        self._ui.verify_ssl_checkbox.setChecked(bool(remote.verify_ssl))

    def save(self):
        """ Save edited remote information by calling the appropriate conan methods. """
        new_name = self._ui.name_line_edit.text()
        new_url = self._ui.url_line_edit.text()
        new_verify_ssl = self._ui.verify_ssl_checkbox.isChecked()
        try:
            if self._new_remote:
                self._remotes_controller.add(
                    Remote(new_name, new_url, new_verify_ssl, False))
                self.accept()
                return
            if new_name != self._remote.name:
                self._remotes_controller.rename(self._remote, new_name)
            if new_url != self._remote.url or new_verify_ssl != self._remote.verify_ssl:
                self._remotes_controller.update_remote(
                    Remote(new_name, new_url, new_verify_ssl, self._remote.disabled))
        except Exception as e:
            Logger().error(str(e))
        self.accept()
