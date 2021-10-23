import os.path as osp
import posixpath
import mimetypes
import time
from typing import Any, List, Union

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileIconProvider

FSMItemOrNone = Union["_FileSystemModelLiteItem", None]


def sizeof_fmt(num, suffix="B"):
    """Creates a human readable string from a file size"""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class _FileSystemModelLiteItem(object):
    """Represents a single node (drive, folder or file) in the tree"""

    def __init__(
        self,
        data: List[Any],
        icon=QFileIconProvider.Computer,
        parent: FSMItemOrNone = None,
    ):
        self._data: List[Any] = data
        self._icon = icon
        self._parent: _FileSystemModelLiteItem = parent
        self.child_items: List[_FileSystemModelLiteItem] = []

    def append_child(self, child: "_FileSystemModelLiteItem"):
        self.child_items.append(child)

    def child(self, row: int) -> FSMItemOrNone:
        try:
            return self.child_items[row]
        except IndexError:
            return None

    def child_count(self) -> int:
        return len(self.child_items)

    def column_count(self) -> int:
        return len(self._data)

    def data(self, column: int) -> Any:
        try:
            return self._data[column]
        except IndexError:
            return None

    def icon(self):
        return self._icon

    def row(self) -> int:
        if self._parent:
            return self._parent.child_items.index(self)
        return 0

    def parent_item(self) -> FSMItemOrNone:
        return self._parent


class FileSystemModelLite(QAbstractItemModel):
    def __init__(self, file_list: List[str], parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._icon_provider = QFileIconProvider()

        self._root_item = _FileSystemModelLiteItem(
            ["Name", "Size", "Type", "Modification Date"]
        )
        self._setup_model_data(file_list, self._root_item)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        item: _FileSystemModelLiteItem = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif index.column() == 0 and role == Qt.DecorationRole:
            return self._icon_provider.icon(item.icon())
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_item.data(section)
        return None

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item: _FileSystemModelLiteItem = index.internalPointer()
        parent_item: FSMItemOrNone = child_item.parent_item()

        if parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return parent.internalPointer().column_count()
        return self._root_item.column_count()

    def _setup_model_data(
        self, file_list: List[str], parent: "_FileSystemModelLiteItem"
    ):
        def _add_to_tree(_file_record, _parent: "_FileSystemModelLiteItem", root=False):
            item_name = _file_record["bits"].pop(0)
            for child in _parent.child_items:
                if item_name == child.data(0):
                    item = child
                    break
            else:
                data = [item_name, "", "", ""]
                if root:
                    icon = QFileIconProvider.Computer
                elif len(_file_record["bits"]) == 0:
                    icon = QFileIconProvider.File
                    data = [
                        item_name,
                        _file_record["size"],
                        _file_record["type"],
                        _file_record["modified_at"],
                    ]
                else:
                    icon = QFileIconProvider.Folder

                item = _FileSystemModelLiteItem(data, icon=icon, parent=_parent)
                _parent.append_child(item)

            if len(_file_record["bits"]):
                _add_to_tree(_file_record, item)

        for file in file_list:
            file_record = {
                "size": sizeof_fmt(osp.getsize(file)),
                "modified_at": time.strftime(
                    "%a, %d %b %Y %H:%M:%S %Z", time.localtime(osp.getmtime(file))
                ),
                "type": mimetypes.guess_type(file)[0],
            }

            drive = True
            if "\\" in file:
                file = posixpath.join(*file.split("\\"))
            bits = file.split("/")
            if len(bits) > 1 and bits[0] == "":
                bits[0] = "/"
                drive = False

            file_record["bits"] = bits
            _add_to_tree(file_record, parent, drive)


class Widget(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        file_list = [
            "C:\\",
        ]
        self._fileSystemModel = FileSystemModelLite(file_list, self)

        layout = QVBoxLayout(self)

        self._treeView = QTreeView(self)
        self._treeView.setModel(self._fileSystemModel)
        layout.addWidget(self._treeView)


if __name__ == "__main__":
    from sys import argv, exit
    from PyQt5.QtWidgets import QApplication

    a = QApplication(argv)
    w = Widget()
    w.show()
    exit(a.exec())
