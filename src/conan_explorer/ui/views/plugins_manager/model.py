from pathlib import Path
from typing import Any, Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont
from typing_extensions import override

import conan_explorer.app as app  # using global module pattern
from conan_explorer.settings import PLUGINS_SECTION_NAME
from conan_explorer.ui.common import (TreeModel, TreeModelItem,
                                      get_themed_asset_icon)
from conan_explorer.ui.plugin import (PluginDescription, PluginFile,
                                      PluginHandler)


class PluginModelItem(TreeModelItem):

    def __init__(self, plugin: PluginDescription, plugin_path: str, enabled: bool, parent: TreeModelItem):
        super().__init__([plugin.name, plugin.version, plugin.description, plugin.conan_versions,
                          plugin.author], parent,  lazy_loading=False)
        self._icon = plugin.icon
        self.enabled = enabled
        self.plugin_path = str(Path(plugin_path).resolve())

class PluginModel(TreeModel):
    def __init__(self, *args, **kwargs):
        super().__init__(checkable=True, *args, **kwargs)
        self.root_item = TreeModelItem(["Name", "Version", "Description", "Conan", "Author"])

    def setup_model_data(self):
        self.root_item.child_items = []
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            plugins = PluginFile.read(plugin_path)
            for plugin in plugins:
                plugin_element = PluginModelItem(plugin, plugin_path, PluginHandler.is_plugin_enabled(plugin), self.root_item)
                self.root_item.append_child(plugin_element)

    @override
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
        if not index.isValid():
            return None
        item: PluginModelItem = index.internalPointer() # type: ignore
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return item.data(index.column())
            except Exception:
                return ""
        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() != 0:  # only display icon for first column
                return
            if isinstance(item, PluginModelItem):
                return get_themed_asset_icon(item._icon)
        if role == Qt.ItemDataRole.FontRole and not item.enabled:
            font = QFont()
            font.setItalic(True)
            return font
        return None
