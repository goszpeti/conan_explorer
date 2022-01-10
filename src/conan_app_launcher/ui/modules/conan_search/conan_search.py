import pprint
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from conans.model.ref import ConanFileReference

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher import asset_path
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from conan_app_launcher.ui.common import QtLoaderObject
from conan_app_launcher.components import open_file
from conan_app_launcher.ui.modules.conan_install import ConanInstallDialog
from .model import PROFILE_TYPE, PkgSearchModel, SearchedPackageTreeItem

Qt = QtCore.Qt

if TYPE_CHECKING:
    from conan_app_launcher.ui.modules.package_explorer import LocalConanPackageExplorer


class ConanSearchDialog(QtWidgets.QDialog):
    """  """

    # TODO local remote?
    # TODO Open Package folder of installed package

    def __init__(self, parent:Optional[QtWidgets.QWidget], local_package_explorer: "LocalConanPackageExplorer"=None):
        super().__init__(parent)
        self._local_package_explorer = local_package_explorer
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "conan_search.ui", baseinstance=self)
        self.setMinimumSize(550, 550)

        # init search bar
        icon = QtGui.QIcon(str(asset_path / "icons" / "search_packages.png"))
        self._ui.search_icon.setPixmap(icon.pixmap(20, 20))
        self._ui.search_button.clicked.connect(self.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)
        self.search_action = QtWidgets.QAction("search", parent)
        self.search_action.setShortcut(QtGui.QKeySequence(Qt.Key_Enter))
        # for the shortcut to work, the action has to be added to a higher level widget
        parent.addAction(self.search_action)
        self.search_action.triggered.connect(self.on_search)

        # init remotes list
        remotes = app.conan_api.get_remotes()
        for remote in remotes:
            item = QtWidgets.QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.checkState
        self._ui.remote_list.adjustSize()

        self._pkg_result_model = PkgSearchModel()
        self._pkg_result_loader = QtLoaderObject()

        self._ui.search_results_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.search_results_tree_view.customContextMenuRequested.connect(
            self.on_pkg_context_menu_requested)
        self._init_pkg_context_menu()

    def _enable_search_button(self):
        """ Enable search button from minimum 3 characters onwards"""
        if len(self._ui.search_line.text()) > 2:
            self._ui.search_button.setEnabled(True)
        else:
            self._ui.search_button.setEnabled(False)

    def _init_pkg_context_menu(self):
        self.select_cntx_menu = QtWidgets.QMenu()
        icons_path = asset_path / "icons"

        self.copy_ref_action = QtWidgets.QAction("Copy reference", self)
        self.copy_ref_action.setIcon(QtGui.QIcon(str(icons_path / "copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.on_copy_ref_requested)

        self.show_conanfile_action = QtWidgets.QAction("Show conanfile", self)
        self.show_conanfile_action.setIcon(QtGui.QIcon(str(icons_path / "file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self.on_show_conanfile_requested)

        self.install_pkg_action = QtWidgets.QAction("Install package", self)
        self.install_pkg_action.setIcon(QtGui.QIcon(str(icons_path / "download_pkg.png")))
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(self.on_install_pkg_requested)

        self.show_in_pkg_exp_action = QtWidgets.QAction("Show in Package Explorer", self)
        self.show_in_pkg_exp_action.setIcon(QtGui.QIcon(str(icons_path / "search_packages.png")))
        self.select_cntx_menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.triggered.connect(self.on_show_in_pkg_exp)

    def on_pkg_context_menu_requested(self, position):
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.is_installed:
            self.show_in_pkg_exp_action.setEnabled(True)
        else:
            self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec_(self._ui.search_results_tree_view.mapToGlobal(position))

    def on_search(self):
        #self._load_search_model()
        #self._finish_load_search_model()
        self._pkg_result_loader.async_loading(
             self, self._load_search_model, self._finish_load_search_model, "Searching for packages...")

    def on_show_in_pkg_exp(self):
        if not self._local_package_explorer:
            return
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        self._local_package_explorer.select_local_package_from_ref(item.get_conan_ref())
    
    def _load_search_model(self):
        self._pkg_result_model = PkgSearchModel()
        self._pkg_result_model.setup_model_data(self._ui.search_line.text(), self.get_selected_remotes())

    def _finish_load_search_model(self):
        self._ui.search_results_tree_view.setModel(self._pkg_result_model.proxy_model)
        self._ui.search_results_tree_view.resizeColumnToContents(0)
        self._ui.search_results_tree_view.sortByColumn(1, Qt.AscendingOrder)  # sort by remote at default
        self._ui.search_results_tree_view.selectionModel().selectionChanged.connect(self.on_package_selected)

    def on_package_selected(self):
        # display package info
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if not item.type == PROFILE_TYPE:
            return
        pkg_info = pprint.pformat(item.pkg_data).translate(
            {ord("{"): None, ord("}"): None, ord(","): None, ord("'"): None})
        self._ui.package_info_text.setText(pkg_info)

    def on_copy_ref_requested(self):
        conan_ref = self.get_selected_conan_ref()
        QtWidgets.QApplication.clipboard().setText(conan_ref)

    def on_show_conanfile_requested(self):
        conan_ref = self.get_selected_conan_ref()
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        open_file(conanfile)

    def on_install_pkg_requested(self):
        conan_ref = self.get_selected_conan_ref()
        dialog = ConanInstallDialog(self, conan_ref)
        dialog.exec_()

    def get_selected_remotes(self) -> List[str]:
        selected_remotes = []
        for i in range(self._ui.remote_list.count()):
            item = self._ui.remote_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_remotes.append(item.text())
        return selected_remotes

    def get_selected_conan_ref(self) -> str:
        # no need to map from postition, since rightclick selects a single item
        source_item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not source_item:
            return ""
        conan_ref_item = source_item
        id_str = ""
        if source_item.type == PROFILE_TYPE:
            conan_ref_item = source_item.parent()
            id_str = ":" + source_item.pkg_data.get("id", "")
        if not conan_ref_item:
            return ""
        return conan_ref_item.item_data[0] + id_str

    def get_selected_source_item(self, view) -> Optional[SearchedPackageTreeItem]:
        indexes = view.selectedIndexes()
        if not indexes:
            return None
        view_index = view.selectedIndexes()[0]
        source_item = view_index.model().mapToSource(view_index).internalPointer()
        return source_item
