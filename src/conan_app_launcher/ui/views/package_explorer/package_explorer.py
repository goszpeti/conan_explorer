import os
from typing import TYPE_CHECKING

from conan_app_launcher.ui.common.model import re_register_signal
from conan_app_launcher.ui.plugin import PluginDescription, PluginInterfaceV1
from conan_app_launcher.ui.views.package_explorer.controller import PackageFileExplorerController, PackageSelectionController
from conan_app_launcher.ui.widgets import RoundedMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShowEvent, QResizeEvent, QAction
from PySide6.QtWidgets import QWidget


if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


class LocalConanPackageExplorer(PluginInterfaceV1):
    conan_pkg_selected = Signal(str, dict)  # conan_ref, ConanPkg -> needs dict for Qt to resolve it

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: "BaseSignals", page_widgets: "FluentWindow.PageStore"):
        super().__init__(parent, plugin_description, base_signals, page_widgets)
        from .package_explorer_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.load_signal.connect(self.load)

    def load(self):
        assert self._base_signals
        assert self._page_widgets
        self._pkg_sel_ctrl = PackageSelectionController(
            self, self._ui.package_select_view, self._ui.package_filter_edit,
            self.conan_pkg_selected, self._base_signals, self._page_widgets)
        self._pkg_file_exp_ctrl = PackageFileExplorerController(
            self, self._ui.package_file_view, self._ui.package_path_label,
            self.conan_pkg_selected, self._base_signals, self._page_widgets)
        self.file_cntx_menu = None
        self.set_themed_icon(self._ui.refresh_button, "icons/refresh.svg")

        # connect pkg selection controller
        self._ui.package_select_view.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self._ui.package_select_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.package_select_view.customContextMenuRequested.connect(
            self.on_selection_context_menu_requested)
        self._init_selection_context_menu()
        self._ui.refresh_button.clicked.connect(self._pkg_sel_ctrl.on_pkg_refresh_clicked)
        self._ui.package_filter_edit.textChanged.connect(self._pkg_sel_ctrl.set_filter_wildcard)
        self.conan_pkg_selected.connect(self.on_pkg_selection_change)
        self._ui.package_path_label.setText("<Package path>")
        self._ui.package_path_label.setAlignment(Qt.AlignmentFlag.AlignRight) # must be called after every text set
        self.updateGeometry()
        self.resize_filter()

    def on_pkg_selection_change(self, conan_ref, pkg):
        # init/update the context menu
        re_register_signal(self._ui.package_file_view.customContextMenuRequested,
                           self.on_file_context_menu_requested)
        self._init_pkg_file_context_menu()

    def showEvent(self, a0: QShowEvent) -> None:
        self._pkg_sel_ctrl.refresh_pkg_selection_view(update=False)  # only update the first time
        return super().showEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self._pkg_file_exp_ctrl.resize_file_columns()
        super().resizeEvent(a0)

    def resize_filter(self):
        # resize filter splitter to roughly match file view splitter
        sizes = self._ui.splitter.sizes()
        offset = self._ui.package_filter_label.width() + self._ui.refresh_button.width()
        self._ui.splitter_filter.setSizes(
            [sizes[0]  - offset -5, sizes[1] + 5])

    def reload_themed_icons(self):
        super().reload_themed_icons()
        self._init_selection_context_menu()
        self._init_pkg_file_context_menu()

    # Selection view context menu

    def _init_selection_context_menu(self):
        self.select_cntx_menu = RoundedMenu()

        self.copy_ref_action = QAction("Copy reference", self)
        self.set_themed_icon(self.copy_ref_action, "icons/copy_link.svg")
        self.select_cntx_menu.addAction(self.copy_ref_action)
        self.copy_ref_action.triggered.connect(self._pkg_sel_ctrl.on_copy_ref_requested)

        self.open_export_action = QAction("Open export Folder", self)
        self.set_themed_icon(self.open_export_action, "icons/opened_folder.svg")
        self.select_cntx_menu.addAction(self.open_export_action)
        self.open_export_action.triggered.connect(self._pkg_sel_ctrl.on_open_export_folder_requested)

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.set_themed_icon(self.show_conanfile_action, "icons/file_preview.svg")
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self._pkg_sel_ctrl.on_show_conanfile_requested)

        self.install_ref_action = QAction("Re(install) package", self)
        self.set_themed_icon(self.install_ref_action, "icons/download_pkg.svg")
        self.select_cntx_menu.addAction(self.install_ref_action)
        self.install_ref_action.triggered.connect(self._pkg_sel_ctrl.on_install_ref_requested)

        self.remove_ref_action = QAction("Remove package", self)
        self.set_themed_icon(self.remove_ref_action, "icons/delete.svg")
        self.select_cntx_menu.addAction(self.remove_ref_action)
        self.remove_ref_action.triggered.connect(self._pkg_sel_ctrl.on_remove_ref_requested)

    def on_selection_context_menu_requested(self, position):
        self.select_cntx_menu.exec(self._ui.package_select_view.mapToGlobal(position))

    def _init_pkg_file_context_menu(self):
        if self.file_cntx_menu:
            return
        self.file_cntx_menu = RoundedMenu()

        self.open_fm_action = QAction("Show in File Manager", self)
        self.set_themed_icon(self.open_fm_action, "icons/file_explorer.svg")
        self.file_cntx_menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self._pkg_file_exp_ctrl.on_open_file_in_file_manager)

        self.copy_as_path_action = QAction("Copy as Path", self)
        self.set_themed_icon(self.copy_as_path_action, "icons/copy_to_clipboard.svg")
        self.file_cntx_menu.addAction(self.copy_as_path_action)
        self.copy_as_path_action.triggered.connect(self._pkg_file_exp_ctrl.on_copy_file_as_path)

        self._edit_file_action = QAction("Edit file", self)
        self.set_themed_icon(self._edit_file_action, "icons/edit_file.svg")
        self.file_cntx_menu.addAction(self._edit_file_action)
        self._edit_file_action.triggered.connect(self._pkg_file_exp_ctrl.on_edit_file)

        self.open_terminal_action = QAction("Open terminal here", self)
        self.set_themed_icon(self.open_terminal_action, "icons/cmd.svg")
        self.file_cntx_menu.addAction(self.open_terminal_action)
        self.open_terminal_action.triggered.connect(self._pkg_file_exp_ctrl.on_open_terminal_in_dir)

        self.file_cntx_menu.addSeparator()
        # TODO QAction::event: Ambiguous shortcut overload: Ctrl+V
        self.copy_action = QAction("Copy", self)
        self.set_themed_icon(self.copy_action, "icons/copy.svg")
        self.copy_action.setShortcut(QKeySequence("Ctrl+c"))
        self.copy_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.file_cntx_menu.addAction(self.copy_action)
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self.copy_action)
        self.copy_action.triggered.connect(self._pkg_file_exp_ctrl.on_file_copy)

        self.paste_action = QAction("Paste", self)
        self.set_themed_icon(self.paste_action, "icons/paste.svg")
        self.paste_action.setShortcut(QKeySequence("Ctrl+v"))  # Qt.CTRL + Qt.Key_V))
        self.paste_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.addAction(self.paste_action)
        self.file_cntx_menu.addAction(self.paste_action)
        self.paste_action.triggered.connect(self._pkg_file_exp_ctrl.on_file_paste)

        self.delete_action = QAction("Delete", self)
        self.set_themed_icon(self.delete_action, "icons/delete.svg")
        self.delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.file_cntx_menu.addAction(self.delete_action)
        self.delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.addAction(self.delete_action)
        self.delete_action.triggered.connect(self._pkg_file_exp_ctrl.on_file_delete)

        self.file_cntx_menu.addSeparator()

        self.add_link_action = QAction("Add link to App Grid", self)
        self.set_themed_icon(self.add_link_action, "icons/add_link.svg")
        self.file_cntx_menu.addAction(self.add_link_action)
        self.add_link_action.triggered.connect(self._pkg_file_exp_ctrl.on_add_app_link_from_file)

    def on_file_context_menu_requested(self, position):
        if not self.file_cntx_menu:
            return
        path = self._pkg_file_exp_ctrl.get_selected_pkg_path()
        self.add_link_action.setEnabled(True)
        if os.path.isdir(path):
            self.add_link_action.setDisabled(True)
        self.file_cntx_menu.exec(self._ui.package_file_view.mapToGlobal(position))

    def select_local_package_from_ref(self, conan_ref: str) -> bool:
        return self._pkg_sel_ctrl.select_local_package_from_ref(conan_ref)
