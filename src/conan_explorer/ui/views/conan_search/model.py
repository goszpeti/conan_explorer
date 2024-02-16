from typing import Dict, List, Optional

import conan_explorer.app as app
from conan_explorer.app import AsyncLoader  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper import ConanApi
from conan_explorer.conan_wrapper.types import ConanPkg
from conan_explorer.ui.common import TreeModel, TreeModelItem, get_platform_icon, get_themed_asset_icon
from conan_explorer.conan_wrapper.types import ConanRef
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Slot, SignalInstance

REF_TYPE = 0
PROFILE_TYPE = 1


class SearchedPackageTreeItem(TreeModelItem):
    """
    Represents a tree item of a Conan pkg.
    1. ref/id 2. remote 3. quick profile
    """

    def __init__(self, data: List[str], parent=None, pkg_data: Optional[ConanPkg] = None,
                 item_type=REF_TYPE, lazy_loading=False, installed=False, empty=False):
        super().__init__(data, parent, lazy_loading=lazy_loading)
        self.type = item_type
        self.pkg_data = pkg_data
        self.is_installed = installed
        self.empty = empty  # indicates a "no result" item, which must be handled separately

    def load_children(self):  # override
        # can't call super method: fetching would finish early
        self.child_items = []

        pkgs_to_be_added: Dict[str, SearchedPackageTreeItem] = {}
        for remote in self.data(1).split(","):
            recipe_ref = self.data(0)
            # cross reference with installed packages
            infos = app.conan_api.get_local_pkgs_from_ref(
                ConanRef.loads(recipe_ref))
            installed_ids = [info.get("id") for info in infos]
            packages = app.conan_api.get_remote_pkgs_from_ref(
                ConanRef.loads(recipe_ref), remote)
            for pkg in packages:
                pkg_id = pkg.get("id", "")
                if pkg_id in pkgs_to_be_added.keys():  # package already found in another remote
                    pkgs_to_be_added[pkg_id].item_data[1] += "," + remote
                    continue
                installed = False
                if pkg_id in installed_ids:
                    installed = True
                pkgs_to_be_added[pkg_id] = SearchedPackageTreeItem(
                    [pkg_id, remote,  ConanApi.build_conan_profile_name_alias(
                        pkg.get("settings", {}))],
                    self, pkg, PROFILE_TYPE, False, installed)
        for pkg in pkgs_to_be_added.values():
            self.child_items.append(pkg)
        if not self.child_items:
            self.child_items.append(SearchedPackageTreeItem(
                ["No package found", "",  ""], self, {}, PROFILE_TYPE, empty=True))
        self.is_loaded = True

    def child_count(self) -> int:  # override
        if self.type == REF_TYPE:
            return len(self.child_items) if len(self.child_items) > 0 else 1
        elif self.type == PROFILE_TYPE:
            return 0  # no child
        return 0  # for safety

    def get_conan_ref(self) -> str:
        if self.type == REF_TYPE:
            return self.data(0)
        elif self.type == PROFILE_TYPE:
            parent = self.parent()
            if parent is None:
                return ""
            return parent.data(0) + ":" + self.data(0)
        return ""


class PkgSearchModel(TreeModel):

    def __init__(self, conan_pkg_installed: Optional[SignalInstance] = None, conan_pkg_removed: Optional[SignalInstance] = None, *args, **kwargs):
        super(PkgSearchModel, self).__init__(*args, **kwargs)
        self.root_item = SearchedPackageTreeItem(
            ["Packages", "Remote(s)", "Quick Profile"])
        self.proxy_model = QtCore.QSortFilterProxyModel()  # for sorting
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)
        self._loader_widget_parent = None
        if conan_pkg_installed:
            conan_pkg_installed.connect(self.mark_pkg_as_installed)
        if conan_pkg_removed:
            conan_pkg_removed.connect(self.mark_pkg_as_not_installed)

    def setup_model_data(self, search_query: str, remotes: List[str]):
        # needs to be ConanRef, so we can check with get_all_local_refs directly
        self.clear_items()
        self.beginResetModel()
        recipes_with_remotes: Dict[ConanRef, str] = {}
        for remote in remotes:
            recipe_list = (app.conan_api.search_recipes_in_remotes(
                f"{search_query}*", remote_name=remote))
            for recipe in recipe_list:
                current_value = recipes_with_remotes.get(recipe, "")
                if current_value:
                    recipes_with_remotes[recipe] = current_value + "," + remote
                else:  # element 0
                    recipes_with_remotes[recipe] = remote

        if not recipes_with_remotes:
            self.root_item.append_child(SearchedPackageTreeItem(
                ["No package found!", "", ""], self.root_item, None,
                  PROFILE_TYPE, empty=True))
            return

        # add info if it is installed
        installed_refs = app.conan_api.get_all_local_refs()
        for recipe in recipes_with_remotes:
            recipe_remotes = recipes_with_remotes.get(recipe, "")
            installed = False
            if recipe in installed_refs:
                installed = True
            conan_item = SearchedPackageTreeItem(
                [str(recipe), recipe_remotes, ""], self.root_item, None, REF_TYPE, 
                lazy_loading=True, installed=installed)
            self.root_item.append_child(conan_item)
        self.endResetModel()

    def data(self, index: QtCore.QModelIndex, role: Qt.ItemDataRole):  # override
        if not index.isValid():
            return None
        item: SearchedPackageTreeItem = index.internalPointer()  # type: ignore
        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() != 0:  # only display icon for first column
                return
            if item.type == REF_TYPE:
                return QtGui.QIcon(get_themed_asset_icon("icons/package.svg"))
            if item.type == PROFILE_TYPE:
                profile_name = item.data(2)
                return get_platform_icon(profile_name)
        elif role == Qt.ItemDataRole.DisplayRole:
            return item.data(index.column())
        elif role == Qt.ItemDataRole.FontRole and item.is_installed:
            font = QtGui.QFont()
            font.setBold(True)
            return font
        return None

    def get_item_from_ref(self, conan_ref: str) -> Optional[SearchedPackageTreeItem]:
        for item in self.root_item.child_items:
            if item.item_data[0] == conan_ref:
                return item
        return None

    @Slot(str, str)
    def mark_pkg_as_installed(self, conan_ref: str, pkg_id: str):
        self._set_pkg_install_status(conan_ref, pkg_id, True)

    @Slot(str, str)
    def mark_pkg_as_not_installed(self, conan_ref: str, pkg_id: str):
        self._set_pkg_install_status(conan_ref, pkg_id, False)

    def _set_pkg_install_status(self, conan_ref: str, pkg_id: str, installed: bool):
        item = self.get_item_from_ref(conan_ref)
        if not item:
            return
        item.is_installed = installed
        pkg_items = item.child_items
        for pkg_item in pkg_items:
            if installed and pkg_item.pkg_data.get("id", "") == pkg_id:
                Logger().debug(
                    f"Set {pkg_id} as install status to {installed}")
                pkg_item.is_installed = installed
                break
            if not pkg_id and not installed:  # if ref was removed, all pkgs are deleted too
                pkg_item.is_installed = installed

    def fetchMore(self, index):  # override
        item = index.internalPointer()
        loader = AsyncLoader(self)
        self._loader_widget_parent = QtWidgets.QWidget()
        loader.async_loading(self._loader_widget_parent,
                             item.load_children, loading_text="Loading Packages...")
        loader.wait_for_finished()
