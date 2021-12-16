import pprint
from typing import Dict, List, Union
from conan_app_launcher.components import ConanApi
import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import asset_path
from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt

REF_TYPE = 0
PROFILE_TYPE = 1


class PackageFilter(QtCore.QSortFilterProxyModel):
    """ Filter packages but always showing the parent (ref) of the packages """

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
        '''
        Traverse to the root node and check if any of the
        ancestors match the filter
        '''
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        '''
        Starting from the current node as root, traverse all
        the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count = model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False


class PackageTreeItem(object):
    """
    Represents a tree item of a Conan pkg.
    Implemented like the default QT example.  # TODO Should be refactored in the future
    """

    def __init__(self, data: List[Union[str, Dict]], parent=None, item_type=REF_TYPE):
        self.parent_item = parent
        self.item_data = data
        self.type = item_type
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return len(self.item_data)

    def get_dummy_profile_name(self, column):
        if self.type == PROFILE_TYPE:
            return ConanApi.build_conan_profile_name_alias(self.item_data[column].get("settings", {}))

    def data(self, column):
        return self.item_data[column]

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)

        return 0


class PkgSelectModel(QtCore.QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super(PkgSelectModel, self).__init__(*args, **kwargs)
        self._icons_path = asset_path / "icons"
        self.root_item = PackageTreeItem(["Packages"])
        self.proxy_model = PackageFilter()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        self.setup_model_data()

    def setup_model_data(self):
        for conan_ref in app.conan_api.get_all_local_refs():
            conan_item = PackageTreeItem([str(conan_ref)], self.root_item)
            self.root_item.append_child(conan_item)
            infos = app.conan_api.get_local_pkgs_from_ref(conan_ref)
            for info in infos:
                pkg_item = PackageTreeItem([info], conan_item, PROFILE_TYPE)
                conan_item.append_child(pkg_item)

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
        if not index.isValid():
            return None
        item: PackageTreeItem = index.internalPointer()
        if role == Qt.ToolTipRole:
            if item.type == PROFILE_TYPE:
                data = item.data(0)
                # remove dict style print characters
                return pprint.pformat(data).translate({ord("{"): None, ord("}"): None, ord(","): None, ord("'"): None})
        if role == Qt.DecorationRole:
            if item.type == REF_TYPE:
                return QtGui.QIcon(str(self._icons_path / "package.png"))
            if item.type == PROFILE_TYPE:
                profile_name = item.get_dummy_profile_name(0)
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
            if item.type == REF_TYPE:
                return item.data(index.column())
            if item.type == PROFILE_TYPE:
                return item.get_dummy_profile_name(0)

        return None

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
