import configparser

from pathlib import Path
import uuid
from typing import List, Union
from conan_explorer import BUILT_IN_PLUGIN

import conan_explorer.app as app
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import str2bool
from conan_explorer.settings import PLUGINS_SECTION_NAME
from conan_explorer.ui.plugin.types import PluginDescription

class PluginValidationException(Exception):
    ...


class PluginFile():
    """ 
    Plugin file related methods.
    Format implemented as ini file.
    """

    @staticmethod
    def register(plugin_file_path: Union[Path, str]):
        """ Register the given file into the application settings with a uuid. """
        plugin_file_path = Path(plugin_file_path)
        # check, if path already registered
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            settings_plugin_file_path = app.active_settings.get_string(
                plugin_group_name)
            if Path(settings_plugin_file_path) == plugin_file_path:
                return
        app.active_settings.add(str(uuid.uuid1()), str(
            plugin_file_path), PLUGINS_SECTION_NAME)

    @staticmethod
    def unregister(plugin_file_path: Union[Path, str]):
        """ Unregister given plugin file from application settings """
        plugin_file_path = Path(plugin_file_path)
        for plugin_group_name in app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME):
            settings_plugin_file_path = app.active_settings.get_string(
                plugin_group_name)
            if Path(settings_plugin_file_path) == plugin_file_path:
                app.active_settings.remove(plugin_group_name)

    @staticmethod
    def read(plugin_file_path: Union[Path, str]) -> List[PluginDescription]:
        """ Read given plugin file and return list of contained plugin descriptions. """
        plugin_file_path = Path(plugin_file_path)
        if not plugin_file_path.is_file():
            Logger().error(f"Plugin file {plugin_file_path} does not exist.")
            return []  # error
        plugins = []
        parser = configparser.ConfigParser()
        parser.read(plugin_file_path, encoding="utf-8")
        PVE = PluginValidationException
        for section in parser.keys():
            if parser.default_section == section:
                continue
            plugin_info = parser[section]
            try:
                name = plugin_info.get("name")
                if not name:
                    raise PVE("field 'name' is required")
                version = plugin_info.get("version", "Unknown")

                icon_str = plugin_info.get("icon")
                if not icon_str:
                    raise PVE("field 'icon' is required")
                if version == BUILT_IN_PLUGIN:
                    icon = icon_str
                else:
                    icon_path = plugin_file_path.parent / icon_str
                    if not icon_path.is_file():
                        raise PVE(f"icon {str(icon_path)} does not exist.") 
                    icon = str(icon_path)

                if not plugin_info.get("import_path"):
                    raise PVE("field 'import_path' is required")
                import_path = plugin_file_path.parent / plugin_info.get("import_path")
                if not import_path.is_dir():
                    raise PVE(f"import_path {str(import_path)} does not exist.")
                if import_path.is_dir():  # needs an __init__.py
                    init_py_path = import_path / "__init__.py"
                    init_pyc_path = import_path / "__init__.pyc" # for precompiled
                    if not (init_py_path.exists() or init_pyc_path.exists()):
                        raise PVE(f"{str(init_py_path)} does not exist")

                plugin_class = plugin_info.get("plugin_class")
                if not plugin_class:
                    raise PVE("field 'plugin_class' is required")
                description = plugin_info.get("description", "")
                author = plugin_info.get("author", "Unknown")
                side_menu = str2bool(plugin_info.get("side_menu", "False"))
                conan_versions = plugin_info.get("conan_versions", "")
                desc = PluginDescription(name, version, author, icon, str(import_path),
                                         plugin_class, description, side_menu, conan_versions)
                plugins.append(desc)
            except Exception as e:
                Logger().error(
                    f"Can't read {section} plugin information from {plugin_file_path}: {str(e)}.")

        return plugins

    @staticmethod
    def write(plugin_file_path: Union[Path, str], plugin_descriptions: List[PluginDescription]):
        """ Write plugin file to specified path with the given the plugin descripton """
        parser = configparser.ConfigParser()
        for i, description in enumerate(plugin_descriptions):
            section_name = "PluginDescription" + str(i)
            parser.add_section(section_name)
            for setting, value in description.__dict__.items():
                parser[section_name][setting] = str(value)
        with open(plugin_file_path, 'w', encoding="utf-8") as fd:
            parser.write(fd)
