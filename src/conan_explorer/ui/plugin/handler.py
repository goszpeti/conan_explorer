import importlib
import sys
from packaging import specifiers, version

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal, QObject, SignalInstance
from PySide6.QtWidgets import QWidget


import conan_explorer.app as app
from conan_explorer import BUILT_IN_PLUGIN, base_path, conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.settings import PLUGINS_SECTION_NAME


from .file import PluginFile
from .types import PluginDescription, PluginInterfaceV1


class PluginHandler(QObject):
    # Both signals need to be connected in the main gui
    load_plugin: SignalInstance = Signal(PluginDescription)  # type: ignore
    unload_plugin: SignalInstance = Signal(str)  # type: ignore

    def __init__(self, parent: QWidget, base_signals, page_widgets) -> None:
        super().__init__(parent)
        self._base_signals = base_signals
        self._page_widgets = page_widgets
        self._active_plugins = []

    def load_all_plugins(self):
        # load built-in from dynamic path
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            if plugin_group_name == BUILT_IN_PLUGIN:
                # fix potentially outdated setting
                correct_plugin_path = str(base_path / "ui" / "plugins.ini")
                if plugin_path != correct_plugin_path:
                    app.active_settings.add(
                        BUILT_IN_PLUGIN, correct_plugin_path, PLUGINS_SECTION_NAME)
                    plugin_path = correct_plugin_path
            self._load_plugins_from_file(plugin_path)

    def get_plugin_descr_from_name(self, plugin_name: str) -> Optional[PluginDescription]:
        plugins: List[PluginDescription] = self.get_same_file_plugins_from_name(
            plugin_name)
        for plugin in plugins:
            if plugin.name == plugin_name:
                return plugin

    def get_same_file_plugins_from_name(self, plugin_name: str) -> List[PluginDescription]:
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            file_plugins = PluginFile.read(plugin_path)
            for plugin in file_plugins:
                if plugin.name == plugin_name:
                    return file_plugins
        return []

    def add_plugin(self, plugin_path: str):
        PluginFile.register(plugin_path)
        plugins = self._load_plugins_from_file(plugin_path)
        for plugin in plugins:
            self.load_plugin.emit(plugin)
            plugin.load_signal.emit()

    def remove_plugin(self, plugin_path: str):
        PluginFile.unregister(plugin_path)
        file_plugins = PluginFile.read(plugin_path)
        for plugin in file_plugins:
            self._unload_plugin(plugin)

    def reload_plugin(self, plugin_name: str):
        plugin_descr = self.get_plugin_descr_from_name(plugin_name)
        assert plugin_descr
        self._unload_plugin(plugin_descr)
        plugin = self._load_plugin(plugin_descr, reload=True)
        self.load_plugin.emit(plugin)
        plugin.load_signal.emit()

    def _load_plugins_from_file(self, plugin_path: str) -> List [PluginInterfaceV1]:
        file_plugin_descrs = PluginFile.read(plugin_path)
        loaded_plugins = []
        for plugin_descr in file_plugin_descrs:
            loaded_plugins.append(self._load_plugin(plugin_descr))
        return loaded_plugins

    def _load_plugin(self, plugin: PluginDescription, 
                                        reload=False) -> Optional[PluginInterfaceV1]:
        loaded_plugin = None
        if self.is_plugin_enabled(plugin):
            try:
                import_path = Path(plugin.import_path)
                sys.path.append(str(import_path.parent))
                module_ = importlib.import_module(import_path.stem)
                if reload:
                    # get all modules to re-import
                    modules_to_del = [
                        module for module in sys.modules if import_path.stem in module]
                    # importlib reload does not work with relative imports
                    for module_to_del in modules_to_del:
                        del sys.modules[module_to_del]
                    module_ = importlib.import_module(import_path.stem)

                class_ = getattr(module_, plugin.plugin_class)
                plugin_object: PluginInterfaceV1 = class_(
                    self.parent(), plugin, self._base_signals, self._page_widgets)
                loaded_plugin = plugin_object
            except Exception as e:
                Logger().error(f"Can't load plugin {plugin.name}: {str(e)}")
        else:
            Logger().info(
                f"Can't load plugin {plugin.name}."
                f"Conan version restriction {plugin.conan_versions} applies.")
        if loaded_plugin:
            self._active_plugins.append(loaded_plugin)
        return loaded_plugin

    def post_load_plugins(self):
        for plugin in self._active_plugins:
            self.load_plugin.emit(plugin)
            plugin.load_signal.emit()

    def _unload_plugin(self, plugin: PluginDescription):
        plugin_widget = self.get_plugin_by_description(plugin)
        if not plugin_widget:
            Logger().error(f"Cannot get plugin {plugin.name} for unload")
            return
        self._active_plugins.remove(plugin_widget)
        plugin_widget.close()
        plugin_widget.deleteLater()
        self.unload_plugin.emit(plugin.name)

    def get_plugin_by_description(self, plugin_descr: PluginDescription) -> Optional[PluginInterfaceV1]:
        """ Return Plugin Object by full plugin description """
        for plugin in self._active_plugins:
            if isinstance(plugin, PluginInterfaceV1):
                try:
                    if plugin.plugin_description == plugin_descr:
                        return plugin
                except Exception as e:
                    Logger().error(
                        f"Can't retrive plugin information: {str(e)}")

    @staticmethod
    def eval_conan_version_spec(spec: str, conan_version: str = conan_version) -> bool:
        if not spec:
            return True
        specs = specifiers.Specifier(spec)
        return specs.contains(version.parse(conan_version))

    @staticmethod
    def is_plugin_enabled(plugin: PluginDescription):
        result = PluginHandler.eval_conan_version_spec(plugin.conan_versions)
        return result
