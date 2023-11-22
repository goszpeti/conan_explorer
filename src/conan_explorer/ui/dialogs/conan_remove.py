from typing import Optional

import conan_explorer.app as app
from conan_explorer.app import AsyncLoader  # using global module pattern
from conan_explorer.app.logger import Logger

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QMessageBox, QWidget

from conan_explorer.conan_wrapper.types import ConanRef


class ConanRemoveDialog(QMessageBox):

    def __init__(self, parent: Optional[QWidget],  conan_ref: str, pkg_id: str,
                 conan_pkg_removed: Optional[SignalInstance] = None):
        super().__init__(parent)
        self._conan_ref = conan_ref
        self._pkg_id = pkg_id
        self._conan_pkg_removed_sig = conan_pkg_removed

        self.setWindowTitle("Remove package")
        self.setText(f"Are you sure, you want to remove {conan_ref} {pkg_id}?")
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        self.setIcon(QMessageBox.Icon.Question)

        self.setModal(True)
        self.button(self.StandardButton.Yes).clicked.connect(self.on_remove)
        self.show()

    def on_remove(self):
        """ Remove conan ref/pkg and emit a signal, if registered """
        loader = AsyncLoader(self)
        loader.async_loading(self, self.remove, cancel_button=False)
        loader.wait_for_finished()

    def remove(self):
        try:
            Logger().info(f"Deleting {self._conan_ref} {self._pkg_id}")
            app.conan_api.remove_reference(ConanRef.loads(self._conan_ref), self._pkg_id)
        except Exception as e:
            Logger().error(f"Error while removing package {self._conan_ref}: {str(e)}")
        if not self._conan_pkg_removed_sig:
            return
        self._conan_pkg_removed_sig.emit(self._conan_ref, self._pkg_id)