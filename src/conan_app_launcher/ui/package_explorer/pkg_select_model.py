
from conan_app_launcher.components import ConanApi
import conan_app_launcher as this
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

REF_TYPE = 0
PROFILE_TYPE = 1


class PackageFilter(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setFilterKeyColumn(0)

    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''

        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True

        # Finally, check if any of the children match
        return self.has_accepted_children(row_num, source_parent)


    def filter_accepts_row_itself(self, row_num, parent):
        return super().filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
        ''' Traverse to the root node and check if any of the
            ancestors match the filter
        '''
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False


    def has_accepted_children(self, row_num, parent):
        ''' Starting from the current node as root, traverse all
            the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count = model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False

class TreeItem(object):
    def __init__(self, data: str, parent=None, item_type=REF_TYPE):
        self.parentItem = parent
        self.itemData = data
        self.type = item_type
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            if self.type == PROFILE_TYPE:
                return ConanApi.build_conan_profile_name_alias(self.itemData[column].get("settings", {}))
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class PkgSelectModel(QtCore.QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super(PkgSelectModel, self).__init__(*args, **kwargs)
        self._icons_path = this.asset_path / "icons"
        self.rootItem = TreeItem(["Packages"])
        self.proxy_model = PackageFilter()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        if not this.conan_api:
            this.conan_api = ConanApi()
        self.setupModelData()


    def setupModelData(self):
        for conan_ref in this.conan_api.get_all_local_refs():
            conan_item = TreeItem([str(conan_ref)], self.rootItem)
            self.rootItem.appendChild(conan_item)
            infos = this.conan_api.get_local_pkgs_from_ref(conan_ref)
            for info in infos:
                pkg_item = TreeItem([info], conan_item, PROFILE_TYPE)
                conan_item.appendChild(pkg_item)
   
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()


    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def data(self, index: QtCore.QModelIndex, role):
        if not index.isValid():
            return None
        item: TreeItem = index.internalPointer()

        if role == Qt.DecorationRole:
            if item.type == REF_TYPE:
                return QtGui.QIcon(str(self._icons_path / "package.png"))
            if item.type == PROFILE_TYPE:
                profile_name = item.data(0)
                if not profile_name:
                    return None
                profile_name = profile_name.lower()
                if "windows" in profile_name:
                    return QtGui.QIcon(str(self._icons_path / "windows.png"))
                elif "linux" in profile_name:
                    return QtGui.QIcon(str(self._icons_path / "linux.png"))
                elif "android" in profile_name:
                    return QtGui.QIcon(str(self._icons_path / "android.png"))
                elif "macos" in profile_name:
                    return QtGui.QIcon(str(self._icons_path / "mac_os.png"))
                elif "default" in profile_name:
                    return QtGui.QIcon(str(self._icons_path / "default_pkg.png"))
        if role == Qt.DisplayRole:
            return item.data(index.column())
        return None

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None
