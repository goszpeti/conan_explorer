from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app
from conan_app_launcher.ui.common.syntax_highlighting import ConfigHighlighter  # using global module pattern
from conan_app_launcher.ui.plugin import PluginDescription, PluginInterfaceV1
from conan_app_launcher.ui.views import LocalConanPackageExplorer
from conan_app_launcher.ui.widgets import RoundedMenu
from PySide6.QtCore import QPoint, Qt, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import QListWidgetItem, QWidget

from .controller import ConanSearchController


if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


class ConanSearchView(PluginInterfaceV1):

    def __init__(self, parent: QWidget, plugin_description: PluginDescription, 
                 base_signals: Optional["BaseSignals"],
                 page_widgets: Optional["FluentWindow.PageStore"] = None):
        # Add minimize and maximize buttons
        super().__init__(parent, plugin_description, base_signals, page_widgets)
        from .conan_search_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.load_signal.connect(self.load)

    def load(self):
        conan_pkg_installed = None
        conan_pkg_removed = None
        if self._base_signals:
            conan_pkg_installed = self._base_signals.conan_pkg_installed
            conan_pkg_removed = self._base_signals.conan_pkg_removed

        self._search_controller = ConanSearchController(
            self._ui.search_results_tree_view, self._ui.search_line, self._ui.search_button, self._ui.remote_list,
            self._ui.package_info_text, conan_pkg_installed, conan_pkg_removed)

        self._ui.search_button.clicked.connect(self._search_controller.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.install_button.clicked.connect(self._search_controller.on_install_button)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)
        for key in ("Enter", "Return",):
            shorcut = QShortcut(key, self)
            shorcut.activated.connect(self._ui.search_button.animateClick)

        # init remotes list
        self._init_remotes()
        if self._base_signals:
            self._base_signals.conan_remotes_updated.connect(self._init_remotes)
        self._ui.search_results_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.search_results_tree_view.customContextMenuRequested.connect(self.on_pkg_context_menu_requested)
        self._init_pkg_context_menu()
        # force_light_mode for disabled icon in dark mode
        self.set_themed_icon(self._ui.search_button, "icons/search.svg", size=(20, 20), force_light_mode=True)
        self.set_themed_icon(self._ui.install_button, "icons/download_pkg.svg", size=(20, 20))
        self._conan_config_highlighter = ConfigHighlighter(self._ui.package_info_text.document(), "yaml")
        self._ui.remote_list.setMinimumHeight(0)
        self._ui.remote_list.setMaximumHeight(0)
        self.remote_toggle_animation = QPropertyAnimation(self._ui.remote_list, b"maximumHeight")

        # animation for expanding/collapsing remote list
        def start_animation(checked):
            arrow_type = Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
            max_height = self._ui.remote_list.sizeHint().height()
            start_height = 0 if checked else max_height
            end_height = max_height if checked else 0
            self._ui.remote_toggle_button.setArrowType(arrow_type)
            # self.toggleAnimation.setDirection(direction)
            self.remote_toggle_animation.setDuration(400)
            self.remote_toggle_animation.setStartValue(start_height)
            self.remote_toggle_animation.setEndValue(end_height)
            self.remote_toggle_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
            self.remote_toggle_animation.start()

        self._ui.remote_toggle_button.clicked.connect(start_animation)

    def _init_remotes(self):
        remotes = app.conan_api.get_remotes()
        self._ui.remote_list.clear()
        for remote in remotes:
            item = QListWidgetItem(remote.name, self._ui.remote_list)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)

    def _enable_search_button(self):
        """ Enable search button from minimum 3 characters onwards"""
        if len(self._ui.search_line.text()) > 2:
            self._ui.search_button.setEnabled(True)
            self.set_themed_icon(self._ui.search_button, "icons/search.svg", size=(20, 20))
        else:
            self._ui.search_button.setEnabled(False)
            self.set_themed_icon(self._ui.search_button, "icons/search.svg", size=(20, 20), force_light_mode=True)

    def _init_pkg_context_menu(self):
        """ Initalize context menu with all actions """
        self.select_cntx_menu = RoundedMenu()

        self.copy_ref_action = QAction("Copy reference", self)
        self.set_themed_icon(self.copy_ref_action, "icons/copy_link.svg")
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self._search_controller.on_copy_ref_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.set_themed_icon(self.show_conanfile_action, "icons/file_preview.svg")
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self._search_controller.on_show_conanfile_requested)

        self.install_pkg_action = QAction("Install package", self)
        self.set_themed_icon(self.install_pkg_action, "icons/download_pkg.svg")
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(self._search_controller.on_install_pkg_requested)

        self.show_in_pkg_exp_action = QAction("Show in Package Explorer", self)
        self.set_themed_icon(self.show_in_pkg_exp_action, "icons/global/search_packages.svg")
        self.select_cntx_menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.triggered.connect(self.on_show_in_pkg_exp)

    def reload_themed_icons(self):
        self._conan_config_highlighter = ConfigHighlighter(self._ui.package_info_text.document(), "yaml")
        super().reload_themed_icons()

    @Slot(QPoint)
    def on_pkg_context_menu_requested(self, position: QPoint):
        """ 
        Executes, when context menu is requested. 
        This is done to dynamically grey out some options depending on the item type.
        """
        item = self._search_controller.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if item.empty:
            return
        if item.is_installed:
            self.show_in_pkg_exp_action.setEnabled(True)
        else:
            self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec(self._ui.search_results_tree_view.mapToGlobal(position))

    def on_show_in_pkg_exp(self):
        """ Switch to the main gui and select the item (ref or pkg) in the Local Package Explorer. """
        item = self._search_controller.get_selected_source_item(self._ui.search_results_tree_view)
        if not item:
            return
        if not self._page_widgets:
            return
        self._page_widgets.get_page_by_type(LocalConanPackageExplorer).select_local_package_from_ref(
            item.get_conan_ref())

    def resizeEvent(self, a0) -> None:  # override QtGui.QResizeEvent
        super().resizeEvent(a0)
        self._search_controller._resize_package_columns()
