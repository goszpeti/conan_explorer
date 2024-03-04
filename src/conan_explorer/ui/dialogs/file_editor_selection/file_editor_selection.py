
from pathlib import Path
from PySide6.QtWidgets import QDialog, QFileDialog
import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE

class FileEditorSelDialog(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        from .file_editor_selector_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setWindowTitle("File Editor Selection")

        self._ui.file_edit.setText(app.active_settings.get_string(FILE_EDITOR_EXECUTABLE))
        self._ui.browse_button.clicked.connect(self.on_browse_clicked)
        self._ui.button_box.accepted.connect(self.on_save)
        self._ui.button_box.rejected.connect(self.close)


    def on_browse_clicked(self):
        current_file = Path(self._ui.file_edit.text())
        path_to_open = Path().home
        if current_file.exists():
            path_to_open = current_file.parent
        dialog = QFileDialog(parent=self, caption="Select file for icon display",
                             directory=str(path_to_open),
                             filter="Executables (*)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_path = Path(dialog.selectedFiles()[0])
            try:
                self._ui.file_edit.setText(str(selected_path))
            except Exception as e:
                # errors, if it does not resolve
                Logger().debug(f"Can't set selected path: {str(e)}.")

    def on_save(self):
        app.active_settings.set(FILE_EDITOR_EXECUTABLE, self._ui.file_edit.text())
        self.close()
