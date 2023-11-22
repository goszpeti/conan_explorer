import os
from typing import TYPE_CHECKING
from conan_explorer import conan_version

from conan_explorer.conan_wrapper.types import ConanPkg, ConanRef, pretty_print_pkg_info
from conan_explorer.ui.common.model import re_register_signal
from conan_explorer.ui.plugin import PluginDescription, PluginInterfaceV1
from conan_explorer.ui.widgets import RoundedMenu

from .file_controller import PackageFileExplorerController
from .sel_controller import PackageSelectionController
from .sel_model import PkgSelectionType

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QResizeEvent, QAction, QShowEvent
from PySide6.QtWidgets import (QWidget, QTabBar, QTreeView, QHBoxLayout, QFrame, 
                               QAbstractItemView, QAbstractScrollArea)


if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import FluentWindow
    from conan_explorer.ui.main_window import BaseSignals


class LocalConanPackageExplorer(PluginInterfaceV1):
    conan_pkg_selected = Signal(str, ConanPkg, PkgSelectionType)

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
        self._pkg_tabs_ctrl = [PackageFileExplorerController(
            self, self._ui.package_file_view, self._ui.package_path_label,
            self.conan_pkg_selected, self._base_signals, self._page_widgets)]
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
        self._ui.package_path_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # must be called after every text set
        self._ui.package_tab_widget.currentChanged.connect(self.on_tab_index_changed)
        # removes X of new Tab button
        self._ui.package_tab_widget.tabBar().setTabButton(1, QTabBar.ButtonPosition.RightSide, None) # type: ignore
        self._ui.package_tab_widget.tabCloseRequested.connect(self.on_close_tab)
        self._ui.package_tab_widget.tabBar().setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectLeftTab)
        self.updateGeometry()
        self.resize_filter()

    def on_close_tab(self, index: int):
        # self._ui.package_tab_widget.tabBar().setTabVisible(index, False)
        self._ui.package_tab_widget.removeTab(index)
        self._pkg_tabs_ctrl.pop(index)

    def on_tab_index_changed(self, index: int):
        assert self._base_signals
        assert self._page_widgets

        # adds new tab
        if self._ui.package_tab_widget.count() == index + 1:
            tab = QWidget(self._ui.package_tab_widget)
            horizontal_layout = QHBoxLayout(tab)
            horizontal_layout.setSpacing(0)
            horizontal_layout.setObjectName(u"horizontalLayout")
            horizontal_layout.setContentsMargins(0, 0, 0, 0)
            tab.setLayout(horizontal_layout)
            file_explorer_view = QTreeView(tab)
            horizontal_layout.addWidget(file_explorer_view)
            file_explorer_view.setFrameShape(QFrame.Shape.NoFrame)
            file_explorer_view.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            file_explorer_view.setEditTriggers(
                QAbstractItemView.EditTrigger.EditKeyPressed | QAbstractItemView.EditTrigger.SelectedClicked)
            file_explorer_view.setTabKeyNavigation(True)
            file_explorer_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
            file_explorer_view.setDefaultDropAction(Qt.DropAction.TargetMoveAction)
            file_explorer_view.setIndentation(15)
            file_explorer_view.setUniformRowHeights(True)
            file_explorer_view.setItemsExpandable(True)
            file_explorer_view.setSortingEnabled(True)
            file_explorer_view.setAnimated(True)
            file_explorer_view.setSelectionMode(
                                    QAbstractItemView.SelectionMode.ExtendedSelection)

            self._pkg_tabs_ctrl.append(PackageFileExplorerController(
                self, file_explorer_view, self._ui.package_path_label,
                self.conan_pkg_selected, self._base_signals, self._page_widgets))

            self._ui.package_tab_widget.insertTab(index, tab, "New tab")
            self._ui.package_tab_widget.setCurrentIndex(index)
        else:
            ctrl = self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()]
            if ctrl._model:
                self._ui.package_path_label.setText(ctrl._model.rootPath())

    def on_pkg_selection_change(self, conan_ref: str, pkg: ConanPkg, type: PkgSelectionType):
        # init/update the context menu
        for ctrl in self._pkg_tabs_ctrl:
            re_register_signal(ctrl._view.customContextMenuRequested,
                               self.on_file_context_menu_requested)
        self._init_pkg_file_context_menu()
        cfr = ConanRef.loads(conan_ref)
        disp_ref = f"{cfr.name}/{cfr.version}" # only package/version
        if type == PkgSelectionType.export:
            disp_ref += " (export)"
        idx = self._ui.package_tab_widget.currentIndex()
        self._ui.package_tab_widget.setTabText(idx, disp_ref)
        self._ui.package_tab_widget.setTabToolTip(idx, pretty_print_pkg_info(pkg))
        self._ui.package_tab_widget.tabBar().setExpanding(True)
        ctrl = self._pkg_tabs_ctrl[idx]

        ctrl.on_pkg_selection_change(conan_ref, pkg, type)
        if ctrl._model:
            self._ui.package_path_label.setText(ctrl._model.rootPath())

    def showEvent(self, a0: QShowEvent) -> None:
        self._pkg_sel_ctrl.refresh_pkg_selection_view(force_update=False)  # only update the first time
        return super().showEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        for pkg_file_exp_ctrl in self._pkg_tabs_ctrl:
            pkg_file_exp_ctrl.resize_file_columns()
        super().resizeEvent(a0)

    def resize_filter(self):
        # resize filter splitter to roughly match file view splitter
        sizes = self._ui.splitter.sizes()
        offset = self._ui.package_filter_label.width() + self._ui.refresh_button.width()
        self._ui.splitter_filter.setSizes(
            [sizes[0] - offset - 5, sizes[1] + 5])

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

        self.show_conanfile_action = QAction("Show conanfile", self)
        self.set_themed_icon(self.show_conanfile_action, "icons/file_preview.svg")
        self.select_cntx_menu.addAction(self.show_conanfile_action)
        self.show_conanfile_action.triggered.connect(self._pkg_sel_ctrl.on_show_conanfile_requested)

        self.install_ref_action = QAction("Re(install) package", self)
        self.set_themed_icon(self.install_ref_action, "icons/download_pkg.svg")
        self.select_cntx_menu.addAction(self.install_ref_action)
        self.install_ref_action.triggered.connect(self._pkg_sel_ctrl.on_install_ref_requested)

        # always have show_build_info_action so access to it is possible in ConanV2 
        # even if it does nothing
        self.show_build_info_action = QAction("Show package build info", self)
        if not conan_version.startswith("2"): # Currently not doable
            self.set_themed_icon(self.show_build_info_action, "icons/download.svg")
            self.select_cntx_menu.addAction(self.show_build_info_action)
            self.show_build_info_action.triggered.connect(self._pkg_sel_ctrl.on_show_build_info)

        self.remove_ref_action = QAction("Remove package(s)", self)
        self.set_themed_icon(self.remove_ref_action, "icons/delete.svg")
        self.select_cntx_menu.addAction(self.remove_ref_action)
        self.remove_ref_action.triggered.connect(self._pkg_sel_ctrl.on_remove_ref_requested)

    def on_selection_context_menu_requested(self, position):
        # no multiselect
        if len(self._pkg_sel_ctrl.get_selected_conan_refs()) > 1:
            self.show_build_info_action.setVisible(False)
            self.show_conanfile_action.setVisible(False)
            self.install_ref_action.setVisible(False)
            self.remove_ref_action.setVisible(False)
        else:
            self.show_build_info_action.setVisible(True)
            self.show_conanfile_action.setVisible(True)
            self.install_ref_action.setVisible(True)
            self.remove_ref_action.setVisible(True)

        self.select_cntx_menu.exec(self._ui.package_select_view.mapToGlobal(position))

    # Package File Explorer context menu

    def on_open_file_in_file_manager(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_open_file_in_file_manager(model_index)

    def on_copy_file_as_path(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_copy_file_as_path()

    def on_edit_file(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_edit_file()

    def on_open_terminal_in_dir(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_open_terminal_in_dir()

    def on_file_rename(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_file_rename()

    def on_file_copy(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_files_copy()

    def on_file_cut(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_files_cut()

    def on_file_paste(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_files_paste()

    def on_file_delete(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_file_delete()

    def on_add_app_link_from_file(self, model_index):
        self._pkg_tabs_ctrl[self._ui.package_tab_widget.currentIndex()].on_add_app_link_from_file()

    def _init_pkg_file_context_menu(self):
        if self.file_cntx_menu:
            return
        # for pkg_file_exp_ctrl in self._pkg_tabs_ctrl:
        self.file_cntx_menu = RoundedMenu()
        self._open_fm_action = QAction("Show in File Manager", self)
        self.set_themed_icon(self._open_fm_action, "icons/file_explorer.svg")
        self.file_cntx_menu.addAction(self._open_fm_action)
        self._open_fm_action.triggered.connect(self.on_open_file_in_file_manager)

        self._copy_as_path_action = QAction("Copy as Path", self)
        self.set_themed_icon(self._copy_as_path_action, "icons/copy_to_clipboard.svg")
        self.file_cntx_menu.addAction(self._copy_as_path_action)
        self._copy_as_path_action.triggered.connect(self.on_copy_file_as_path)

        self._edit_file_action = QAction("Edit file", self)
        self.set_themed_icon(self._edit_file_action, "icons/edit_file.svg")
        self.file_cntx_menu.addAction(self._edit_file_action)
        self._edit_file_action.triggered.connect(self.on_edit_file)

        self._open_terminal_action = QAction("Open terminal here", self)
        self.set_themed_icon(self._open_terminal_action, "icons/cmd.svg")
        self.file_cntx_menu.addAction(self._open_terminal_action)
        self._open_terminal_action.triggered.connect(self.on_open_terminal_in_dir)

        self.file_cntx_menu.addSeparator()

        self._rename_action = QAction("Rename", self)
        self.set_themed_icon(self._rename_action, "icons/rename.svg")
        self._rename_action.setShortcut(QKeySequence("F2"))
        self._rename_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.file_cntx_menu.addAction(self._rename_action)
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self._rename_action)
        self._rename_action.triggered.connect(self.on_file_rename)

        self._copy_action = QAction("Copy", self)
        self.set_themed_icon(self._copy_action, "icons/copy.svg")
        self._copy_action.setShortcut(QKeySequence("Ctrl+c"))
        self._copy_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.file_cntx_menu.addAction(self._copy_action)
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self._copy_action)
        self._copy_action.triggered.connect(self.on_file_copy)

        self._cut_action = QAction("Cut", self)
        self.set_themed_icon(self._cut_action, "icons/cut.svg")
        self._cut_action.setShortcut(QKeySequence("Ctrl+x"))
        self._cut_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.file_cntx_menu.addAction(self._cut_action)
        # for the shortcut to work, the action has to be added to a higher level widget
        self.addAction(self._cut_action)
        self._cut_action.triggered.connect(self.on_file_cut)

        self._paste_action = QAction("Paste", self)
        self.set_themed_icon(self._paste_action, "icons/paste.svg")
        self._paste_action.setShortcut(QKeySequence("Ctrl+v"))  # Qt.CTRL + Qt.Key_V))
        self._paste_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.addAction(self._paste_action)
        self.file_cntx_menu.addAction(self._paste_action)
        self._paste_action.triggered.connect(self.on_file_paste)

        self._delete_action = QAction("Delete", self)
        self.set_themed_icon(self._delete_action, "icons/delete.svg")
        self._delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.file_cntx_menu.addAction(self._delete_action)
        self._delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.addAction(self._delete_action)
        self._delete_action.triggered.connect(self.on_file_delete)

        self.file_cntx_menu.addSeparator()

        self._add_link_action = QAction("Add link to App Grid", self)
        self.set_themed_icon(self._add_link_action, "icons/add_link.svg")
        self.file_cntx_menu.addAction(self._add_link_action)
        self._add_link_action.triggered.connect(self.on_add_app_link_from_file)

    def on_file_context_menu_requested(self, position):
        """ Disable some context menu items depending on context """
        if not self.file_cntx_menu:
            return
        self._add_link_action.setVisible(True)
        self._edit_file_action.setVisible(True)
        self._rename_action.setVisible(True)

        tab_idx = self._ui.package_tab_widget.currentIndex()
        # Add Link only works on actual packages
        pkg_type  = self._pkg_tabs_ctrl[tab_idx].get_conan_pkg_type()
        if pkg_type == PkgSelectionType.export:
            self._add_link_action.setVisible(False)
        else:
            self._add_link_action.setVisible(True)

        # multiselect options
        paths = self._pkg_tabs_ctrl[tab_idx].get_selected_pkg_paths()
        if len (paths) > 1: # no multiselect
            self._add_link_action.setVisible(False)
            self._edit_file_action.setVisible(False)
            self._rename_action.setVisible(False)
            self._open_fm_action.setVisible(False)
            self._copy_as_path_action.setVisible(False)
            self._open_terminal_action.setVisible(False)
        elif os.path.isdir(paths[0]):
            self._add_link_action.setVisible(False)
            self._edit_file_action.setVisible(False)
            self._rename_action.setVisible(True)
            self._open_fm_action.setVisible(True)
            self._copy_as_path_action.setVisible(True)
            self._open_terminal_action.setVisible(True)

        self.file_cntx_menu.exec(self._ui.package_file_view.mapToGlobal(position))

    def select_local_package_from_ref(self, conan_ref: str) -> bool:
        return self._pkg_sel_ctrl.select_local_package_from_ref(conan_ref)
