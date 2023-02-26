from pathlib import Path

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.settings import PLUGINS_SECTION_NAME
from conan_app_launcher.ui.common import TreeModel, TreeModelItem, get_themed_asset_icon
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, QModelIndex

from conan_app_launcher.ui.plugin.plugins import PluginDescription, PluginFile

class PluginModelItem(TreeModelItem):

    def __init__(self, plugin: PluginDescription, plugin_path: str,  parent):
        super().__init__([plugin.name, plugin.version, plugin.author, plugin.description], parent, lazy_loading=False)
        self._icon = plugin.icon
        self.plugin_path = str(Path(plugin_path).resolve())

class PluginModel(TreeModel):
    def __init__(self, *args, **kwargs):
        super().__init__(checkable=True, *args, **kwargs)
        self.root_item = TreeModelItem(["Name", "Version", "Author", "Description", "Conan support"])

    def setup_model_data(self):
        self.root_item.child_items = []
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            plugins = PluginFile.read_file(plugin_path)
            for plugin in plugins:
                plugin_element = PluginModelItem(plugin, plugin_path, self.root_item)
                self.root_item.append_child(plugin_element)


    def data(self, index: QModelIndex, role):  # override
        if not index.isValid():
            return None
        item = index.internalPointer()
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
        return None
