
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QDialog, QFileDialog, QWidget
from conan_explorer.conan_wrapper.types import EditablePkg

from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.conan_conf.editable_controller import ConanEditableController

class EditableEditDialog(QDialog):
    def __init__(self, editable: Optional[EditablePkg], editable_controller: ConanEditableController, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        from .editable_edit_dialog_ui import Ui_Dialog
        if editable is None:
            editable = EditablePkg("", "", "")
        self._editable = editable
        self._editable_controller = editable_controller
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(get_themed_asset_icon("icons/edit.svg", True))
        self._ui.button_box.accepted.connect(self.save)
        self._ui.path_browse_button.clicked.connect(self.on_path_browse_button_clicked)
        self._ui.output_folder_browse_button.clicked.connect(self.on_output_browse_button_clicked)

        self._ui.name_line_edit.setText(editable.conan_ref)
        self._ui.path_line_edit.setText(editable.path)
        self._ui.output_folder_line_edit.setText(str(editable.output_folder))

    def on_path_browse_button_clicked(self):
        current_path = self._ui.path_line_edit.text()
        default_path = current_path if current_path else str(Path.home())
        path = self.select_folder_dialog(default_path)
        if not path:
            return
        self._ui.path_line_edit.setText(path)

    def on_output_browse_button_clicked(self):
        current_path = self._ui.output_folder_line_edit.text()
        default_path = current_path if current_path else str(Path.home())
        path = self.select_folder_dialog(default_path)
        if not path:
            return
        self._ui.output_folder_line_edit.setText(path)

    def select_folder_dialog(self, start_path: str) -> str:
        dialog = QFileDialog(parent=self, caption="Select path",
                             directory=str(start_path),)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0]
        return ""

    def save(self):
        """ Save edited editable information by calling the appropriate conan methods. """
        new_name = self._ui.name_line_edit.text().strip()
        remove_after_add = False # if name changed -> remove the old one
        if self._editable.conan_ref and self._editable.conan_ref != new_name:
            remove_after_add = True

        new_editable = EditablePkg(new_name, self._ui.path_line_edit.text().strip(), 
                                   self._ui.output_folder_line_edit.text())
        if self._editable_controller.add(new_editable):
            if remove_after_add:
                self._editable_controller.remove(self._editable)
        self.accept()
