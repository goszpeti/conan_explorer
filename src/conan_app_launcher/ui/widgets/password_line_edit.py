from pathlib import Path
from PyQt5.QtWidgets import QLineEdit, QApplication, QStyle
from PyQt5.QtGui import QIcon
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.common.icon import get_icon_from_image_file

class PasswordLineEdit(QLineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        # hide per default
        self.setEchoMode(QLineEdit.Password)

        self.show_icon = get_icon_from_image_file(Path(get_themed_asset_image("icons/show.png")))
        self.hide_icon = get_icon_from_image_file(Path(get_themed_asset_image("icons/hide.png")))

        self.toggle_show_pw_action = self.addAction(self.show_icon, QLineEdit.TrailingPosition)
        self.toggle_show_pw_action.triggered.connect(self.on_toggle_show_password)
        self._pw_shown = False

    def on_toggle_show_password(self):
        if self._pw_shown:
            self.setEchoMode(QLineEdit.Password)
            self._pw_shown = False
            self.toggle_show_pw_action.setIcon(self.show_icon)
        else:
            self.setEchoMode(QLineEdit.Normal)
            self._pw_shown = True
            self.toggle_show_pw_action.setIcon(self.hide_icon)
