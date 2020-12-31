from typing import List

from conan_app_launcher.components import AppConfigEntry, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS, Settings)
from conan_app_launcher.ui.qt import app_edit
from PyQt5 import QtCore, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class EditAppDialog(QtWidgets.QDialog):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setModal(True)
        self._ui = app_edit.Ui_Dialog()
        self._ui.setupUi(self.dialog)

        # fill up current info
        self._ui.name_line_edit.setText(self._app_info.name)
        self._ui.conan_ref_line_edit.setText(str(self._app_info.conan_ref))
        self._ui.exec_path_line_edit.setText(self._app_info.app_data["executable"])
        self._ui.is_console_app_checkbox.setChecked(self._app_info.is_console_application)
        self._ui.icon_line_edit.setText(self._app_info.app_data["icon"])
        self._ui.args_line_edit.setText(self._app_info.args)

        conan_options_text = ""
        for option in self._app_info.conan_options:
            conan_options_text += f"{option}={self._app_info.conan_options.get(option)}\n"
        self._ui.conan_opts_text_edit.setText(conan_options_text)

        self._ui.button_box.accepted.connect(self.save_edited_dialog)
        self.dialog.show()

    def save_edited_dialog(self):
        self._ui
