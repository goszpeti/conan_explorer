import pprint
from typing import List, Union

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.core import ConanApi
from conan_app_launcher.core.conan import ConanPkg
from conan_app_launcher.ui.common import get_platform_icon, get_themed_asset_image, TreeModel, TreeModelItem
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from PyQt5.QtGui import QIcon

REF_TYPE = 0
PROFILE_TYPE = 1


class PackageFilter(QSortFilterProxyModel):
    """ Filter packages but always showing the parent (ref) of the packages """

    def __init__(self):
        super().__init__()
        self.setFilterKeyColumn(0)

    def filterAcceptsRow(self, row_num, source_parent):
        """ Overriding the parent function """

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


class PackageTreeItem(TreeModelItem):
    """ Represents a tree item of a Conan pkg. To be used for the parent (ref) and the child (Profile)"""

    def __init__(self, data: List[Union[str, ConanPkg]], parent=None, item_type=REF_TYPE):
        super().__init__(data, parent)
        self.type = item_type


class PkgSelectModel(TreeModel):

    def __init__(self, *args, **kwargs):
        super(PkgSelectModel, self).__init__(*args, **kwargs)
        self.root_item = PackageTreeItem(["Packages"])
        self.proxy_model = PackageFilter()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def setup_model_data(self):
        for conan_ref in app.conan_api.get_all_local_refs():
            conan_item = PackageTreeItem([str(conan_ref)], self.root_item)
            infos = app.conan_api.get_local_pkgs_from_ref(conan_ref)
            for info in infos:
                pkg_item = PackageTreeItem([info], conan_item, PROFILE_TYPE)
                conan_item.append_child(pkg_item)
            self.root_item.append_child(conan_item)

    def data(self, index: QModelIndex, role):  # override
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
                return QIcon(get_themed_asset_image("icons/package.png"))
            if item.type == PROFILE_TYPE:
                profile_name = self.get_quick_profile_name(item)
                return get_platform_icon(profile_name)
        if role == Qt.DisplayRole:
            if item.type == REF_TYPE:
                return item.data(index.column())
            if item.type == PROFILE_TYPE:
                return self.get_quick_profile_name(item)

        return None

    def get_quick_profile_name(self, item) -> str:
        return ConanApi.build_conan_profile_name_alias(item.data(0).get("settings", {}))
