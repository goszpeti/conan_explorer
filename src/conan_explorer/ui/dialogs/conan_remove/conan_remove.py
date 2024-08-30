from typing import Dict, List, Optional

import conan_explorer.app as app
from conan_explorer.app import LoaderGui  # using global module pattern
from conan_explorer.app.logger import Logger

from PySide6.QtCore import SignalInstance, Qt
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QListWidgetItem, QStyle

from conan_explorer.conan_wrapper.types import ConanRef


class ConanRemoveDialog(QDialog):

    def __init__(self, parent: Optional[QWidget], conan_refs_with_pkg_ids: Dict[str, List[str]],
                 conan_pkg_removed: Optional[SignalInstance] = None):
        super().__init__(parent)
        self._conan_pkg_removed_sig = conan_pkg_removed
        from .conan_remove_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        pixmapi = getattr(QStyle, "SP_MessageBoxQuestion")
        if pixmapi:
            icon = self.style().standardIcon(pixmapi)
            self._ui.icon.setPixmap(icon.pixmap(40,40))

        for conan_ref, pkg_ids in conan_refs_with_pkg_ids.items():
            for pkg_id in pkg_ids:
                if not pkg_id:
                    text = conan_ref
                else:
                    text = f"{conan_ref}:{pkg_id}"
                list_item = QListWidgetItem(text)
                list_item.setCheckState(Qt.CheckState.Checked)
                self._ui.package_list_widget.addItem(list_item)

        self._ui.button_box.button(
            QDialogButtonBox.StandardButton.Yes).clicked.connect(self.on_remove)

    def on_remove(self):
        """ Remove conan ref/pkg and emit a signal, if registered """
        self.loader = LoaderGui(self)
        self.loader.load_for_blocking(self, self.remove, cancel_button=False, loading_text="Removing packages")
        self.loader.wait_for_finished()

    def remove(self):
        """ Remove the selected ref or pkg. Emit conan_pkg_removed global signal.
        To be called while loading dialog is active. """
        for list_row in range(self._ui.package_list_widget.count()):
            list_item = self._ui.package_list_widget.item(list_row)
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
