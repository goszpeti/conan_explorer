from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.app.logger import Logger
from PyQt5.QtCore import pyqtBoundSignal
from PyQt5.QtWidgets import QMessageBox, QWidget


class ConanRemoveDialog(QMessageBox):

    def __init__(self, parent: Optional[QWidget],  conan_ref: str, pkg_id: str,
                 conan_pkg_removed: Optional[pyqtBoundSignal] = None):
        super().__init__(parent)
        self._conan_ref = conan_ref
        self._pkg_id = pkg_id
        self._conan_pkg_removed_sig = conan_pkg_removed

        self.setWindowTitle("Remove package")
        self.setText(f"Are you sure, you want to remove {conan_ref} {pkg_id}?")
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        self.setIcon(QMessageBox.Question)

        self.setModal(True)
        self.button(self.Yes).clicked.connect(self.on_remove)
        self.show()

    def on_remove(self):
        """ Remove conan ref/pkg and emit a signal, if registered """
        try:
            Logger().info(f"Deleting {self._conan_ref} {self._pkg_id}")

            pkg_ids = [self._pkg_id] if self._pkg_id else None
            app.conan_api.conan.remove(self._conan_ref, packages=pkg_ids, force=True)
        except Exception as e:
            Logger().error(f"Error while removing package {self._conan_ref}: {str(e)}")
        if not self._conan_pkg_removed_sig:
            return
        self._conan_pkg_removed_sig.emit(self._conan_ref, self._pkg_id)
