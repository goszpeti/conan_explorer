import configparser
import importlib
import sys
import types
from packaging import specifiers, version

import os
from dataclasses import dataclass
from pathlib import Path
import uuid
from typing import TYPE_CHECKING, List, Optional
from conan_app_launcher import BUILT_IN_PLUGIN, conan_version

import conan_app_launcher.app as app
from conan_app_launcher import base_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import PLUGINS_SECTION_NAME
from PySide6.QtCore import Signal, QObject, SignalInstance
from PySide6.QtWidgets import QWidget, QSizePolicy

from ..fluent_window.fluent_window import ThemedWidget

if TYPE_CHECKING:
    from conan_app_launcher.ui.fluent_window import FluentWindow
    from conan_app_launcher.ui.main_window import BaseSignals


@dataclass
class PluginDescription():
    name: str  # Display name, also used as page title
    version: str
    author: str
    icon: str  # left menu icon
    import_path: str  # this path will be placed on python path or a file directly
    plugin_class: str  # class to be loaded from module
    description: str
    side_menu: bool  # will create a side menu, which can be accessed by page_widgets
    conan_versions: str  # restrict the plugin to a conan version (will be greyed out)


class PluginInterfaceV1(ThemedWidget):
    """
    Class to extend the application with custom views.
    """
    # Return a signal, which will be called, when the Ui should load.
    # Connect this to your actual load method.
    # This is used for asynchronous loading.
    load_signal: SignalInstance = Signal()  # type: ignore

    def __init__(self, parent: QWidget, plugin_description: PluginDescription,
                 base_signals: Optional["BaseSignals"] = None,
                 page_widgets: Optional["FluentWindow.PageStore"] = None) -> None:
        ThemedWidget.__init__(self, parent)
        self._base_signals = base_signals
        self._page_widgets = page_widgets
        # save PluginDescription to query data from outside
        self.plugin_description = plugin_description
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, a0) -> None:
        # handles maximum size on resize
        if not self._base_signals:
            super().resizeEvent(a0)
            return
        self._base_signals.page_size_changed.emit(self)
        super().resizeEvent(a0)


class PluginFile():

    @staticmethod
    def register(plugin_path: str):
        plugin_path_obj = Path(plugin_path)
        # check, if path already registered
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_file_path = app.active_settings.get_string(plugin_group_name)
            if Path(plugin_file_path) == plugin_path_obj:
                return
        app.active_settings.add(str(uuid.uuid1()), plugin_path, PLUGINS_SECTION_NAME)

    @staticmethod
    def unregister(plugin_path: str):
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_file_path = app.active_settings.get_string(plugin_group_name)
            if Path(plugin_file_path) == plugin_path:
                app.active_settings.remove(plugin_group_name)

    @staticmethod
    def read_file(plugin_file_path: str) -> List[PluginDescription]:
        if not os.path.exists(plugin_file_path):
            pass  # error
        plugins = []
        parser = configparser.ConfigParser()
        parser.read(plugin_file_path, encoding="UTF-8")
        for section in parser.keys():
            if parser.default_section == section:
                continue
            plugin_info = parser[section]
            try:
                name = plugin_info.get("name")
                assert name, "field 'name' is required"
                version = plugin_info.get("version", "None")

                icon_str = plugin_info.get("icon")
                assert icon_str, "field 'icon' is required"
                if version == BUILT_IN_PLUGIN:
                    icon = icon_str
                else:
                    icon = str(Path(plugin_file_path).parent / icon_str)

                import_path = Path(plugin_file_path).parent / plugin_info.get("import_path")
                assert import_path, "field 'import_path' is required"
                # import_path =  / import_path_str
                assert import_path.exists(), f"import_path {str(import_path)} does not exist"
                if import_path.is_dir():  # needs an __init__.py
                    assert (import_path / "__init__.py").exists()

                plugin_class = plugin_info.get("plugin_class")
                assert plugin_class, "field 'plugin_class' is required"
                description = plugin_info.get("description", "")
                author = plugin_info.get("author", "Unknown")
                from distutils.util import strtobool
                side_menu = bool(strtobool(plugin_info.get("side_menu", "False")))
                conan_versions = plugin_info.get("conan_versions", "")
                desc = PluginDescription(name, version, author, icon, str(import_path),
                                         plugin_class, description, side_menu, conan_versions)
                plugins.append(desc)
            except Exception as e:
                Logger().error(f"Can't read {section} plugin information from {plugin_file_path}: {str(e)}.")

        return plugins

    @staticmethod
    def write(path: str, infos: List[PluginDescription]):
        parser = configparser.ConfigParser()

        for i in range(len(infos)):
            section_name = "PluginDescription" + str(i)
            parser.add_section(section_name)
            for setting, value in infos[i].__dict__.items():
                parser[section_name][setting] = str(value)
        with open(path, 'w', encoding="utf8") as fd:
            parser.write(fd)


class PluginHandler(QObject):
    # Both signals need to be connected in the main gui
    load_plugin: SignalInstance = Signal(PluginDescription)  # type: ignore
    unload_plugin: SignalInstance = Signal(str)  # type: ignore

    def __init__(self, parent: Optional[QObject], base_signals, page_widgets) -> None:
        super().__init__(parent)
        self._base_signals = base_signals
        self._page_widgets = page_widgets

    def load_all_plugins(self):
        # load built-in from dynamic path
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            if plugin_group_name == BUILT_IN_PLUGIN:
                # fix potentially outdated setting
                correct_plugin_path = str(base_path / "ui" / "plugins.ini")
                if plugin_path != correct_plugin_path:
                    app.active_settings.add(BUILT_IN_PLUGIN, correct_plugin_path, PLUGINS_SECTION_NAME)
                    plugin_path = correct_plugin_path
            self._load_plugins_from_file(plugin_path)

    def get_plugin_descr_from_name(self, plugin_name: str) -> Optional[PluginDescription]:
        plugins = self.get_same_file_plugins_from_name(plugin_name)
        for plugin in plugins:
            if plugin.name == plugin_name:
                return plugin

    def get_same_file_plugins_from_name(self, plugin_name: str) -> List[PluginDescription]:
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            plugin_path = app.active_settings.get_string(plugin_group_name)
            file_plugins = PluginFile.read_file(plugin_path)
            for plugin in file_plugins:
                if plugin.name == plugin_name:
                    return file_plugins
        return []

    def add_plugin(self, plugin_path: str):
        PluginFile.register(plugin_path)
        self._load_plugins_from_file(plugin_path)

    def remove_plugin(self, plugin_path: str):
        file_plugins = PluginFile.read_file(plugin_path)
        PluginFile.unregister(plugin_path)
        for plugin in file_plugins:
            self._unload_plugin(plugin)

    def reload_plugin(self, plugin_name: str):
        plugin = self.get_plugin_descr_from_name(plugin_name)
        assert plugin
        self._unload_plugin(plugin)
        self._load_plugin(plugin, reload=True)

    def _load_plugins_from_file(self, plugin_path: str):
        file_plugins = PluginFile.read_file(plugin_path)
        for plugin in file_plugins:
            self._load_plugin(plugin)

    def _load_plugin(self, plugin: PluginDescription, reload=False):
        if self.is_plugin_enabled(plugin):
            try:
                import_path = Path(plugin.import_path)
                sys.path.append(str(import_path.parent))
                module_ = importlib.import_module(import_path.stem)
                if reload:
                    modules_to_del = [x for x in sys.modules if import_path.stem in x]
                    # importlib reload does not work with relative imports
                    for module_to_del in modules_to_del:
                        del sys.modules[module_to_del]
                    module_ = importlib.import_module(import_path.stem)

                class_ = getattr(module_, plugin.plugin_class)
                plugin_object: PluginInterfaceV1 = class_(self.parent(), plugin, self._base_signals, self._page_widgets)
                self.load_plugin.emit(plugin_object)
                plugin_object.load_signal.emit()
            except Exception as e:
                Logger().error(f"Can't load plugin {plugin.name}: {str(e)}")
        else:
            Logger().info(
                f"Can't load plugin {plugin.name}. Conan version restriction {plugin.conan_versions} applies.")

    def _unload_plugin(self, plugin: PluginDescription):
        if not self.is_plugin_enabled(plugin):
            return
        self.unload_plugin.emit(plugin.name)

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
