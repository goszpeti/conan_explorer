from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, Slot
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import QListWidgetItem, QMenu, QWidget
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.ui.common.syntax_highlighting import ConfigHighlighter
from conan_explorer.ui.plugin import PluginDescription, PluginInterfaceV1

from .controller import ConanSearchController

if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import PageStore
    from conan_explorer.ui.main_window import BaseSignals


class ConanSearchView(PluginInterfaceV1):
    MINIMUM_CHARS_FOR_SEARCH = 2  # for qt to work

    def __init__(
        self,
        parent: QWidget,
        plugin_description: PluginDescription,
        base_signals: Optional["BaseSignals"],
        page_widgets: Optional["PageStore"] = None,
    ):
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
            self._ui.search_results_tree_view,
            self._ui.search_line,
            self._ui.search_button,
            self._ui.remote_list,
            self._ui.package_info_text,
            conan_pkg_installed,
            conan_pkg_removed,
        )

        self._ui.search_button.clicked.connect(self._search_controller.on_search)
        self._ui.search_button.setEnabled(False)
        self._ui.install_button.clicked.connect(self._search_controller.on_install_button)
        self._ui.search_line.validator_enabled = False
        self._ui.search_line.textChanged.connect(self._enable_search_button)
        for key in (
            "Enter",
            "Return",
        ):
            self._search_shorcut = QShortcut(
                key, self._ui.search_line, self._ui.search_button.animateClick
            )
            self._search_shorcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

        # init remotes list
        self._init_remotes()
        if self._base_signals:
            self._base_signals.conan_remotes_updated.connect(self._init_remotes)
        self._ui.select_all_widget.itemChanged.connect(self.on_toggled_remotes_selection)

        self._ui.search_results_tree_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._ui.search_results_tree_view.customContextMenuRequested.connect(
            self.on_pkg_context_menu_requested
        )
        self._init_pkg_context_menu()
        # force_light_mode for disabled icon in dark mode
        self.set_themed_icon(
            self._ui.search_button, "icons/search.svg", size=(20, 20), force_light_mode=True
        )
        self.set_themed_icon(self._ui.install_button, "icons/download_pkg.svg", size=(20, 20))
        self._conan_config_highlighter = ConfigHighlighter(
            self._ui.package_info_text.document(), "yaml"
        )
        self._ui.frame.setMinimumHeight(0)
        self._ui.frame.setMaximumHeight(0)
        self.remote_toggle_animation = QPropertyAnimation(self._ui.frame, b"maximumHeight")

        # animation for expanding/collapsing remote list
        def start_animation(checked):
            arrow_type = Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
            max_height = self._ui.frame.sizeHint().height()
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

    def on_toggled_remotes_selection(self):
        for i in range(self._ui.remote_list.count()):
            item = self._ui.remote_list.item(i)
            item.setCheckState(self._ui.select_all_widget.item(0).checkState())

    def _enable_search_button(self):
        """Enable search button from minimum characters"""
        if len(self._ui.search_line.text()) >= self.MINIMUM_CHARS_FOR_SEARCH:
            self._ui.search_button.setEnabled(True)
            self.set_themed_icon(self._ui.search_button, "icons/search.svg", size=(20, 20))
        else:
            self._ui.search_button.setEnabled(False)
            self.set_themed_icon(
                self._ui.search_button, "icons/search.svg", size=(20, 20), force_light_mode=True
            )

    def _init_pkg_context_menu(self):
        """Initalize context menu with all actions"""
        self.select_cntx_menu = QMenu()
        self.copy_ref_action = QAction("Copy reference", self)
        self.set_themed_icon(self.copy_ref_action, "icons/copy_link.svg")
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self._search_controller.on_copy_ref_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.set_themed_icon(self.show_conanfile_action, "icons/file_preview.svg")
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(
            self._search_controller.on_show_conanfile_requested
        )

        self.install_pkg_action = QAction("Install package", self)
        self.set_themed_icon(self.install_pkg_action, "icons/download_pkg.svg")
        self.select_cntx_menu.addAction(self.install_pkg_action)
        self.install_pkg_action.triggered.connect(
            self._search_controller.on_install_pkg_requested
        )

        self.show_in_pkg_exp_action = QAction("Show in Package Explorer", self)
        self.set_themed_icon(self.show_in_pkg_exp_action, "icons/global/search_packages.svg")
        self.select_cntx_menu.addAction(self.show_in_pkg_exp_action)
        self.show_in_pkg_exp_action.triggered.connect(self.on_show_in_pkg_exp)

        self.diff_pkgs_action = QAction("Compare packages", self)
        self.set_themed_icon(self.diff_pkgs_action, "icons/difference.svg")
        self.select_cntx_menu.addAction(self.diff_pkgs_action)
        self.diff_pkgs_action.triggered.connect(self._search_controller.on_diff_requested)

    def reload_themed_icons(self):
        self._conan_config_highlighter = ConfigHighlighter(
            self._ui.package_info_text.document(), "yaml"
        )
        super().reload_themed_icons()

    @Slot(QPoint)
    def on_pkg_context_menu_requested(self, position: QPoint):
        """
        Executes, when context menu is requested.
        This is done to dynamically grey out some options depending on the item type.
        """
        items = self._search_controller.get_selected_source_items()
        if len(items) < 1:
            return
        elif len(items) < 2:
            self.diff_pkgs_action.setEnabled(False)
        else:
            self.diff_pkgs_action.setEnabled(True)

        item = items[0]
        if item.empty:
            return
        if item.is_installed:
            self.show_in_pkg_exp_action.setEnabled(True)
        else:
            self.show_in_pkg_exp_action.setEnabled(False)
        self.select_cntx_menu.exec(self._ui.search_results_tree_view.mapToGlobal(position))

    def on_show_in_pkg_exp(self):
        """Switch to the Package Explorer view and select the item (ref or pkg)
        Needs other view as ref, so will not be moved to controller.
        """
        from conan_explorer.ui.views import LocalConanPackageExplorer

        items = self._search_controller.get_selected_source_items()
        if len(items) != 1:
            return
        item = items[0]
        if not self._page_widgets:
            return
        self._page_widgets.get_page_by_type(
            LocalConanPackageExplorer
        ).select_local_package_from_ref(item.get_conan_ref())

    @override
    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self._search_controller._resize_search_result_columns()

    @override
    def showEvent(self, a0) -> None:
        # set cursor in search line when switching to this tab
        self._ui.search_line.setFocus()
        return super().showEvent(a0)
