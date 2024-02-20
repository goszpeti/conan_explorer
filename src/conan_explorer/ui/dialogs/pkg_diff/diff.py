
from pprint import pformat
from typing import Literal
from PySide6.QtWidgets import QDialog, QListWidgetItem
from PySide6.QtCore import Qt

from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanPkg
from conan_explorer.ui.common.syntax_highlighting import ConfigHighlighter


from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QTextCharFormat, QColor, QAction
from conan_explorer.ui.common.theming import ThemedWidget

from conan_explorer.ui.widgets import RoundedMenu
class ConfigDiffHighlighter(ConfigHighlighter):
    def __init__(self, parent, type: Literal['ini', 'yaml']) -> None:
        super().__init__(parent, type)
        self.modified_diffs = []
        self.added_diffs = []
        self.removed_diffs = []

    def reset_diff(self):
        self.modified_diffs = []
        self.added_diffs = []
        self.removed_diffs = []

    def highlightBlock(self, text: str):
        super().highlightBlock(text)
        key_format = QTextCharFormat()
        # clear all background color
        key_format.clearBackground()
        expression = QRegularExpression(".*")
        match = expression.match(text)
        self.setFormat(match.capturedStart(), match.capturedLength(), key_format)

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
        

class PkgDiffDialog(QDialog, ThemedWidget):

    def __init__(self, parent) -> None:
        QDialog.__init__(self, parent)
        ThemedWidget.__init__(self, None)
        from .diff_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self._left_content = {}
        self._right_content = {}
        self._item_data = []
        self.setWindowTitle("Compare Packages")
        self._highlight_diff = {}
        self._left_highlighter = ConfigDiffHighlighter(
            self._ui.left_text_browser.document(), "yaml")
        self._right_highlighter = ConfigDiffHighlighter(
            self._ui.right_text_browser.document(), "yaml")
        # self._diff_highlighter = ConfigHighlighter(
        #     self._ui.diff_text_browser.document(), "yaml")
        self._ui.button_box.accepted.connect(self.close)
        self.setWindowFlag( Qt.WindowType.WindowMaximizeButtonHint)

        self._ui.pkgs_list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.pkgs_list_widget.customContextMenuRequested.connect(
            self.on_pkg_context_menu_requested)
        self._init_pkg_context_menu()

        # set up changed left element connection
        self._ui.pkgs_list_widget.currentItemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        sel_item_id = item.data(0)
        if "*" in sel_item_id:
            return
        for item_data in self._item_data:
            if sel_item_id == item_data.get("id", ""):
                content = item_data
                break
        self.set_right_content(self.filter_display_content(content))
        self.update_diff()

    def add_diff_item(self, content: ConanPkg):
        """" """
        item_name = content.get("id", "Unknown")
        if self._ui.pkgs_list_widget.count() == 0: # first item
            item_name = "* " + item_name
            self.set_left_content(self.filter_display_content(content))
        elif self._ui.pkgs_list_widget.count() == 1: # second item
            self.set_right_content(self.filter_display_content(content))
        item = QListWidgetItem(item_name, self._ui.pkgs_list_widget)
        self._item_data.append(content)

    def filter_display_content(self, content: ConanPkg):
        new_content = {}
        new_content["settings"] = content.get("settings")
        new_content["options"] = content.get("options")
        new_content["requires"] = content.get("requires")
        return new_content

    def set_left_content(self, content):
        self._left_content = content
        pkg_info = pformat(content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.left_text_browser.setText(pkg_info)

    def set_right_content(self, content):
        self._right_content = content
        pkg_info = pformat(content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.right_text_browser.setText(pkg_info)

    def update_diff(self):
        # populate left diff item menu
        try:
            # reset diffs
            self._left_highlighter.reset_diff()
            self._right_highlighter.reset_diff()

            # set left and right content with first two diff elements
            from dictdiffer import diff
            pkg_diffs = list(diff(self._left_content, self._right_content))
            # filter other id 
            pkg_diffs = list(filter(lambda diff: diff[1] != "id", pkg_diffs))
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
            self._left_highlighter.rehighlight()
            self._right_highlighter.rehighlight()
        except Exception as e:
            Logger().error("Diffing crashed: " + str(e))

    def _init_pkg_context_menu(self):
        """ Initalize context menu with all actions """
        self.select_cntx_menu = RoundedMenu()

        self.set_ref_item = QAction("Set as reference", self)
        self.set_themed_icon(self.set_ref_item, "icons/copy_link.svg")
        self.select_cntx_menu.addAction(self.set_ref_item)
        self.set_ref_item.triggered.connect(self._set_ref_item)

    def _set_ref_item(self):
        items = self._ui.pkgs_list_widget.selectedItems()
        if not len(items) == 1:
            return
        self._clear_ref_item()
        sel_item = items[0]
        id = sel_item.data(0)
        for item in self._item_data:
            if item.get("id", "") == id:
                item_name = "* " + id
                sel_item.setData(0, item_name)
                self.set_left_content(self.filter_display_content(item))
                self.update_diff()
                return

    def _clear_ref_item(self):
        items = self._ui.pkgs_list_widget.findItems("* ", Qt.MatchFlag.MatchContains)
        item = items[0]
        item.setData(0, item.data(0).replace("* ", ""))

    def on_pkg_context_menu_requested(self, position):
        self.select_cntx_menu.exec(self._ui.pkgs_list_widget.mapToGlobal(position))
