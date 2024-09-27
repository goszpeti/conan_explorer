from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QDialog, QStyle, QTreeWidgetItem, QWidget

from conan_explorer.app import LoaderGui  # using global module pattern
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import delete_path, get_folder_size_mb
from conan_explorer.conan_wrapper.conan_cleanup import ConanCleanup


class ConanCacheCleanupDialog(QDialog):
    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        from .conan_cache_cleanup_ui import Ui_Dialog

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        ref_items = []
        self.cleanup_info = None

        cleaner = ConanCleanup()
        loader = LoaderGui(self)
        self.loader = loader
        self.accepted.connect(self.on_accept)
        loader.load(
            self,
            cleaner.get_cleanup_cache_info,
            loading_text="Gathering obsolete directories...",
            cancel_button=False,
        )
        loader.wait_for_finished()
        cleanup_info = loader.return_value
        if not cleanup_info:
            Logger().info("Nothing found in cache to clean up.")
            return

        def setup_model_data_with_sizes(cleanup_info):
            size_mbytes = 0
            for ref, paths in cleanup_info.items():
                ref_item = QTreeWidgetItem([ref])
                for path_type, path in paths.items():
                    loader.loading_string_signal.emit(
                        (
                            f"Calculating size of {ref} {path_type}\n"
                            f"Found {size_mbytes:.1f}MB to clean up"
                        )
                    )
                    size_mbytes_item = get_folder_size_mb(Path(path))
                    child = QTreeWidgetItem([path_type, f"{size_mbytes_item:.2f}"])
                    size_mbytes += size_mbytes_item
                    ref_item.addChild(child)
                ref_items.append(ref_item)
            return size_mbytes

        loader.load(self, setup_model_data_with_sizes, (cleanup_info,), cancel_button=False)
        loader.wait_for_finished()
        size = loader.return_value
        self.cleanup_info = cleanup_info

        if size is None:
            size = 0

        self._ui.cleanup_tree_widget.addTopLevelItems(ref_items)
        self._ui.question_label.setText(
            f"Found {size:.2f} MB to clean up.\n"
            "Are you sure you want to delete the found folders?\t"
        )
        pixmapi = getattr(QStyle, "SP_MessageBoxQuestion")
        if pixmapi:
            icon = self.style().standardIcon(pixmapi)
            self._ui.icon.setPixmap(icon.pixmap(40, 40))
        self._ui.cleanup_tree_widget.expandAll()
        self._ui.cleanup_tree_widget.resizeColumnToContents(0)

        self.show()

    def on_accept(self):
        if not self.cleanup_info:
            return

        def delete_cache_paths(cleanup_info):
            for _, paths in cleanup_info.items():
                for _, path in paths.items():
                    self.loader.loading_string_signal.emit("Deleting\n" + str(path))
                    delete_path(Path(path))

        self.loader.load(
            self,
            delete_cache_paths,
            (self.cleanup_info,),
            loading_text="Deleting cache paths...",
            cancel_button=False,
        )
