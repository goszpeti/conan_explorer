
from pprint import pformat
from typing import Literal
from typing_extensions import override

from dictdiffer import diff
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QAction, QColor, QShowEvent, QTextCharFormat
from PySide6.QtWidgets import QDialog, QListWidgetItem, QMenu

from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanPkg
from conan_explorer.ui.common.syntax_highlighting import ConfigHighlighter
from conan_explorer.ui.common.theming import ThemedWidget


class ConfigDiffHighlighter(ConfigHighlighter):
    """ Syntax highlighter to highlight the differences of a dict with different
    background colors (modified, added, removed)"""
    DIFF_NEW_COLOR = QColor("green")
    DIFF_REMOVED_COLOR = QColor("red")
    DIFF_MODIFIED_COLOR = QColor("orange")

    def __init__(self, parent, type: Literal['ini', 'yaml']) -> None:
        super().__init__(parent, type)
        self._reset_diff()

    def _reset_diff(self):
        self.modified_diffs = []
        self.added_diffs = []
        self.removed_diffs = []

    @override
    def highlightBlock(self, text: str):
        super().highlightBlock(text)
        key_format = QTextCharFormat()
        # clear all background color
        key_format.clearBackground()
        expression = QRegularExpression(".*")
        match = expression.match(text)
        self.setFormat(match.capturedStart(), match.capturedLength(), key_format)

        for diff_item in self.modified_diffs:
            key_format.setBackground(self.DIFF_MODIFIED_COLOR)
            expression = QRegularExpression(diff_item)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)
        for diff_item in self.added_diffs:
            key_format.setBackground(self.DIFF_NEW_COLOR)
            expression = QRegularExpression(diff_item)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)
        for diff_item in self.removed_diffs:
            key_format.setBackground(self.DIFF_REMOVED_COLOR)
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
        # TODO test out dialog._ui.left_text_browser.AutoFormattingFlag
        self._init_pkg_context_menu()

        self.setWindowTitle("Compare Packages")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)

        self._left_content = {}
        self._right_content = {}
        self._item_data = []

        self._left_highlighter = ConfigDiffHighlighter(
            self._ui.left_text_browser.document(), "yaml")
        self._right_highlighter = ConfigDiffHighlighter(
            self._ui.right_text_browser.document(), "yaml")
        self._ui.button_box.accepted.connect(self.close)

        self._ui.pkgs_list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.pkgs_list_widget.customContextMenuRequested.connect(
            self.on_pkg_context_menu_requested)

        # set up changed left element connection
        self._ui.pkgs_list_widget.currentItemChanged.connect(self._on_item_changed)

    def _init_pkg_context_menu(self):
        """ Initalize context menu with all actions """
        self.select_cntx_menu = QMenu()

        self.set_ref_item = QAction("Set as reference", self)
        self.set_themed_icon(self.set_ref_item, "icons/copy_link.svg")
        self.select_cntx_menu.addAction(self.set_ref_item)
        self.set_ref_item.triggered.connect(self._set_ref_item)

    def on_pkg_context_menu_requested(self, position):
        self.select_cntx_menu.exec(self._ui.pkgs_list_widget.mapToGlobal(position))

    @override
    def showEvent(self, event: QShowEvent) -> None:
        self._populate_left_items()
        self.update_diff()
        return super().showEvent(event)

    # public methods

    def add_diff_item(self, content: ConanPkg):
        """" """
        self._item_data.append(content)

    def update_diff(self):
        """ Resets the syntax highlighting, adds the different category items
        to the SyntaxHighlighter and then redraws them """
        try:
            # reset diffs
            self._left_highlighter._reset_diff()
            self._right_highlighter._reset_diff()

            # set left and right content with first two diff elements
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
                        self._left_highlighter.added_diffs.append(
                            f"({key}: {value_left})")
                        self._right_highlighter.added_diffs.append(
                            f"({key}: {value_right})")
                elif diff_mode == "remove":
                    for detail_diff in pkg_diff[2]:
                        key = str(detail_diff[0])
                        value_left = str(detail_diff[1])
                        value_right = "INVALID"
                        self._left_highlighter.removed_diffs.append(
                            f"({key}: {value_left})")
                        self._right_highlighter.removed_diffs.append(
                            f"({key}: {value_right})")
                self._left_highlighter.modified_diffs.append(f"({key}: {value_left})")
                self._right_highlighter.modified_diffs.append(f"({key}: {value_right})")
            self._left_highlighter.rehighlight()
            self._right_highlighter.rehighlight()
        except Exception as e:
            Logger().error("Diffing crashed: " + str(e))

    # internals

    def _on_item_changed(self, item: QListWidgetItem):
        """ Set right content, when selection changes """
        if not item:
            return
        sel_item_id = item.data(0)
        if "*" in sel_item_id:
            self._set_right_content(self._left_content)
            self.update_diff()
            return
        for item_data in self._item_data:
            if sel_item_id == item_data.get("id", ""):
                content = item_data
                self._set_right_content(content)
                self.update_diff()
                return

    def _filter_display_content(self, content: ConanPkg):
        """ Only allow the following keys in the view"""
        new_content = {}
        new_content["settings"] = content.get("settings")
        new_content["options"] = content.get("options")
        new_content["requires"] = content.get("requires")
        return new_content

    def _set_left_content(self, content):
        self._left_content = self._filter_display_content(content)
        pkg_info = pformat(self._left_content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.left_text_browser.setText(pkg_info)

    def _set_right_content(self, content):
        self._right_content = self._filter_display_content(content)
        pkg_info = pformat(self._right_content).translate(
            {ord("{"): None, ord("}"): None, ord("'"): None})
        self._ui.right_text_browser.setText(pkg_info)

    def _set_ref_item(self):
        """ Change the reference (*, left content) """
        items = self._ui.pkgs_list_widget.selectedItems()
        if len(items) != 1:
            return
        sel_item = items[0]
        pkg_id = sel_item.data(0)
        for item in self._item_data:
            if item.get("id", "") == pkg_id:
                idx = self._item_data.index(item)
                self._item_data.pop(idx)
                self._item_data.insert(0, item)
                self._set_left_content(item)
                break
        self._ui.pkgs_list_widget.clear()
        self._populate_left_items()
        self.update_diff()

    def _populate_left_items(self):
        ref = self._set_diff_list_prios()

        self._set_left_content(ref)
        QListWidgetItem("* " + ref.get("id", "Unknown"), self._ui.pkgs_list_widget)
        for prio in range(0, 5):
            for content in self._item_data:
                if prio == content["prio"]:
                    item_name = content.get("id", "Unknown")
                    QListWidgetItem(item_name, self._ui.pkgs_list_widget)

        self._set_right_content(self._item_data[1])
        # select 2nd item so we see a diff per default
        self._ui.pkgs_list_widget.setCurrentRow(1)


    def _set_diff_list_prios(self):
        """ Prioritize the list elements depending on the similarity of the original package
            Supports the most common settings.
            No option support yet.
        """
        ref = self._item_data[0]
        ref["prio"] = -1

        item_data_len = len(self._item_data)
        for i in range(1, item_data_len):
            content = self._item_data[i]
            pkg_diffs = list(diff(ref, content))
            pkg_arch_diffs = list(
                filter(lambda diff: diff[1] == "settings.arch", pkg_diffs))
            content["prio"] = 5
            if pkg_arch_diffs:
                content["prio"] = 4
                continue
            pkg_os_diffs = list(
                filter(lambda diff: diff[1] == "settings.os", pkg_diffs))
            if pkg_os_diffs:
                content["prio"] = 3
                continue
            pkg_compiler_diffs = list(
                filter(lambda diff: diff[1] == "settings.compiler", pkg_diffs))
            if pkg_compiler_diffs:
                content["prio"] = 2
                continue
            pkg_compiler_version_diffs = list(
                filter(lambda diff: diff[1] == ['settings', 'compiler.version'], pkg_diffs))
            if pkg_compiler_version_diffs:
                content["prio"] = 1
                continue
            if not pkg_compiler_version_diffs:
                content["prio"] = 0
        return ref
