from typing import Dict, List, Optional, Union

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.core import ConanApi
from conan_app_launcher.core.conan import ConanPkg
from conan_app_launcher.ui.common.icon import get_platform_icon, get_themed_asset_image
from conan_app_launcher.ui.common.model import TreeModel, TreeModelItem
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtGui

Qt = QtCore.Qt


REF_TYPE = 0
PROFILE_TYPE = 1


class SearchedPackageTreeItem(TreeModelItem):
    """
    Represents a tree item of a Conan pkg.
    1. ref/id 2. remote 3. quick profile
    """

    def __init__(self, data: List[Union[str, str, str]], parent=None, pkg_data: Optional[ConanPkg] = None,
                 item_type=REF_TYPE, lazy_loading=False, installed=False, empty=False):
        super().__init__(data, parent, lazy_loading=lazy_loading)
        self.type = item_type
        self.pkg_data = pkg_data
        self.is_installed = installed
        self.empty = empty # indicates a "no result" item, which must be handled separately 

    def load_children(self):
        self.child_items = []

        pkgs_to_be_added: Dict[str, SearchedPackageTreeItem] = {}
        for remote in self.data(1).split(","):
            recipe_ref = self.data(0)
            # cross reference with installed packages
            infos = app.conan_api.get_local_pkgs_from_ref(ConanFileReference.loads(recipe_ref))
            installed_ids = [info.get("id") for info in infos]
            packages = app.conan_api.get_packages_in_remote(ConanFileReference.loads(recipe_ref), remote)
            for pkg in packages:
                id = pkg.get("id", "")
                if id in pkgs_to_be_added.keys(): # package already found in another remote
                    pkgs_to_be_added[id].item_data[1] += "," + remote
                    continue
                installed = False
                if id in installed_ids:
                    installed = True
                pkgs_to_be_added[id] = SearchedPackageTreeItem(
                    [id, remote,  ConanApi.build_conan_profile_name_alias(pkg.get("settings", {}))],
                     self, pkg, PROFILE_TYPE, False, installed)
        for pkg in pkgs_to_be_added.values():
            self.child_items.append(pkg)
        if not self.child_items:
            self.child_items.append(SearchedPackageTreeItem(
                ["No package found", "",  ""], self, {}, PROFILE_TYPE, empty=True))
        self.is_loaded = True

    def child_count(self):
        if self.type == REF_TYPE:
            return len(self.child_items) if len(self.child_items) > 0 else 1
        elif self.type == PROFILE_TYPE:
            return 0  # no child

    def get_conan_ref(self) -> str:
        if self.type == REF_TYPE:
            return self.data(0)
        elif self.type == PROFILE_TYPE:
            return self.parent().data(0) + ":" + self.data(0)
        return ""

class PkgSearchModel(TreeModel):

    def __init__(self, *args, **kwargs):
        super(PkgSearchModel, self).__init__(*args, **kwargs)
        self.root_item = SearchedPackageTreeItem(["Packages", "Remote(s)", "Quick Profile"])
        self.proxy_model = QtCore.QSortFilterProxyModel()  # for sorting
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setSourceModel(self)

    def setup_model_data(self, search_query, remotes=[]):
        recipes_with_remotes: Dict[ConanFileReference, str] = {}
        for remote in remotes:
            # todo case insensitive
            recipe_list = (app.conan_api.search_query_in_remotes(
                f"{search_query}*", remote=remote))
            for recipe in recipe_list:
                current_value = recipes_with_remotes.get(str(recipe), "")
                if current_value:
                    recipes_with_remotes[recipe] = current_value + "," + remote
                else:  # element 0
                    recipes_with_remotes[recipe] = remote

        if not recipes_with_remotes:
            self.root_item.append_child(SearchedPackageTreeItem(
                ["No package found!", "", ""], self.root_item, None, PROFILE_TYPE, empty=True))
            return

        installed_refs = app.conan_api.get_all_local_refs()
        for recipe in recipes_with_remotes:
            remotes = recipes_with_remotes.get(recipe, "")
            installed = False
            if recipe in installed_refs:
                installed = True
            conan_item = SearchedPackageTreeItem(
                [str(recipe), remotes, ""], self.root_item, None, REF_TYPE, lazy_loading=True, installed=installed)
            self.root_item.append_child(conan_item)

    def data(self, index: QtCore.QModelIndex, role):  # override
        if not index.isValid():
            return None
        item: SearchedPackageTreeItem = index.internalPointer()
        if role == Qt.DecorationRole:
            if index.column() != 0:  # only display icon for first column
                return
            if item.type == REF_TYPE:
                return QtGui.QIcon(get_themed_asset_image("icons/package.png"))
            if item.type == PROFILE_TYPE:
                profile_name = item.data(2)
                return get_platform_icon(profile_name)
        elif role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.FontRole:
            if item.is_installed:
                font = QtGui.QFont()
                font.setBold(True)
                return font
        return None
