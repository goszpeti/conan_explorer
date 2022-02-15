from PyQt5 import QtCore


class TreeModelItem(object):
    """
    Represents a tree item for a model view with lazy loading.
    Implemented like the default QT example.
    """

    def __init__(self, data=[], parent=None, lazy_loading=False):
        self.parent_item = parent
        self.item_data = data
        self.child_items = []
        self.is_loaded = not lazy_loading

    def append_child(self, item):
        self.child_items.append(item)

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


class TreeModel(QtCore.QAbstractItemModel):
    """ Qt tree model to be used with TreeModelItem.
    Supports lazy loading, if TreeModelItem enables it."""

    def __init__(self, *args, **kwargs):
        super(TreeModel, self).__init__(*args, **kwargs)

    def columnCount(self, parent):  # override
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self.root_item.column_count()

    def index(self, row, column, parent):  # override
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def data(self, index: QtCore.QModelIndex, role):  # override
        raise NotImplementedError

    def rowCount(self, parent):  # override
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def flags(self, index):  # override
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):  # override
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def headerData(self, section, orientation, role):  # override
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root_item.data(section)

        return None

    def canFetchMore(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        return not item.is_loaded # enabled, if lazy loading is enabled

    def fetchMore(self, index):
        item = index.internalPointer()
        item.load_children()
