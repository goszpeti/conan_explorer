from typing import Dict, List, Optional

from PySide6.QtCore import Qt, SignalInstance
from PySide6.QtWidgets import QDialogButtonBox, QListWidgetItem, QWidget

import conan_explorer.app as app
from conan_explorer.app import LoaderGui  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanRef

from .. import QuestionWithItemListDialog

StdButton = QDialogButtonBox.StandardButton


class ConanRemoveDialog(QuestionWithItemListDialog):
    def __init__(
        self,
        parent: Optional[QWidget],
        conan_refs_with_pkg_ids: Dict[str, List[str]],
        conan_pkg_removed: Optional[SignalInstance] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Remove Package(s)")
        self.set_question_text("Are you sure you want to remove these packages?")
        self._conan_pkg_removed_sig = conan_pkg_removed
        for conan_ref, pkg_ids in conan_refs_with_pkg_ids.items():
            for pkg_id in pkg_ids:
                if not pkg_id:
                    text = conan_ref
                else:
                    text = f"{conan_ref}:{pkg_id}"
                list_item = QListWidgetItem(text)
                list_item.setCheckState(Qt.CheckState.Checked)
                self.item_list_widget.addItem(list_item)

        self.button_box.button(StdButton.Yes).clicked.connect(self.on_remove)

    def on_remove(self):
        """Remove conan ref/pkg and emit a signal, if registered"""
        self.loader = LoaderGui(self)
        self.loader.load_for_blocking(
            self, self.remove, cancel_button=False, loading_text="Removing packages"
        )
        self.loader.wait_for_finished()

    def remove(self):
        """Remove the selected ref or pkg. Emit conan_pkg_removed global signal.
        To be called while loading dialog is active."""
        for list_row in range(self.item_list_widget.count()):
            list_item = self.item_list_widget.item(list_row)
            if list_item.checkState() != Qt.CheckState.Checked:
                continue
            conan_ref_with_id = list_item.text()
            pkg_id = ""
            if ":" in conan_ref_with_id:
                conan_ref, pkg_id = conan_ref_with_id.split(":")
            else:
                conan_ref = conan_ref_with_id
            try:
                self.loader.loading_string_signal.emit(f"Removing {conan_ref} {pkg_id}")
                # can handle multiple pkgs at once, but then we can't log info for the
                # progress bar
                app.conan_api.remove_reference(ConanRef.loads(conan_ref), pkg_id)
            except Exception as e:
                Logger().error(f"Error while removing package {conan_ref}: {str(e)}")
                continue
            if self._conan_pkg_removed_sig:
                self._conan_pkg_removed_sig.emit(conan_ref, pkg_id)
            Logger().info(f"Removing package {conan_ref_with_id} finished")
