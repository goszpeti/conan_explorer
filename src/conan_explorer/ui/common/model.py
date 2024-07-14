from typing import TYPE_CHECKING, Callable, List, Optional
from typing_extensions import override

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, SignalInstance
from PySide6.QtWidgets import QFileSystemModel

from conan_explorer.app.logger import Logger

QAF = Qt.AlignmentFlag
QORI = Qt.Orientation
QIDR = Qt.ItemDataRole

if TYPE_CHECKING:
    from typing import Self


def re_register_signal(signal: SignalInstance, slot: Callable):
    try:  # need to be removed, otherwise will be called multiple times
        signal.disconnect()
    except RuntimeError:
        # no way to check if it is connected and it will throw an error
        pass
    signal.connect(slot)


class FileSystemModel(QFileSystemModel):
    """ This fixes an issue with the header not being centered vertically """

    def __init__(self, h_align=QAF.AlignLeft | QAF.AlignVCenter,
                 v_align=QAF.AlignVCenter, parent=None):
        super().__init__(parent)
        self.alignments = {QORI.Horizontal: h_align, QORI.Vertical: v_align}

    @override
    def headerData(self, section, orientation, role):
        if role == QIDR.TextAlignmentRole:
            return self.alignments[orientation]
        elif role == QIDR.DecorationRole:
            return None
        else:
            return QFileSystemModel.headerData(self, section, orientation, role)


class TreeModelItem(object):
    """
    Represents a tree item for a model view with lazy loading.
    Implemented like the default QT example.
    """

    def __init__(self, data: List[str], parent: Optional["TreeModelItem"] = None, lazy_loading=False):
        self.parent_item = parent
        self.item_data = data
        self.child_items: List["Self"] = []
        self.is_loaded = not lazy_loading

    def append_child(self, item):
        self.child_items.append(item)

    def remove_child(self, item):
        self.child_items.remove(item)

    def get_child_item_row(self, item):
        return self.child_items.index(item)

    def child(self, row):
        try:
            return self.child_items[row]
        except Exception:
            return None

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return len(self.item_data)

    def data(self, column):
        return self.item_data[column]

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def load_children(self):
        self.child_items = []
        self.is_loaded = True

class TreeModel(QAbstractItemModel):
    """ Qt tree model to be used with TreeModelItem.
    Supports lazy loading, if TreeModelItem enables it."""

    def __init__(self, checkable=False, *args, **kwargs):
        super(TreeModel, self).__init__(*args, **kwargs)
        self.root_item = TreeModelItem([])
        self._checkable = checkable

    def clear_items(self):
        self.beginResetModel()
        self.root_item.child_items.clear()
        self.endResetModel()

    def add_item(self, item: TreeModelItem):  # to root_item
        child_count = self.root_item.child_count()
        item.parent_item = self.root_item
        self.beginInsertColumns(QModelIndex(), child_count, child_count)
        self.root_item.append_child(item)
        self.endInsertRows()

    def remove_item(self, item: TreeModelItem):  # from root_item
        item_index = self.get_index_from_item(item)
        self.beginRemoveRows(item_index.parent(), item_index.row(), item_index.row())
        self.root_item.remove_child(item)
        self.endRemoveRows()

    @override
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().column_count()  # type: ignore
        else:
            return self.root_item.column_count()

    @override
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)  # type: ignore
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    @override
    def data(self, index, role):
        raise NotImplementedError

    @override
    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()  # type: ignore

    @override
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if self._checkable:
            flags = flags | Qt.ItemFlag.ItemIsUserCheckable
        return flags

    @override
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    @override
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == QIDR.DisplayRole:
            return self.root_item.data(section)
        return None

    @override
    def canFetchMore(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        return not item.is_loaded  # enabled, if lazy loading is enabled

    @override
    def fetchMore(self, index):
        item = index.internalPointer()
        item.load_children()

    def get_index_from_item(self, item: TreeModelItem) -> QModelIndex:
        # find the row with the matching reference
        found_item = False
        ref_row = 0
        for ref_row in range(self.root_item.child_count()):
            current_item = self.root_item.child_items[ref_row]
            # always has one dummy child count
            for child_row in range(len(current_item.child_items)):
                current_child_item = current_item.child_items[child_row]
                if current_child_item == item:
                    found_item = True
                    parent_index = self.index(ref_row, 0, QModelIndex())
                    return self.index(child_row, 0, parent_index)
            if current_item == item:
                found_item = True
                return self.index(ref_row, 0, QModelIndex())
        if not found_item:
            Logger().debug(f"Cannot find {str(item)} in model")
            return QModelIndex()
        return self.index(ref_row, 0, QModelIndex())
