
from conan_app_launcher.components import ConanApi
import conan_app_launcher as this
from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt

REF_TYPE = 0
PROFILE_TYPE = 1

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
        self.setupModelData()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)

    def setupModelData(self):
        for conan_ref in ConanApi().get_all_local_refs():
            conan_item = TreeItem([str(conan_ref)], self.rootItem)
            self.rootItem.appendChild(conan_item)
            for pkg in ConanApi().get_local_pkgs_from_ref(conan_ref):
                pkg_item = TreeItem([pkg], conan_item, PROFILE_TYPE)
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
