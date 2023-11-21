from PySide6.QtWidgets import QLineEdit
from conan_explorer.ui.common import get_themed_asset_icon

class PasswordLineEdit(QLineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        # hide per default
        self.setEchoMode(self.EchoMode.Password)

        self.show_icon = get_themed_asset_icon("icons/show.svg")
        self.hide_icon = get_themed_asset_icon("icons/hide.svg")

        self.toggle_show_pw_action = self.addAction(self.show_icon, self.ActionPosition.TrailingPosition)
        self.toggle_show_pw_action.triggered.connect(self.on_toggle_show_password)
        self._pw_shown = False

    def on_toggle_show_password(self):
        if self._pw_shown:
            self.setEchoMode(self.EchoMode.Password)
            self._pw_shown = False
            self.toggle_show_pw_action.setIcon(self.show_icon)
        else:
            self.setEchoMode(self.EchoMode.Normal)
            self._pw_shown = True
            self.toggle_show_pw_action.setIcon(self.hide_icon)
