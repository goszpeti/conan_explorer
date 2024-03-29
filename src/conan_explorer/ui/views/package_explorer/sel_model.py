from enum import Enum
from typing import Any, List, Union

from PySide6.QtCore import (QModelIndex, QPersistentModelIndex,
                            QSortFilterProxyModel, Qt)
from PySide6.QtGui import QFont, QIcon
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.conan_wrapper import ConanApiFactory
from conan_explorer.conan_wrapper.types import (ConanPkg, ConanRef,
                                                pretty_print_pkg_info)
from conan_explorer.ui.common import (TreeModel, TreeModelItem,
                                      get_platform_icon, get_themed_asset_icon)


class PkgSelectionType(Enum):
    ref = 0
    pkg = 1
    editable = 2
    export = 3

class PackageTreeItem(TreeModelItem):
    """ Represents a tree item of a Conan pkg. To be used for the parent (ref) and the child (Profile)"""

    def __init__(self, data: List[str], parent=None, item_type=PkgSelectionType.ref, pkg_info={}):
        super().__init__(data, parent, lazy_loading=True)
        self.pkg_info: ConanPkg = pkg_info
        self.type = item_type

    @override
    def load_children(self):
        # can't call super method: fetching would finish early
        self.child_items = []
        pkg_item = PackageTreeItem(
            [], self, PkgSelectionType.export, ConanPkg())
        self.append_child(pkg_item)
        infos = app.conan_api.get_local_pkgs_from_ref(ConanRef.loads(self.data(0)))
        for info in infos:
            pkg_item = PackageTreeItem([], self, PkgSelectionType.pkg, info)
            self.append_child(pkg_item)
        self.is_loaded = True

    @override
    def child_count(self) -> int:
        if self.type == PkgSelectionType.ref:
            return len(self.child_items) if len(self.child_items) > 0 else 1
        return 0  # for safety

class PackageFilter(QSortFilterProxyModel):
    """ Filter packages but always showing the parent (ref) of the packages """

    def __init__(self):
        super().__init__()
        self.setFilterKeyColumn(0)

    @override
    def filterAcceptsRow(self, row_num, source_parent) -> bool:
        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True
        return False

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
        self.clear_items()
        self.beginResetModel()
        for conan_ref in app.conan_api.get_all_local_refs():
            conan_item = PackageTreeItem([str(conan_ref)], self.root_item)
            self.root_item.append_child(conan_item)
        for conan_ref in app.conan_api.get_editable_references():
            conan_item = PackageTreeItem(
                [str(conan_ref)], self.root_item, PkgSelectionType.editable)
            self.root_item.append_child(conan_item)
        self.endResetModel()

    @override
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = 0) -> Any:
        if not index.isValid():
            return None
        item: PackageTreeItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.ToolTipRole:
            if item.type == PkgSelectionType.pkg:
                # remove dict style print characters
                return pretty_print_pkg_info(item.pkg_info)
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

    def get_quick_profile_name(self, item: PackageTreeItem) -> str:
        return ConanApiFactory().build_conan_profile_name_alias(item.pkg_info.get("settings", {}))
