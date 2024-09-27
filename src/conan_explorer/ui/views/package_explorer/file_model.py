from pathlib import Path
from typing import List

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QColor, QFont
from typing_extensions import override

from conan_explorer.ui.common import FileSystemModel
from conan_explorer.ui.common.model import QAF


class CalFileSystemModel(FileSystemModel):
    def __init__(
        self, h_align=QAF.AlignLeft | QAF.AlignVCenter, v_align=QAF.AlignVCenter, parent=None
    ):
        super().__init__(h_align, v_align, parent)
        self._disabled_indexes = set()

    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.FontRole and self._row_is_disabled(index):
            font = QFont()
            font.setItalic(True)
            return font
        if role == Qt.ItemDataRole.ForegroundRole:
            try:
                if self._row_is_disabled(index):
                    return QColor(Qt.GlobalColor.gray)
            except Exception:
                pass
        return super().data(index, role)

    def _row_is_disabled(self, index: QModelIndex):
        return index in self._disabled_indexes

    def add_disabled_items(self, item_paths: List[str]):
        for item_path in item_paths:
            self._disabled_indexes.add(self.index(Path(item_path).as_posix(), 0))

    def clear_all_disabled_items(self):
        self._disabled_indexes = set()
