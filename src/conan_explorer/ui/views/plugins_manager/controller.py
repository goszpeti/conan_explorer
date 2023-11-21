from typing import Optional

from PySide6.QtCore import QModelIndex, QObject
from PySide6.QtWidgets import QTreeView

from conan_explorer.ui.plugin import PluginHandler

from .model import PluginModel, PluginModelItem


class PluginController(QObject):

    def __init__(self, view: QTreeView, plugin_handler: PluginHandler) -> None:
        super().__init__(view)
        self._view = view
        self._model = PluginModel()
        self._plugin_handler = plugin_handler

    def update(self):
        self._model = PluginModel()
        self._model.setup_model_data()
        self._view.setItemsExpandable(False)
        self._view.setRootIsDecorated(False)
        self._view.setModel(self._model)
        self._view.expandAll()
        self._resize_columns()

    def get_selected_source_item(self) -> Optional[PluginModelItem]:
        """ Gets the selected item from a view """
        indexes = self._view.selectedIndexes()
        if not indexes:
            return None
        view_index = indexes[0]
        source_item: PluginModelItem = view_index.internalPointer() # type: ignore
        return source_item

    def _resize_columns(self):
        count = self._view.model().columnCount(QModelIndex())
        for i in reversed(range(count-1)):
            self._view.resizeColumnToContents(i)

    def add_plugin(self, plugin_path: str):
        self._plugin_handler.add_plugin(plugin_path)

    def remove_plugin(self, plugin_path: str):
        self._plugin_handler.remove_plugin(plugin_path)

    def reload_plugin(self, plugin_name: str):
        self._plugin_handler.reload_plugin(plugin_name)
