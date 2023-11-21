
from pathlib import Path
from typing import Optional

import conan_explorer.app as app  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.ui.common import measure_font_width
from conan_explorer.ui.common.theming import get_themed_asset_icon
from conan_explorer.ui.views.app_grid.model import UiAppLinkModel
from conan_explorer.ui.dialogs import ConanInstallDialog
from conan_explorer.conan_wrapper.types import ConanRef

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QWidget, QDialog, QFileDialog, QMessageBox


class AppEditDialog(QDialog):

    def __init__(self,  model: UiAppLinkModel, parent: Optional[QWidget],
                 pkg_installed_signal: Optional[SignalInstance] = None):
        super().__init__(parent=parent)
        self._model = model
        self._pkg_installed_signal = pkg_installed_signal
        from .app_edit_dialog_ui import Ui_Dialog

        # without baseinstance, dialog would further needed to be configured
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        self.setModal(True)
        self.setWindowTitle("Edit App Link")
        self.setWindowIcon(get_themed_asset_icon("icons/edit.svg", True))

        self._ui.executable_browse_button.setEnabled(False)
        self._ui.icon_browse_button.setEnabled(False)

        self._ui.conan_ref_line_edit.set_loading_callback(self.loading_started_info)
        self._ui.conan_ref_line_edit.completion_finished.connect(self.loading_finished_info)
        self._ui.conan_ref_line_edit.textChanged.connect(self.toggle_browse_buttons)

        # fill up current info
        self._ui.name_line_edit.setText(self._model.name)
        self._ui.conan_ref_line_edit.setText(self._model.conan_ref)
        self._ui.execpath_line_edit.setText(self._model.executable)
        self._ui.is_console_app_checkbox.setChecked(self._model.is_console_application)
        self._ui.icon_line_edit.setText(self._model.icon)
        self._ui.args_line_edit.setText(self._model.args)
        width_to_set = measure_font_width(self._ui.args_line_edit.text()) + 10
        if width_to_set > self.parentWidget().geometry().width():
            width_to_set = self.parentWidget().geometry().width()
        if width_to_set < self.parentWidget().geometry().width()/2:
            width_to_set = int(self.parentWidget().geometry().width()/2)
        self.setMinimumWidth(width_to_set)
        conan_options_text = ""
        for option in self._model.conan_options:
            conan_options_text += f"{option}={self._model.conan_options.get(option)}\n"
        self._ui.conan_opts_text_edit.setText(conan_options_text)

        self._ui.install_button.clicked.connect(self.on_install_clicked)
        self._ui.executable_browse_button.clicked.connect(self.on_executable_browse_clicked)
        self._ui.icon_browse_button.clicked.connect(self.on_icon_browse_clicked)

        # enable/disable button, if package_folder is set
        if self._pkg_installed_signal:
            self._pkg_installed_signal.connect(self.toggle_browse_buttons)

        # for some reason OK is not connected at default
        self._ui.button_box.accepted.connect(self.save_data)
        self._ui.button_box.accepted.connect(self.cleanup)
        self._ui.button_box.rejected.connect(self.cleanup)

    def cleanup(self) -> None:
        self._ui.conan_ref_line_edit.cleanup()

    def toggle_browse_buttons(self):
        if not self._ui.conan_ref_line_edit.is_valid:
            self._ui.executable_browse_button.setEnabled(False)
            self._ui.icon_browse_button.setEnabled(False)
            return
        self._ui.executable_browse_button.setEnabled(True)
        self._ui.icon_browse_button.setEnabled(True)

    def on_install_clicked(self):
        dialog = ConanInstallDialog(self, self._ui.conan_ref_line_edit.text(), self._pkg_installed_signal, lock_reference=True)
        dialog.show()

    def on_executable_browse_clicked(self):
        _, temp_package_path = app.conan_api.get_best_matching_local_package_path(
            ConanRef.loads(self._ui.conan_ref_line_edit.text()), self.resolve_conan_options())
        if not temp_package_path.exists():  # default path
            temp_package_path = Path.home()
        dialog = QFileDialog(parent=self, caption="Select file for icon display",
                             directory=str(temp_package_path))
        # filter="Images (*.ico *.svg *.jpg)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        # TODO restrict to the package directory, or emit Error dialog and call anew
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            exe_path = Path(dialog.selectedFiles()[0])
            try:
                exe_rel_path = exe_path.relative_to(temp_package_path)
            except Exception:
                msg = QMessageBox(parent=self)
                msg.setWindowTitle("Invalid selection")
                msg.setText(f"The entered path {str(exe_path)} is not in the selected conan package folder!")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
                return False
            # use as_posix to always get forward slashes in the relpath
            self._ui.execpath_line_edit.setText(exe_rel_path.as_posix())
            return True

    def on_icon_browse_clicked(self):
        _, temp_package_path = app.conan_api.get_best_matching_local_package_path(
            ConanRef.loads(self._ui.conan_ref_line_edit.text()), self.resolve_conan_options())
        if not temp_package_path.exists():  # default path
            temp_package_path = Path.home()
        dialog = QFileDialog(parent=self, caption="Select file for icon display",
                             directory=str(temp_package_path),
                             filter="Images (*.ico *.png *.svg *.jpg)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            icon_path = Path(dialog.selectedFiles()[0])
            try:
                icon_rel_path = icon_path.relative_to(temp_package_path)
                self._ui.icon_line_edit.setText(str(icon_rel_path))
            except Exception:
                # errors, if it does not resolve
                self._ui.icon_line_edit.setText(str(icon_path))

    def loading_started_info(self):
        self._ui.conan_ref_label.setText("Conan Reference (query in progress)")

    def loading_finished_info(self):
        self._ui.conan_ref_label.setText("Conan Reference (query finished)")

    def resolve_conan_options(self):
        conan_options_text = self._ui.conan_opts_text_edit.toPlainText().splitlines()
        conan_options = {}
        for line in conan_options_text:
            split_values = line.split("=")
            if len(split_values) == 2:
                conan_options.update({split_values[0]: split_values[1]})
            else:
                Logger().warning(f"Wrong format in option: {line}")
        return conan_options

    def save_data(self):
        # check all input validations
        if not self._ui.conan_ref_line_edit.is_valid:
            msg = QMessageBox(parent=self)
            msg.setWindowTitle("Invalid Conan Reference")
            msg.setText(f"The entered Conan reference has an invalid format!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return
        # write back app info
        self._model.name = self._ui.name_line_edit.text()
        self._model.conan_ref = self._ui.conan_ref_line_edit.text()
        self._model.executable = self._ui.execpath_line_edit.text()
        self._model.is_console_application = self._ui.is_console_app_checkbox.isChecked()
        self._model.icon = self._ui.icon_line_edit.text()
        self._model.args = self._ui.args_line_edit.text()
        self._model.conan_options = self.resolve_conan_options()
        self._model.save()
        self.accept()
