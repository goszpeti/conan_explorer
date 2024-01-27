
from pathlib import Path
from pprint import pformat, pprint
from typing import Any, Dict
from PySide6.QtWidgets import QDialog, QFileDialog
import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE
from conan_explorer.ui.common.syntax_highlighting import ConfigHighlighter

class PkgDiffDialog(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        from .diff_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self._left_content = {}
        self._right_content = {}
        self.setWindowTitle("Compare Packages")
        self._left_highlighter = ConfigHighlighter(
            self._ui.left_text_browser.document(), "yaml")
        self._right_highlighter = ConfigHighlighter(
            self._ui.right_text_browser.document(), "yaml")
        self._diff_highlighter = ConfigHighlighter(
            self._ui.diff_text_browser.document(), "yaml")
        self._ui.button_box.accepted.connect(self.close)

        # set up changed left element connection


    def add_diff_item(self):
        pass


    def set_left_content(self, content: Dict[str, Any]):
        self._left_content = content
        pkg_info = pformat(content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.left_text_browser.setText(pkg_info)

    def set_right_content(self, content: Dict[str, Any]):
        self._right_content = content
        pkg_info = pformat(content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.right_text_browser.setText(pkg_info)

    def update_diff(self):
        # populate left diff item menu

        # set left and right content with first two diff elements
        from dictdiffer import diff
        pkg_diff = list(diff(self._left_content, self._right_content))
        # filter other id 
        pkg_diff = list(filter(lambda diff: diff[1] != "id", pkg_diff))
        pkg_diff = list(map(lambda diff: diff[1:], pkg_diff))
        self._ui.diff_text_browser.setText(pformat(pkg_diff).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None}))