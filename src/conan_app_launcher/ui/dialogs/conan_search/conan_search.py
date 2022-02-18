import pprint
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.core import open_file
from conan_app_launcher.ui.common import QtLoaderObject
from conan_app_launcher.ui.common.icon import get_themed_asset_image
from conan_app_launcher.ui.dialogs.conan_install import ConanInstallDialog
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot

from .model import PROFILE_TYPE, PkgSearchModel, SearchedPackageTreeItem

Qt = QtCore.Qt

if TYPE_CHECKING:  # pragma: no cover
    from conan_app_launcher.ui.main_window import MainWindow


class ConanSearchDialog(QtWidgets.QDialog):
    conan_pkg_installed = QtCore.pyqtSignal(str, str)  # conan_ref, pkg_id
    conan_pkg_removed = QtCore.pyqtSignal(str, str)  # conan_ref, pkg_id

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, main_window: Optional["MainWindow"] = None):
        # Add minimize and maximize buttons
        super().__init__(parent,  Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        if main_window:
            self._main_window = main_window  # needed for signals and local pkg explorer, if started from main window
        else:
            self._main_window = self
        current_dir = Path(__file__).parent
        self._ui = uic.loadUi(current_dir / "conan_search.ui", baseinstance=self)
        self.setMinimumSize(650, 550)

        # init search bar
        icon = QtGui.QIcon(str(app.asset_path / "icons/icon.ico"))
        self.setWindowIcon(icon)

        self._ui.search_button.clicked.connect(self.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)
        self.search_action = QtWidgets.QAction("search", parent)
        self.search_action.setShortcut(QtGui.QKeySequence(Qt.Key_Enter))
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self.search_action)
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
        self._pkg_result_loader = QtLoaderObject(self)
        self._ui.search_results_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.search_results_tree_view.customContextMenuRequested.connect(self.on_pkg_context_menu_requested)
        self.apply_theme()

    def apply_theme(self):
        icon = QtGui.QIcon(get_themed_asset_image("icons/search_packages.png"))
        self._init_pkg_context_menu()
        self._ui.search_icon.setPixmap(icon.pixmap(20, 20))

    def load(self):  # TODO define interface for entrypoints
        pass

    def _enable_search_button(self):
        """ Enable search button from minimum 3 characters onwards"""
        if len(self._ui.search_line.text()) > 2:
            self._ui.search_button.setEnabled(True)
        else:
            self._ui.search_button.setEnabled(False)

    def _init_pkg_context_menu(self):
        """ Initalize context menu with all actions """
        self.select_cntx_menu = QtWidgets.QMenu()

        self.copy_ref_action = QtWidgets.QAction("Copy reference", self)
        self.copy_ref_action.setIcon(QtGui.QIcon(get_themed_asset_image("icons/copy_link.png")))
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self.on_copy_ref_requested)

        self.show_conanfile_action = QtWidgets.QAction("Show conanfile", self)
        self.show_conanfile_action.setIcon(QtGui.QIcon(get_themed_asset_image("icons/file_preview.png")))
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self.on_show_conanfile_requested)

        self.install_pkg_action = QtWidgets.QAction("Install package", self)
        self.install_pkg_action.setIcon(QtGui.QIcon(get_themed_asset_image("icons/download_pkg.png")))
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(self.on_install_pkg_requested)

        if self._main_window:
            self.show_in_pkg_exp_action = QtWidgets.QAction("Show in Package Explorer", self)
            self.show_in_pkg_exp_action.setIcon(QtGui.QIcon(
                get_themed_asset_image("icons/search_packages.png")))
            self.select_cntx_menu.addAction(self.show_in_pkg_exp_action)
            self.show_in_pkg_exp_action.triggered.connect(self.on_show_in_pkg_exp)

    @pyqtSlot(QtCore.QPoint)
    def on_pkg_context_menu_requested(self, position: QtCore.QPoint):
        """ 
        Executes, when context menu is requested. 
        This is done to dynamically grey out some options depending on the item type.
        """
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.empty:
            return
        if self._main_window:
            if item.is_installed:
                self.show_in_pkg_exp_action.setEnabled(True)
            else:
                self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec_(self._ui.search_results_tree_view.mapToGlobal(position))

    @pyqtSlot()
    def on_search(self):
        """ Search for the user entered text by re-initing the model"""
        # IMPORTANT! if put in async loading, the pyqt signal of the model will be created in another Qt thread
        # and not be able to emit to the GUI thread.
        conan_pkg_removed_signal = None
        if self._main_window:
            conan_pkg_removed_signal = self._main_window.conan_pkg_removed

        self._pkg_result_model = PkgSearchModel(self._main_window.conan_pkg_installed, conan_pkg_removed_signal)
        self._pkg_result_loader.async_loading(
            self, self._load_search_model, (), self._finish_load_search_model, "Searching for packages...")
        # reset info text
        self._ui.package_info_text.setText("")

    @pyqtSlot()
    def on_show_in_pkg_exp(self):
        """ Switch to the main gui and select the item (ref or pkg) in the Local Package Epxlorer. """
        if not self._main_window:
            return
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        self._main_window.local_package_explorer.select_local_package_from_ref(item.get_conan_ref(), refresh=True)

    def _load_search_model(self):
        """ Initialize tree view model by searching in conan """
        self._pkg_result_model.setup_model_data(self._ui.search_line.text(), self.get_selected_remotes())

    def _finish_load_search_model(self):
        """ After conan search adjust the view """
        self._ui.search_results_tree_view.setModel(self._pkg_result_model.proxy_model)
        self._ui.search_results_tree_view.setColumnWidth(0, 320)
        self._ui.search_results_tree_view.sortByColumn(1, Qt.AscendingOrder)  # sort by remote at default
        self._ui.search_results_tree_view.selectionModel().selectionChanged.connect(self.on_package_selected)

    @pyqtSlot()
    def on_package_selected(self):
        """ Display package info only for pkg ref"""
        item = self.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if not item.type == PROFILE_TYPE:
            return
        pkg_info = pprint.pformat(item.pkg_data).translate(
            {ord("{"): None, ord("}"): None, ord(","): None, ord("'"): None})
        self._ui.package_info_text.setText(pkg_info)

    @pyqtSlot()
    def on_copy_ref_requested(self):
        """ Copy the selected reference to the clipboard """
        combined_ref = self.get_selected_combined_ref()
        QtWidgets.QApplication.clipboard().setText(combined_ref)

    @pyqtSlot()
    def on_show_conanfile_requested(self):
        """ Show the conanfile by downloading and opening with the associated program """
        combined_ref = self.get_selected_combined_ref()
        conan_ref = combined_ref.split(":")[0]
        conanfile = app.conan_api.get_conanfile_path(ConanFileReference.loads(conan_ref))
        open_file(conanfile)

    @pyqtSlot()
    def on_install_pkg_requested(self):
        """ Spawn the Conan install dialog """
        combined_ref = self.get_selected_combined_ref()
        dialog = ConanInstallDialog(self, combined_ref, self._main_window.conan_pkg_installed)
        dialog.show()

    def get_selected_remotes(self) -> List[str]:
        """ Returns the user selected remotes """
        selected_remotes = []
        for i in range(self._ui.remote_list.count()):
            item = self._ui.remote_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_remotes.append(item.text())
        return selected_remotes

    def get_selected_combined_ref(self) -> str:
        """ Returns the user selected ref in <ref>:<id> format """
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
        """ Gets the selected item from a view """
        indexes = view.selectedIndexes()
        if not indexes:
            return None
        view_index = view.selectedIndexes()[0]
        source_item = view_index.model().mapToSource(view_index).internalPointer()
        return source_item
