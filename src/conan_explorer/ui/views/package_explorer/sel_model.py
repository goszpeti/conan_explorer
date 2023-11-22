from enum import Enum
from typing import List, Union

import conan_explorer.app as app  # using global module pattern
from conan_explorer.conan_wrapper import ConanApi
from conan_explorer.conan_wrapper.types import ConanPkg, pretty_print_pkg_info
from conan_explorer.ui.common import get_platform_icon, get_themed_asset_icon, TreeModel, TreeModelItem
from PySide6.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from PySide6.QtGui import QIcon, QFont


class PkgSelectionType(Enum):
    ref = 0
    pkg = 1
    editable = 2
    export = 3


class PackageTreeItem(TreeModelItem):
    """ Represents a tree item of a Conan pkg. To be used for the parent (ref) and the child (Profile)"""

    def __init__(self, data: List[Union[str, ConanPkg]], parent=None, item_type=PkgSelectionType.ref):
        super().__init__(data, parent)
        self.type = item_type


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


class PkgSelectModel(TreeModel):

    def __init__(self, *args, **kwargs):
        super(PkgSelectModel, self).__init__(*args, **kwargs)
        self.root_item = PackageTreeItem(["Packages"])
        self.proxy_model = PackageFilter()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def setup_model_data(self):
        for conan_ref in app.conan_api.get_all_local_refs():
            conan_item = PackageTreeItem([str(conan_ref)], self.root_item)
            pkg_item = PackageTreeItem(
                [ConanPkg()], conan_item, PkgSelectionType.export)
            conan_item.append_child(pkg_item)
            infos = app.conan_api.get_local_pkgs_from_ref(conan_ref)
            for info in infos:
                pkg_item = PackageTreeItem([info], conan_item, PkgSelectionType.pkg)
                conan_item.append_child(pkg_item)
            self.root_item.append_child(conan_item)
        for conan_ref in app.conan_api.get_editable_references():
            conan_item = PackageTreeItem(
                [str(conan_ref)], self.root_item, PkgSelectionType.editable)
            self.root_item.append_child(conan_item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):  # override
        if not index.isValid():
            return None
        item: PackageTreeItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.ToolTipRole:
            if item.type == PkgSelectionType.pkg:
                data = item.data(0)
                # remove dict style print characters
                return pretty_print_pkg_info(data)
        if role == Qt.ItemDataRole.DecorationRole:
            if item.type == PkgSelectionType.ref:
                return QIcon(get_themed_asset_icon("icons/package.svg"))
            elif item.type == PkgSelectionType.editable:
                return QIcon(get_themed_asset_icon("icons/edit.svg"))
            elif item.type == PkgSelectionType.pkg:
                profile_name = self.get_quick_profile_name(item)
                return get_platform_icon(profile_name)
            elif item.type == PkgSelectionType.export:
                return QIcon(get_themed_asset_icon("icons/export_notes.svg"))
        if role == Qt.ItemDataRole.DisplayRole:
            if item.type == PkgSelectionType.ref:
                return item.data(index.column())
            elif item.type == PkgSelectionType.editable:
                return item.data(index.column()) + " (editable)"
            elif item.type == PkgSelectionType.pkg:
                return self.get_quick_profile_name(item)
            elif item.type == PkgSelectionType.export:
                return "export"
        if role == Qt.ItemDataRole.FontRole:
            if item.type == PkgSelectionType.editable:
                font = QFont()
                font.setItalic(True)
                return font
        return None

    def get_quick_profile_name(self, item) -> str:
        return ConanApi.build_conan_profile_name_alias(item.data(0).get("settings", {}))
