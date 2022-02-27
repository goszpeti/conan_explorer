
from pathlib import Path
from conan_app_launcher import asset_path
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.views.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog

from PyQt5 import QtCore, QtGui, QtWidgets, uic

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class AppEditDialog(QtWidgets.QDialog):

    def __init__(self,  model: UiAppLinkModel, parent: QtWidgets.QWidget, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self._model = model

        # without baseinstance, dialog would further needed to be configured
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "app_edit_dialog.ui", baseinstance=self)

        self.setModal(True)
        self.setWindowTitle("Edit App Link")
        self.setWindowIcon(QtGui.QIcon(str(asset_path / "icons" / "edit.png")))

        # fill up current info
        self._ui.name_line_edit.setText(self._model.name)
        self._ui.conan_ref_line_edit.setText(self._model.conan_ref)
        self._ui.exec_path_line_edit.setText(self._model.executable)
        self._ui.is_console_app_checkbox.setChecked(self._model.is_console_application)
        self._ui.icon_line_edit.setText(self._model.icon)
        self._ui.args_line_edit.setText(self._model.args)

        self._ui.conan_ref_line_edit.set_loading_callback(self.loading_started_info)
        self._ui.conan_ref_line_edit.completion_finished.connect(self.loading_finished_info)
        conan_options_text = ""
        for option in self._model.conan_options:
            conan_options_text += f"{option}={self._model.conan_options.get(option)}\n"
        self._ui.conan_opts_text_edit.setText(conan_options_text)
        
        self._ui.install_button.clicked.connect(self.on_install_clicked)
        self._ui.executable_browse_button.clicked.connect(self.on_executable_browse_clicked)
        self._ui.icon_browse_button.clicked.connect(self.on_icon_browse_clicked)

        # for some reason OK is not connected at default
        self._ui.button_box.accepted.connect(self.save_data)
        self.adjustSize()

    def on_install_clicked(self):
        dialog = ConanInstallDialog(self, self._ui.conan_ref_line_edit.text()) # TODO , self._main_window.conan_pkg_installed)
        dialog.show()

    def on_executable_browse_clicked(self):
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select file for icon display",
                                       directory=str(self._model.package_folder))
                                      # filter="Images (*.ico *.png *.jpg)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        # TODO restrict to the package directory, or emit Error dialog and call anew
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            exe_path = Path(dialog.selectedFiles()[0])
            try:
                exe_rel_path = exe_path.relative_to(self._model.package_folder)
            except:
                msg = QtWidgets.QMessageBox(parent=self)
                msg.setWindowTitle("Invalid selection")
                msg.setText(f"The entered path {str(exe_path)} is not in the selected conan package folder!")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.exec_()
                return False
            self._ui.exec_path_line_edit.setText(str(exe_rel_path))
            return True

    def on_icon_browse_clicked(self):
        dialog = QtWidgets.QFileDialog(parent=self, caption="Select file for icon display",
                                       directory=str(self._model.package_folder),
                                       filter="Images (*.ico *.png *.jpg)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            icon_path = Path(dialog.selectedFiles()[0])
            try:
                icon_rel_path = icon_path.relative_to(self._model.package_folder)
                self._ui.icon_line_edit.setText(str(icon_rel_path))
            except:
                # errors, if it does not resolve
                self._ui.icon_line_edit.setText(str(icon_path))

    def loading_started_info(self):
        self._ui.conan_ref_label.setText("Conan Reference (query in progress)")

    def loading_finished_info(self):
        self._ui.conan_ref_label.setText("Conan Reference (query finished)")

    def save_data(self):
        # check all input validations
        if not self._ui.conan_ref_line_edit.is_valid:
           msg = QtWidgets.QMessageBox(parent=self)
           msg.setWindowTitle("Invalid Conan Reference")
           msg.setText(f"The entered Conan reference has an invalid format!")
           msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
           msg.setIcon(QtWidgets.QMessageBox.Critical)
           msg.exec_()
           return
        if not self.exe_path_valid(Path(self._ui.exec_path_line_edit.text())):
            return

        # write back app info
        self._model.name = self._ui.name_line_edit.text()
        self._model.conan_ref = self._ui.conan_ref_line_edit.text()
        self._model.executable = self._ui.exec_path_line_edit.text()
        self._model.is_console_application = self._ui.is_console_app_checkbox.isChecked()
        self._model.icon = self._ui.icon_line_edit.text()
        self._model.args = self._ui.args_line_edit.text()

        conan_options_text = self._ui.conan_opts_text_edit.toPlainText().splitlines()
        conan_options = {}
        for line in conan_options_text:
            split_values = line.split("=")
            if len(split_values) == 2:
                conan_options.update({split_values[0]: split_values[1]})
            else:
                Logger().warning(f"Wrong format in option: {line}")
        self._model.conan_options = conan_options
        self._model.save()
        self.accept()
