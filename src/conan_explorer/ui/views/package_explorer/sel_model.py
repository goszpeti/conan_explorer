from enum import Enum
from typing import Any, List, Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QColor, QFont, QIcon
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer import conan_version
from conan_explorer.app.system import get_folder_size
from conan_explorer.conan_wrapper import ConanApiFactory
from conan_explorer.conan_wrapper.conan_cleanup import ConanCleanup
from conan_explorer.conan_wrapper.types import ConanPkg, ConanRef, pretty_print_pkg_info
from conan_explorer.ui.common import (
    TreeModel,
    TreeModelItem,
    get_platform_icon,
    get_themed_asset_icon,
)


class PkgSelectionType(Enum):
    ref = 0
    pkg = 1
    editable = 2
    export = 3

class PackageTreeItem(TreeModelItem):
    """ Represents a tree item of a Conan pkg. To be used for the parent (ref) and the child (Profile)"""

    def __init__(self, data: List[str], parent=None, item_type=PkgSelectionType.ref, pkg_info={}, invalid=False):
        super().__init__(data, parent, lazy_loading=True)
        self.pkg_info: ConanPkg = pkg_info
        self.type = item_type
        self.invalid = invalid
        if item_type == PkgSelectionType.pkg:
            self.item_data[0] = self.get_quick_profile_name()

    @override
    def load_children(self):
        # can't call super method: fetching would finish early
        self.child_items = []
        pkg_item = PackageTreeItem(
            ["export", "0"], self, PkgSelectionType.export, ConanPkg())
        pkg_item.is_loaded = True
        self.append_child(pkg_item)
        infos = app.conan_api.get_local_pkgs_from_ref(ConanRef.loads(self.data(0)))
        for info in infos:
            pkg_item = PackageTreeItem(["package", "0"], self, PkgSelectionType.pkg, info)
            pkg_item.is_loaded = True

            self.append_child(pkg_item)
        self.is_loaded = True

    @override
    def child_count(self) -> int:
        if self.type == PkgSelectionType.ref:
            return len(self.child_items) if len(self.child_items) > 0 else 1
        return 0  # for safety

    def get_quick_profile_name(self) -> str:
        return ConanApiFactory().build_conan_profile_name_alias(self.pkg_info.get("settings", {}))

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
    
    def lessThan(self, source_left: Union[QModelIndex, QPersistentModelIndex], 
                 source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        role = Qt.ItemDataRole.DisplayRole
        leftData = self.sourceModel().data(source_left, role)
        rightData = self.sourceModel().data(source_right, role)
        if leftData is None:
            return True
        elif rightData is None:
            return False
        try:
            leftData = float(leftData)
            rightData = float(rightData)
        except Exception:
            return super().lessThan(source_left, source_right)
        if type(leftData) != type(rightData): 
            # don't want to sort at all in these cases, False is just a copout ...
            # should warn user
            return False

        return leftData < rightData
class PkgSelectModel(TreeModel):

    def __init__(self, loader_signal):
        super(PkgSelectModel, self).__init__()
        # header
        self._loader_signal = loader_signal
        self._acc_size = 0
        self.root_item = PackageTreeItem(["Packages", "Size (MB)"])
        self.proxy_model = PackageFilter()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.show_sizes = False

    def setup_model_data(self):
        self.clear_items()
        self.beginResetModel()
        # get invalid remotes refs
        invalid_refs = []
        if conan_version.major == 1:
            invalid_refs = ConanCleanup(app.conan_api).gather_invalid_remote_metadata() # type: ignore
        for conan_ref in app.conan_api.get_all_local_refs():
            invalid = str(conan_ref) in invalid_refs
            conan_item = PackageTreeItem(
                [str(conan_ref), "0"], self.root_item, invalid=invalid)
            self.root_item.append_child(conan_item)
        for conan_ref in app.conan_api.get_editable_references():
            conan_item = PackageTreeItem(
                [str(conan_ref), "0"], self.root_item, PkgSelectionType.editable)
            self.root_item.append_child(conan_item)
        self.endResetModel()

    def get_size(self, item: PackageTreeItem):
        if item.parent_item is None:
            return
        if item.type not in [PkgSelectionType.pkg, PkgSelectionType.export]:
            return
        if not item.item_data:
            return
        if item.item_data[1] != "0":
            return

        conan_ref = ConanRef.loads(item.parent_item.data(0))
        if item.type == PkgSelectionType.export:
            pkg_path = app.conan_api.get_export_folder(conan_ref) # TODO can crash
        else:
            pkg_path = app.conan_api.get_package_folder(conan_ref, item.pkg_info.get("id", ""))
        self._loader_signal.emit(
            f"Calculating size for\n {str(conan_ref)}\n{self._acc_size:.1f} MB read.")
        size = get_folder_size(pkg_path)
        item.item_data[1] = f"{size:.3f}"
        acc_size = float(item.parent_item.item_data[1]) + size
        self._acc_size += size
        item.parent_item.item_data[1] =  f"{acc_size:.3f}"

    @override
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = 0) -> Any:
        if not index.isValid():
            return None
        item: PackageTreeItem = index.internalPointer()  # type: ignore
        if self.show_sizes:
            self.get_size(item)
        if role == Qt.ItemDataRole.ToolTipRole:
            if item.invalid:
                return "Invalid package metadata"
            if item.type == PkgSelectionType.pkg:
                # remove dict style print characters
                return pretty_print_pkg_info(item.pkg_info)

        elif role == Qt.ItemDataRole.DecorationRole:
            if index.column() != 0:
                return None
            if item.type == PkgSelectionType.ref:
                return QIcon(get_themed_asset_icon("icons/package.svg"))
            elif item.type == PkgSelectionType.editable:
                return QIcon(get_themed_asset_icon("icons/edit.svg"))
            elif item.type == PkgSelectionType.pkg:
                return get_platform_icon(item.data(index.column()))
            elif item.type == PkgSelectionType.export:
                return QIcon(get_themed_asset_icon("icons/export_notes.svg"))
        elif role == Qt.ItemDataRole.DisplayRole:
            if item.type == PkgSelectionType.editable:
                return item.data(index.column()) + " (editable)"
            else:
                return item.data(index.column())
        elif role == Qt.ItemDataRole.FontRole:
            if item.type == PkgSelectionType.editable:
                font = QFont()
                font.setItalic(True)
                return font
        elif role == Qt.ItemDataRole.ForegroundRole:
            if item.invalid:
                return QColor("red")
        return None
