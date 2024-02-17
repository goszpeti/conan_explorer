
from pathlib import Path
from pprint import pformat, pprint
from typing import Any, Dict, Literal, Union
from PySide6.QtWidgets import QDialog, QFileDialog
import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE
from conan_explorer.ui.common.syntax_highlighting import ConfigHighlighter


from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
class ConfigDiffHighlighter(ConfigHighlighter):
    def __init__(self, parent, type: Literal['ini', 'yaml']) -> None:
        super().__init__(parent, type)
        self.modified_diffs = []
        self.added_diffs = []
        self.removed_diffs = []

    def highlightBlock(self, text: str):
        super().highlightBlock(text)
        key_format = QTextCharFormat()

        for diff_item in self.modified_diffs:
            key_format.setBackground(QColor("orange"))
            expression = QRegularExpression(diff_item)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)
        for diff_item in self.added_diffs:
            key_format.setBackground(QColor("green"))
            expression = QRegularExpression(diff_item)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)
        for diff_item in self.removed_diffs:
            key_format.setBackground(QColor("red"))
            expression = QRegularExpression(diff_item)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)


class PkgDiffDialog(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        from .diff_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self._left_content = {}
        self._right_content = {}
        self.setWindowTitle("Compare Packages")
        self._highlight_diff = {}
        self._left_highlighter = ConfigDiffHighlighter(
            self._ui.left_text_browser.document(), "yaml")
        self._right_highlighter = ConfigDiffHighlighter(
            self._ui.right_text_browser.document(), "yaml")
        # self._diff_highlighter = ConfigHighlighter(
        #     self._ui.diff_text_browser.document(), "yaml")
        self._ui.button_box.accepted.connect(self.close)

        # set up changed left element connection

    def add_diff_item(self):
        """" """
        # add ref item tree (1 item)
        # add comparison items


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
        try:
            # set left and right content with first two diff elements
            from dictdiffer import diff
            pkg_diffs = list(diff(self._left_content, self._right_content))
            # filter other id 
            pkg_diffs = list(filter(lambda diff: diff[1] != "id", pkg_diffs))
            # pkg_diffs = list(map(lambda diff: diff[1:], pkg_diffs))
            for pkg_diff in pkg_diffs:
                diff_mode = pkg_diff[0]
                if diff_mode == "change":
                    if isinstance(pkg_diff[1], list):
                        key = str(pkg_diff[-1][1].split(".")[-1])
                    else:
                        key = str(pkg_diff[1].split(".")[-1])
                    value_left = str(pkg_diff[2][0])
                    value_right = str(pkg_diff[2][1])
                elif diff_mode == "add":
                    for detail_diff in pkg_diff[2]:
                        key = str(detail_diff[0])
                        value_right = str(detail_diff[1])
                        value_left = "INVALID"
                        self._left_highlighter.added_diffs.append(f"({key}: {value_left})")
                        self._right_highlighter.added_diffs.append(
                            f"({key}: {value_right})")
                elif diff_mode == "remove":
                    for detail_diff in pkg_diff[2]:
                        key = str(detail_diff[0])
                        value_left = str(detail_diff[1])
                        value_right = "INVALID"
                        self._left_highlighter.removed_diffs.append(f"({key}: {value_left})")
                        self._right_highlighter.removed_diffs.append(
                            f"({key}: {value_right})")
                self._left_highlighter.modified_diffs.append(f"({key}: {value_left})")
                self._right_highlighter.modified_diffs.append(f"({key}: {value_right})")
            # self._ui.diff_text_browser.setText(pformat(pkg_diffs).translate(
            #     {ord("{"): None, ord("}"): None, ord("'"): None}))
            self._left_highlighter.rehighlight()
            self._right_highlighter.rehighlight()
            # self._ui.left_text_browser.setText(self._ui.left_text_browser.textChanged())
            # self._ui.right_text_browser.setText(pkg_info)
        except Exception as e:
            Logger().error("Diffing crashed: " + str(e))