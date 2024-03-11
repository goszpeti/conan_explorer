from pathlib import Path
from typing import List

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QColor, QFont
from typing_extensions import override

from conan_explorer.ui.common import FileSystemModel


class CalFileSystemModel(FileSystemModel):
    _disabled_rows: "set[int]" = set()

    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.FontRole:
            if self._row_is_disabled(index):
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
        return index.row() in self._disabled_rows

    def add_disabled_items(self, item_paths: List[str]):
        for item_path in item_paths:
             self._disabled_rows.add(self.index(Path(item_path).as_posix(), 0).row())

    def clear_all_disabled_items(self):
        self._disabled_rows = set()

    def clear_disabled_item(self, item_path: str):
        try:
            disabled_item = self.index(Path(item_path).as_posix(), 0).row()
            self._disabled_rows.remove(disabled_item)
        except Exception:
            pass # element not found
