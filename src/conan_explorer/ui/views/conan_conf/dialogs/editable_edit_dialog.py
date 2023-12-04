
from pathlib import Path
from typing import Optional

import conan_explorer.app as app  # using global module pattern
from conan_explorer.app.logger import Logger

from PySide6.QtWidgets import QDialog, QWidget, QFileDialog

from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.conan_conf.editable_model import EditableModelItem

class EditableEditDialog(QDialog):

    def __init__(self, editable: Optional[EditableModelItem], parent: Optional[QWidget]=None):
        super().__init__(parent=parent)
        from .editable_edit_dialog_ui import Ui_Dialog
        self._new_editable = False
        if editable is None:
            editable = EditableModelItem("", "", "")
            self._new_editable = True
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
        path = self.select_folder_dialog(self._editable.path)
        if not path:
            return
        self._editable.path = path
        self._ui.path_line_edit.setText(path)

    def on_output_browse_button_clicked(self):
        path = self.select_folder_dialog(self._editable.output)
        if not path:
            return
        self._editable.output = path
        self._ui.output_folder_line_edit.setText(path)

    def select_folder_dialog(self, start_path: str) -> str:
        dialog = QFileDialog(parent=self, caption="Select path",
                             directory=str(start_path),
                             )
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0]
        return ""

    def save(self):
        """ Save edited editable information by calling the appropriate conan methods. """
        new_name = self._ui.name_line_edit.text()
        new_path = self._ui.path_line_edit.text()
        new_output_folder = self._ui.output_folder_line_edit.text()
        try:
            if self._new_editable:
                app.conan_api.add_editable(new_name, new_path, new_output_folder)
                self.accept()
                return
            # if name changed -> remove the old one
            app.conan_api.set_editable(new_name, new_path, new_output_folder)
            if new_name != self._editable.name:
                app.conan_api.remove_editable(self._editable.name)
        except Exception as e:
            Logger().error(str(e))
        self.accept()
