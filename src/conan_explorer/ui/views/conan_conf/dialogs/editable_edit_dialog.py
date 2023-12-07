
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

import conan_explorer.app as app  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanRef
from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.conan_conf.editable_model import EditableModelItem


class EditableEditDialog(QDialog):

    def __init__(self, editable: Optional[EditableModelItem], parent: Optional[QWidget]=None):
        super().__init__(parent=parent)
        from .editable_edit_dialog_ui import Ui_Dialog
        if editable is None:
            editable = EditableModelItem("", "", "")
        self._editable = editable
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setWindowIcon(get_themed_asset_icon("icons/edit.svg", True))
        self._ui.button_box.accepted.connect(self.save)
        self._ui.path_browse_button.clicked.connect(self.on_path_browse_button_clicked)
        self._ui.output_folder_browse_button.clicked.connect(self.on_output_browse_button_clicked)

        self._ui.name_line_edit.setText(editable.name)
        self._ui.path_line_edit.setText(editable.path)
        self._ui.output_folder_line_edit.setText(editable.output)

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
        new_path = self._ui.path_line_edit.text().strip()
        new_output_folder = self._ui.output_folder_line_edit.text()
        try:
            # if name changed -> remove the old one
            if app.conan_api.add_editable(ConanRef.loads(new_name), new_path, new_output_folder):
                if self._editable.name and new_name != self._editable.name:
                    app.conan_api.remove_editable(ConanRef.loads(self._editable.name))
        except Exception as e:
            Logger().error(str(e))
        self.accept()
