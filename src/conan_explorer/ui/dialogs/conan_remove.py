from typing import Dict, List, Optional

import conan_explorer.app as app
from conan_explorer.app import LoaderGui  # using global module pattern
from conan_explorer.app.logger import Logger

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QMessageBox, QWidget

from conan_explorer.conan_wrapper.types import ConanRef


class ConanRemoveDialog(QMessageBox):

    def __init__(self, parent: Optional[QWidget], conan_refs_with_pkg_ids: Dict[str, List[str]],
                 conan_pkg_removed: Optional[SignalInstance] = None):
        super().__init__(parent)
        self._conan_refs_with_pkg_ids = conan_refs_with_pkg_ids
        self._conan_pkg_removed_sig = conan_pkg_removed

        self.setWindowTitle("Remove package")
        pkgs_to_delete = []
        for conan_ref, pkg_ids in conan_refs_with_pkg_ids.items():
            for pkg_id in pkg_ids:
                if not pkg_id:
                    pkgs_to_delete.append(conan_ref + " (all packages)")
                else:
                    pkgs_to_delete.append(f"{conan_ref}:{pkg_id}")
        pkgs_to_delete_str = ',\n'.join(pkgs_to_delete)
        self.setText(f"Are you sure, you want to remove: {pkgs_to_delete_str}?")
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        self.setIcon(QMessageBox.Icon.Question)

        self.setModal(True)
        self.button(self.StandardButton.Yes).clicked.connect(self.on_remove)
        self.show()

    def on_remove(self):
        """ Remove conan ref/pkg and emit a signal, if registered """
        self.loader = LoaderGui(self)
        self.loader.load_for_blocking(self, self.remove, cancel_button=False, loading_text="Removing packages")
        self.loader.wait_for_finished()

    def remove(self):
        for conan_ref, pkg_ids in self._conan_refs_with_pkg_ids.items():
            for pkg_id in pkg_ids:
                try:
                    self.loader.loading_string_signal.emit(
                        f"Removing {conan_ref} {pkg_id}")
                    # can handle multiple pkgs at once, but then we can't log info for the 
                    # progress bar
                    app.conan_api.remove_reference(ConanRef.loads(conan_ref), pkg_id)
                except Exception as e:
                    Logger().error(f"Error while removing package {conan_ref}: {str(e)}")
                    continue
                if self._conan_pkg_removed_sig:
                    self._conan_pkg_removed_sig.emit(conan_ref, pkg_id)