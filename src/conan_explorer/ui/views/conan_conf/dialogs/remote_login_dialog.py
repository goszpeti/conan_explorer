
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidgetItem, QWidget

import conan_explorer.app as app
from conan_explorer.app import AsyncLoader
from conan_explorer.conan_wrapper.types import Remote  # using global module pattern
from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.conan_conf.remotes_controller import \
    ConanRemoteController

current_dir = Path(__file__).parent


class RemoteLoginDialog(QDialog):
    """
    Dialog mask for login remotes. 
    The password will be stored by Qt obfuscated, but reversible in RAM.
    To fully lock it out, a manual C++ impl. of QLineEdit would be needed.
    After the dialog is closed, it will be overwritten by a long string.
    """

    def __init__(self, remotes: List[Remote], remotes_controller: ConanRemoteController, parent: Optional[QWidget]):
        super().__init__(parent=parent)
        self._remotes = remotes
        self._remotes_controller = remotes_controller
        from .remote_login_dialog_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # set username, form first name match
        for remote in remotes:
            (name, _) = app.conan_api.get_remote_user_info(remote.name)
            if name:
                self._ui.name_line_edit.setText(name)
                break
        # fill up remote checkbox list
        for remote in remotes:
            item = QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
        self.setWindowIcon(get_themed_asset_icon("icons/login.svg", True))
        self._ui.button_box.accepted.connect(self.on_ok)
        self.adjustSize()

    def on_ok(self):
        """ Is triggered on OK and tries to login while showing a loading dialog """
        loader = AsyncLoader(self)
        loader.async_loading(self, self.login, loading_text="Logging you in...")
        loader.wait_for_finished()
        self.accept()

    def login(self):
        """ Try to login to all selected remotes """
        selected_remotes: List[str] = []
        for idx in range(self._ui.remote_list.count()):
            if self._ui.remote_list.item(idx).checkState() == Qt.CheckState.Checked:
                selected_remotes.append(self._ui.remote_list.item(idx).data(0))
        self._remotes_controller.login_remotes(selected_remotes, self._ui.name_line_edit.text(),
                                               self._ui.password_line_edit.text())
        self.clear_password()

    def clear_password(self):
        """ This will override the currently stored password. Setting an empty string 
        or clear will not work, the string will still be in memory! """
        long_string = "A" * len(self._ui.password_line_edit.text())
        self._ui.password_line_edit.setText(long_string)
        self._ui.password_line_edit.setText("")
        # run gc to clear all possible dangling Python strings
        import gc
        gc.collect()
