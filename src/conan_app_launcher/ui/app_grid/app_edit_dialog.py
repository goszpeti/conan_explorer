
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import conan_app_launcher as this
from conan_app_launcher.components import AppConfigEntry

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class EditAppDialog(QtWidgets.QDialog):

    def __init__(self,  app_config_data: AppConfigEntry, parent: QtWidgets.QWidget, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self._app_config_data = app_config_data
        self._ui = uic.loadUi(this.base_path / "ui" / "app_grid" / "app_edit.ui", baseinstance=self)

        self.setModal(True)
        self.setWindowTitle("Edit App Link")
        self.setWindowIcon(QtGui.QIcon(str(this.asset_path / "icons" / "edit.png")))

        # fill up current info
        self._ui.name_line_edit.setText(self._app_config_data.name)
        self._ui.conan_ref_line_edit.setText(str(self._app_config_data.conan_ref))
        self._ui.exec_path_line_edit.setText(self._app_config_data.app_data.get("executable", ""))
        self._ui.is_console_app_checkbox.setChecked(self._app_config_data.is_console_application)
        self._ui.icon_line_edit.setText(self._app_config_data.app_data.get("icon", ""))
        self._ui.args_line_edit.setText(self._app_config_data.args)

        self._ui.conan_ref_line_edit.set_loading_callback(self.loading_started)
        self._ui.conan_ref_line_edit.completion_finished.connect(self.loading_finished)
        conan_options_text = ""
        for option in self._app_config_data.conan_options:
            conan_options_text += f"{option}={self._app_config_data.conan_options.get(option)}\n"
        self._ui.conan_opts_text_edit.setText(conan_options_text)
        # for some reason OK is not connected at default
        self._ui.button_box.accepted.connect(self.accept)

    def loading_started(self):
        self._ui.conan_ref_label.setText("Conan Reference (query in progress)")

    def loading_finished(self):
        self._ui.conan_ref_label.setText("Conan Reference (query finished)")
  
    def save_data(self):
        # check all input validations
        if not self._ui.conan_ref_line_edit.hasAcceptableInput():
            # TODO handle invalid input
            pass

        # write back app info
        self._app_config_data.name = self._ui.name_line_edit.text()
        self._app_config_data.conan_ref = self._ui.conan_ref_line_edit.text()
        self._app_config_data.executable = self._ui.exec_path_line_edit.text()
        self._app_config_data.is_console_application = self._ui.is_console_app_checkbox.isChecked()
        self._app_config_data.icon = self._ui.icon_line_edit.text()
        self._app_config_data.args = self._ui.args_line_edit.text()

        conan_options_text = self._ui.conan_opts_text_edit.toPlainText().splitlines()
        conan_options = {}
        for line in conan_options_text:
            split_values = line.split("=")
            if len(split_values) == 2:
                conan_options.update({split_values[0]: split_values[1]})
            else:
                pass  # TODO warning
        self._app_config_data.conan_options = conan_options
