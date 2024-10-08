from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

from PySide6.QtCore import (
    QItemSelectionModel,
    QMimeData,
    QModelIndex,
    QObject,
    Qt,
    QUrl,
    SignalInstance,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QListWidgetItem,
    QMessageBox,
    QStyle,
    QTextBrowser,
    QTreeView,
)

import conan_explorer.app as app
from conan_explorer.app.base_ui.loading import LoaderGui
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import (
    calc_paste_same_dir_name,
    copy_path_with_overwrite,
    delete_path,
    execute_cmd,
    open_cmd_in_path,
    open_in_file_manager,
    run_file,
)
from conan_explorer.conan_wrapper.types import ConanPkg, ConanRef
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE
from conan_explorer.ui.common import re_register_signal
from conan_explorer.ui.dialogs import QuestionWithItemListDialog
from conan_explorer.ui.views import AppGridView
from conan_explorer.ui.views.app_grid import UiAppLinkConfig

from .file_model import CalFileSystemModel
from .sel_model import PkgSelectionType

if TYPE_CHECKING:
    from conan_explorer.ui.fluent_window import PageStore
    from conan_explorer.ui.main_window import BaseSignals

    from .package_explorer import LocalConanPackageExplorer

NEW_FOLDER_NAME = "New folder"


class PackageFileExplorerController(QObject):
    def __init__(
        self,
        parent: "LocalConanPackageExplorer",
        view: QTreeView,
        pkg_path_label: QTextBrowser,
        cut_files_reset: SignalInstance,
        base_signals: "BaseSignals",
        page_widgets: "PageStore",
    ):
        super().__init__(parent)
        self._model: Optional[CalFileSystemModel] = None
        self._page_widgets = page_widgets
        self._view = view
        self._pkg_path_label = pkg_path_label
        self.cut_files_reset = cut_files_reset
        self._type = PkgSelectionType.ref
        base_signals.conan_pkg_removed.connect(self.on_conan_pkg_removed)
        self.cut_files_reset.connect(self._disable_cut_selection)

        self._current_ref: Optional[str] = None  # loaded conan ref
        self._current_pkg: Optional[ConanPkg] = None  # loaded conan pkg info

    def get_conan_pkg_info(self):
        return self._current_pkg

    def get_conan_pkg_type(self):
        return self._type

    def on_pkg_selection_change(
        self, conan_ref: str, pkg_info: ConanPkg, type: PkgSelectionType
    ):
        """Change folder in file view"""
        # add try-except
        self._current_ref = conan_ref
        self._current_pkg = pkg_info
        try:
            if type == PkgSelectionType.editable:
                pkg_path = app.conan_api.get_editables_package_path(ConanRef.loads(conan_ref))
                if pkg_path.is_file():
                    pkg_path = pkg_path.parent
            elif type == PkgSelectionType.export:
                pkg_path = app.conan_api.get_export_folder(ConanRef.loads(conan_ref))
            else:
                pkg_path = app.conan_api.get_package_folder(
                    ConanRef.loads(conan_ref), pkg_info.get("id", "")
                )
        except Exception as e:
            Logger().error("Cannot change to package: %s", str(e))
            return

        if not pkg_path.exists():
            Logger().warning(
                f"Can't find package path for {conan_ref} and {str(pkg_info)} for File View"
            )
            return

        if self._model and pkg_path == Path(self._model.rootPath()):
            return
        else:  # initialize once - otherwise this causes performance issues
            self._model = CalFileSystemModel()
            self._view.setModel(self._model)

        self._model.setRootPath(str(pkg_path))
        self._model.sort(0, Qt.SortOrder.AscendingOrder)
        self._model.setReadOnly(False)
        self._view.setRootIndex(self._model.index(str(pkg_path)))
        self._view.setColumnHidden(2, True)  # file type
        self._model.layoutChanged.connect(self.resize_file_columns)
        self._view.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        # disable edit on double click, since we want to open
        re_register_signal(self._view.doubleClicked, self.on_file_double_click)  # type: ignore

        self._view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.resize_file_columns()

    def on_conan_pkg_removed(self, conan_ref: str, pkg_id: str):
        """Slot for on_conan_pkg_removed signal."""
        # clear file view if this pkg is selected
        own_id = pkg_id
        if self._current_pkg:
            own_id = self._current_pkg.get("id", "")
        if self._current_ref == conan_ref:
            delete = False
            if not pkg_id:
                delete = True
            elif pkg_id and pkg_id == own_id:
                delete = True
            if not delete:
                return
            self.close_files_view()
            self.parent().tab_close_requested(self)  # type: ignore

    def close_files_view(self):
        """Reset and clear up file view"""
        if self._model:
            self._model.deleteLater()
        self._model = None  # type: ignore
        self._current_ref = ""
        self._current_pkg = None
        self._pkg_path_label.setText("")
        self._view.setModel(None)  # type: ignore
        self._pkg_path_label.setText("")

    def on_file_double_click(self, model_index):
        file_path = Path(model_index.model().fileInfo(model_index).absoluteFilePath())
        run_file(file_path, True, args="")

    def on_copy_file_as_path(self) -> str:
        files = self.get_selected_pkg_paths()
        file_paths = "\n".join(files)
        QApplication.clipboard().setText(file_paths)
        return file_paths

    def on_open_terminal_in_dir(self) -> int:
        selected_path = Path(self.get_selected_pkg_paths()[0])
        if selected_path.is_file():
            selected_path = selected_path.parent
        return open_cmd_in_path(selected_path)

    def on_edit_file(self):
        selected_paths = self.get_selected_pkg_paths()
        if len(selected_paths) != 1:
            return
        for selected_path in selected_paths:
            if not Path(selected_path).is_file():
                continue
            editor = app.active_settings.get_string(FILE_EDITOR_EXECUTABLE)
            if not editor:
                Logger().info("No editor set up! Please configure it in the settings menu.")
                return
            execute_cmd([editor, selected_path], False)

    def on_file_delete(self):
        selected_paths = self.get_selected_pkg_paths()
        msg = QMessageBox(parent=self._view)
        msg.setWindowTitle("Delete file")
        msg.setText("Are you sure, you want to permanently delete this file(s)/folder(s)?\t")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        msg.setIcon(QMessageBox.Icon.Warning)
        reply = msg.exec()
        if reply != QMessageBox.StandardButton.Yes:
            return

        loader = LoaderGui(None)

        def delete_paths(paths: List[str]):
            for path in paths:
                loader.loading_string_signal.emit("Deleting " + path)
                delete_path(Path(path))

        loader.load(self._view, delete_paths, (selected_paths,), cancel_button=False)

    def on_files_copy(self) -> List[QUrl]:
        if not self._model:
            return []
        files = self.get_selected_pkg_paths()
        if not files:
            return []
        data = QMimeData()
        urls = []
        for file in files:
            urls.append(QUrl.fromLocalFile(file))
        self.cut_files_reset.emit()
        self._view.repaint()
        data.setUrls(urls)

        QApplication.clipboard().setMimeData(data)
        return urls

    def on_files_cut(self) -> List[QUrl]:
        if not self._model:
            return []
        files = self.get_selected_pkg_paths()
        if not files:
            return []
        urls = []
        for file in files:
            urls.append(QUrl.fromLocalFile(file))
        data = QMimeData()
        data.setUrls(urls)
        data.setProperty("action", "cut")
        self._model.clear_all_disabled_items()  # type: ignore
        self.cut_files_reset.emit()

        self._model.add_disabled_items(files)  # type: ignore
        self._view.repaint()

        QApplication.clipboard().setMimeData(data)
        return urls

    def on_item_rename(self):
        file_view_indexes = self._get_pkg_file_source_items()
        if not file_view_indexes:
            return None
        # for multiselect: edit last item
        self._view.edit(file_view_indexes[-1])
        return file_view_indexes

    def on_files_paste(self):
        data = QApplication.clipboard().mimeData()
        if not data or not data.hasUrls():
            return
        urls = data.urls()
        # determine destination path
        sel_item_paths = self.get_selected_pkg_paths()
        if not sel_item_paths:
            return
        # determine destination path
        dst_dir_path = Path(sel_item_paths[0])

        # on multiselect it will paste once in the parent dir of the selected items
        if len(sel_item_paths) > 1:
            dst_dir_path = dst_dir_path.parent

        elif not self._is_selected_file_item_expanded():
            dst_dir_path = dst_dir_path.parent if dst_dir_path.is_file() else dst_dir_path

        # all of them should be true
        cut = True if data.property("action") == "cut" else False
        files_paths: List[Tuple[Path, Path]] = []
        overwrites: List[Path] = []
        for url in urls:
            # try to copy
            if not url.isLocalFile():
                continue
            source_path = Path(url.toLocalFile())
            target_path = Path(dst_dir_path, url.fileName())
            files_paths.append((source_path, target_path))
            if target_path.exists():
                overwrites.append(target_path)

        # Show dialog which files should be overwritten
        if overwrites:
            non_overwrites_paths = self.show_overwrite_dialog(overwrites)
            # remove selected_overwrites from files_paths
            files_paths = list(
                filter(
                    lambda files_path: files_path[1] not in non_overwrites_paths, files_paths
                )
            )
        if not files_paths:
            return
        loader = LoaderGui(None)

        def paste_files(self):
            for source_path, target_path in files_paths:
                self.paste_path(source_path, target_path, cut)

        loader.load(self._view, paste_files, (self,))
        self.cut_files_reset.emit()
        self._disable_cut_selection()

    def _disable_cut_selection(self):
        if self.sender() == self:
            return
        self._model.clear_all_disabled_items()  # type: ignore
        self._view.repaint()

    def paste_path(self, src: Path, dst: Path, cut=False):
        if src == dst and cut:
            return  # do nothing
        if src == dst:  # same target -> create numbered copies
            new_dst = calc_paste_same_dir_name(dst)
            copy_path_with_overwrite(src, new_dst)
        else:
            copy_path_with_overwrite(src, dst)
            if cut:
                delete_path(src)

    def show_overwrite_dialog(self, overwrites: List[Path]):
        non_overwrites = []
        dialog = QuestionWithItemListDialog(
            self._view, QStyle.StandardPixmap.SP_MessageBoxWarning
        )
        dialog.setWindowTitle("Overwrite file/folder")
        dialog.set_question_text("Are you sure, you want to overwrite this file/folder?\t")
        for path in overwrites:
            list_item = QListWidgetItem(str(path))
            list_item.setCheckState(Qt.CheckState.Checked)
            dialog.item_list_widget.addItem(list_item)

        reply = dialog.exec()
        if reply == QDialog.DialogCode.Accepted:
            # get user DEselection
            for list_row in range(dialog.item_list_widget.count()):
                list_item = dialog.item_list_widget.item(list_row)
                if list_item.checkState() != Qt.CheckState.Unchecked:
                    continue
                non_overwrites.append(Path(list_item.text()))
            return non_overwrites
        else:
            return overwrites  # early return to not delete path on cut and cancel

    def on_add_app_link_from_file(self):
        selected_paths = self.get_selected_pkg_paths()
        if len(selected_paths) != 1:
            return
        file_path = Path(selected_paths[0])
        if not file_path.is_file():
            Logger().error("Please select a file, not a directory!")
            return
        if not self._current_ref:
            return
        conan_ref = ConanRef.loads(self._current_ref)
        # determine relpath from package
        pkg_info = self._current_pkg
        if not pkg_info:
            Logger().error("Error on trying to adding Applink: No package info found.")
            return
        pkg_path = app.conan_api.get_package_folder(conan_ref, pkg_info.get("id", ""))
        rel_path = file_path.relative_to(pkg_path).as_posix()  # no \ for UI config

        app_config = UiAppLinkConfig(
            name="NewLink",
            conan_ref=str(self._current_ref),
            executable=str(rel_path),
            conan_options=pkg_info.get("options", {}),
        )
        self._page_widgets.get_page_by_type(AppGridView).open_new_app_dialog_from_extern(
            app_config
        )

    def on_new_folder(self, model_index):
        request_file_path = Path(self.get_selected_pkg_paths()[-1])
        target_file_path = request_file_path
        if request_file_path.is_file():
            target_file_path = request_file_path.parent

        target_folder = target_file_path / NEW_FOLDER_NAME
        target_folder.mkdir(exist_ok=True)
        # it does not seem to be necessary to wait for creation
        if self.select_file_item(str(target_folder)).isValid():
            self.on_item_rename()

    def on_open_file_in_file_manager(self, model_index):
        file_path = Path(self.get_selected_pkg_paths()[-1])
        open_in_file_manager(file_path)

    def _get_pkg_file_source_items(self) -> List[QModelIndex]:
        indexes = []
        for index in self._view.selectedIndexes():
            if index.column() == 0:  # we only need a row once
                indexes.append(index)
        return indexes

    def select_file_item(self, file_to_select: str) -> QModelIndex:
        if not self._model:
            return QModelIndex()
        try:
            sel_idx = self._model.index(file_to_select, 0)
            self._view.selectionModel().select(
                sel_idx, QItemSelectionModel.SelectionFlag.ClearAndSelect
            )
        except Exception:
            Logger().debug("Can't select file %s", file_to_select, exc_info=True)
            return QModelIndex()
        return sel_idx

    def get_selected_pkg_paths(self) -> List[str]:
        file_paths: List[str] = []
        if not self._model:
            return file_paths
        file_view_indexes = self._get_pkg_file_source_items()
        # if nothing selected return root
        if not file_view_indexes:
            return [self._model.rootPath()]
        for file_view_index in file_view_indexes:
            file_paths.append(self._model.fileInfo(file_view_index).absoluteFilePath())
        return file_paths

    def _is_selected_file_item_expanded(self):
        file_view_indexes = self._get_pkg_file_source_items()
        # if nothing selected return root
        if len(file_view_indexes) != 1:
            return False
        return self._view.isExpanded(file_view_indexes[0])

    def resize_file_columns(self):
        if not self._view:
            return
        for i in reversed(range(3 - 1)):
            self._view.resizeColumnToContents(i)
