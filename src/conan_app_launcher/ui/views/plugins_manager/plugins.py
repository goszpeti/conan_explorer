from typing import TYPE_CHECKING, Optional
from conan_app_launcher import AUTHOR, REPO_URL, __version__, asset_path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFrame, QLabel, QSizePolicy, QSpacerItem,
                             QVBoxLayout, QWidget)
from PyQt6.QtCore import QPoint, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import (QListWidgetItem, QWidget)
from conan_app_launcher.ui.fluent_window.plugins import PluginInterface
from conan_app_launcher.ui.widgets import RoundedMenu
from .controller import PluginController

from .plugins_ui import Ui_Form

if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals
class PluginsPage(PluginInterface):

    def __init__(self, parent: QWidget, base_signals: Optional["BaseSignals"]=None,
             page_widgets: Optional["FluentWindow.PageStore"]=None):
        super().__init__(parent)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setObjectName("plugin_manager")
        self._controller = PluginController(self._ui.plugins_tree_view)
        self._controller.update()
        self._ui.plugins_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self._ui.plugins_tree_view.customContextMenuRequested.connect(self.on_pkg_context_menu_requested)
        # self._init_pkg_context_menu()
        self.set_themed_icon(self._ui.add_plugin_button, "icons/plus_rounded.png")
        self.set_themed_icon(self._ui.remove_plugin_button, "icons/minus_rounded.png")
        self.set_themed_icon(self._ui.toggle_plugin_button, "icons/hide.png")

        self._controller.update()
        # self.set_themed_icon(self._ui.search_icon, "icons/search_packages.png", size=(20,20))
    
    # def _init_remote_context_menu(self):
    #     self._remotes_cntx_menu = RoundedMenu()
    #     self._copy_remote_action = QAction("Copy remote name", self)
    #     self._copy_remote_action.setIcon(QIcon(get_themed_asset_image("icons/copy_link.png")))
    #     self._remotes_cntx_menu.addAction(self._copy_remote_action)
    #     self._copy_remote_action.triggered.connect(self.on_copy_remote_name_requested)

    # @pyqtSlot(QPoint)
    # def on_pkg_context_menu_requested(self, position: QPoint):
    #     """ 
    #     Executes, when context menu is requested. 
    #     This is done to dynamically grey out some options depending on the item type.
    #     """
    #     item = self._search_controller.get_selected_source_item(self._ui.search_results_tree_view)
    #     if not item:
    #         return
    #     if item.empty:
    #         return
    #     if item.is_installed:
    #         self.show_in_pkg_exp_action.setEnabled(True)
    #     else:
    #         self.show_in_pkg_exp_action.setEnabled(False)
    #     self.select_cntx_menu.exec(self._ui.search_results_tree_view.mapToGlobal(position))

    # def resizeEvent(self, a0) -> None:  # override QtGui.QResizeEvent
    #     super().resizeEvent(a0)
    #     self._search_controller._resize_package_columns()

