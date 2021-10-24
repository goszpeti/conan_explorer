
from conan_app_launcher.components import ConanApi
import conan_app_launcher as this
from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


class ConanFilterProxyModel(QtCore.QSortFilterProxyModel):
    FILTERED_ITEMS = [".lock", ".count", "metadata.json",
                      "conaninfo.txt", "conanmanifest.txt"  # TODO ??
                      ]

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        # filter out internal files
        # index = self.sourceModel().index(source_row, 0, source_parent)
        # # model_index = self.mapToSource(index)
        # name = self.sourceModel().fileName(index)
        # if self.sourceModel().fileInfo(index).isDir():
        #     return True

        # for item in self.FILTERED_ITEMS:
        #     if item in name:
        #         return False
        return True

    def sourceFileInfo(self, index):
        return super().sourceFileInfo(index)

REF_TYPE = 0
PROFILE_TYPE = 1

class TreeItem(object):
    def __init__(self, data, parent=None, type=REF_TYPE):
        self.parentItem = parent
        self.itemData = data
        self.type = type
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
        self.proxy_model = ConanFilterProxyModel()
        self.proxy_model.setDynamicSortFilter(False)
        self.proxy_model.setSourceModel(self)

    def setupModelData(self):
        for conan_ref in ConanApi().get_all_local_refs():
            conan_item = TreeItem([str(conan_ref)], self.rootItem)
            self.rootItem.appendChild(conan_item)
            for pkg in ConanApi().get_local_pkgs_from_ref(conan_ref):
                pkg_alias = ConanApi.build_conan_profile_name_alias(pkg.get("settings", {}))
                pkg_item = TreeItem([pkg_alias], conan_item, PROFILE_TYPE)
                conan_item.appendChild(pkg_item)


    # def sort(self, col, order=QtCore.Qt.AscendingOrder):

    #     # Storing persistent indexes
    #     self.layoutAboutToBeChanged.emit()
    #     oldIndexList = self.persistentIndexList()
    #     oldIds = self._dfDisplay.index.copy()

    #     # Sorting data
    #     column = self._dfDisplay.columns[col]
    #     ascending = (order == QtCore.Qt.AscendingOrder)
    #     if column in self._sortBy:
    #         i = self._sortBy.index(column)
    #         self._sortBy.pop(i)
    #         self._sortDirection.pop(i)
    #     self._sortBy.insert(0, column)
    #     self._sortDirection.insert(0, ascending)
    #     self.updateDisplay()

    #     # Updating persistent indexes
    #     newIds = self._dfDisplay.index
    #     newIndexList = []
    #     for index in oldIndexList:
    #         id = oldIds[index.row()]
    #         newRow = newIds.get_loc(id)
    #         newIndexList.append(self.index(newRow, index.column(), index.parent()))
    #     self.changePersistentIndexList(oldIndexList, newIndexList)
    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

   
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
                profile_name = item.data(index.column()).lower()
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
