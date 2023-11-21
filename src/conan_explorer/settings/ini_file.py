import configparser
from copy import deepcopy
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from conan_explorer import BUILT_IN_PLUGIN, PathLike, base_path
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import get_default_file_editor
from conan_explorer.app.typing import SignatureCheckMeta

from . import (AUTO_INSTALL_QUICKLAUNCH_REFS, AUTO_OPEN_LAST_VIEW, CONSOLE_SPLIT_SIZES, 
               DEFAULT_INSTALL_PROFILE, FILE_EDITOR_EXECUTABLE, FONT_SIZE, 
               GENERAL_SECTION_NAME, GUI_STYLE, GUI_STYLE_MATERIAL, GUI_MODE_LIGHT, 
               GUI_MODE, LAST_CONFIG_FILE, LAST_VIEW, PLUGINS_SECTION_NAME,
               VIEW_SECTION_NAME, WINDOW_SIZE, SettingsInterface)


def application_settings_spec() -> Dict[str, Dict[str, Any]]:
    return {
        GENERAL_SECTION_NAME: {
            LAST_CONFIG_FILE: "",
            FILE_EDITOR_EXECUTABLE: get_default_file_editor(),
            AUTO_INSTALL_QUICKLAUNCH_REFS: False,
            DEFAULT_INSTALL_PROFILE: ""
        },
        VIEW_SECTION_NAME: {
            FONT_SIZE: 13,
            GUI_STYLE: GUI_STYLE_MATERIAL,
            GUI_MODE: GUI_MODE_LIGHT,
            WINDOW_SIZE: "0,0,800,600",
            CONSOLE_SPLIT_SIZES: "413,126",
            LAST_VIEW: "",
            AUTO_OPEN_LAST_VIEW: True,
        },
        PLUGINS_SECTION_NAME: {
            BUILT_IN_PLUGIN: str(base_path / "ui" / "plugins.ini")
        }

    }


class IniSettings(SettingsInterface, metaclass=SignatureCheckMeta):
    """
    Settings mechanism with an ini file to use as a storage.
    File and entries are automatically created from the default value of the class.
    User defined keys are now allowed for nodes specified incustom_key_enabled_sections.
    Settings should be accessed via their constant name.
    """

    def __init__(self, ini_file_path: Optional[PathLike], auto_save=True,
                 default_values: Dict[str, Dict[str, Any]
                                      ] = application_settings_spec(),
                 custom_key_enabled_sections=[PLUGINS_SECTION_NAME]):
        """
        Read config.ini file to load settings.
        Create, if not existing, but the directory must already exist!
        Default path is current working dir / settings.ini
        """
        if not ini_file_path:
            self._ini_file_path = Path().cwd() / "settings.ini"
        else:
            self._ini_file_path = Path(ini_file_path)
        self._auto_save = auto_save
        self._custom_key_enabled_sections = custom_key_enabled_sections
        self._logger = Logger()
        self._parser = configparser.ConfigParser()

        ### default setting values ###
        self._values: Dict[str, Dict[str, Any]] = deepcopy(default_values)

        # create Settings ini file, if not available for first start
        if not self._ini_file_path.is_file():
            self._ini_file_path.open('a').close()
            self._logger.info('Settings: Creating settings ini-file')
            self.save()
        else:
            self._logger.info(f'Settings: Using {self._ini_file_path}')

        self._read_ini()

    def set_auto_save(self, value):
        self._auto_save = value

    def get_settings_from_node(self, node: str) -> Tuple[str]:
        return tuple(self._values.get(node, {}).keys())

    def get(self, name: str) -> "str | int | float | bool":
        """ Get a specific setting """
        value = None
        for section in self._values.values():
            if name in section:
                value = section.get(name)
                break
        if value is None:
            raise LookupError
        return value

    def get_string(self, name: str) -> str:
        return str(self.get(name))

    def get_int(self, name: str) -> int:
        return int(self.get(name))

    def get_float(self, name: str) -> float:
        return float(self.get(name))

    def get_bool(self, name: str) -> bool:
        return bool(self.get(name))

    def set(self, name: str, value: "str|int|float|bool"):
        """ Set the value of a specific setting. 
        Does not write to file, if value is already set. """
        if name in self._values.keys() and isinstance(value, dict):  # dict type setting
            if self._values[name] == value:
                return
            self._values[name].update(value)
        else:
            for section in self._values.keys():
                if name in self._values[section]:
                    if self._values[section][name] == value:
                        return
                    self._values[section][name] = value
                    break
        if self._auto_save:
            self.save()

    def add(self, name: str, value: "str|int|float|bool", node: Optional[str]=None):
        if node is None:
            node = GENERAL_SECTION_NAME
        if not self._values.get(node):
            self._values[node] = {}
        self._values[node][name] = value
        self.save()

    def remove(self, name: str):
        for node_name, node in self._values.items():
            if name in node:
                node.pop(name)
                del self._parser[node_name][name]
                break
        self.save()

    def save(self):
        """ Save all user modifiable settings to file. """
        # save all default values
        for section in self._values.keys():
            for setting in self._values[section]:
                self._write_setting(setting, section)

        with self._ini_file_path.open('w', encoding="utf-8") as ini_file:
            self._parser.write(ini_file)

    def _read_ini(self):
        """ Read settings ini with configparser. """
        update_needed = False
        try:
            self._parser.read(self._ini_file_path, encoding="utf--8")
            for node in self._parser.sections():
                setting_keys = set(list(self._values.get(node, {}).keys()))
                if node in self._custom_key_enabled_sections:
                    setting_keys = setting_keys.union(
                        set(self._get_section(node).keys()))
                # empty section - this is a user filled dict
                if not self._values.get(node):
                    update_needed |= self._read_dict_setting(node)
                for setting in setting_keys:
                    update_needed |= self._read_setting(setting, node)

        except Exception as e:
            Logger().error((f"Settings: Can't read ini file: {str(e)}",
                             "trying to delete and create a new one..."))
            try:
                # let an exeception to the user, file can't be deleted
                os.remove(str(self._ini_file_path))
            except Exception:
                Logger().error(f"Settings: Can't delete ini file: {str(e)}.")

        # write file - to record defaults, if missing
        if not update_needed:
            return
        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _get_section(self, node: str) -> configparser.SectionProxy:
        """ Get a section from ini, or create it, if it does not exist."""
        if node not in self._parser:
            self._parser.add_section(node)
        if node not in self._values:
            self._values[node] = {}
        return self._parser[node]

    def _read_dict_setting(self, node: str) -> bool:
        """ 
        Get a dict style setting.
        Dict settings are section itself and are read dynamically.
        """
        section = self._get_section(node)
        update_needed = False
        for name in section.keys():
            update_needed |= self._read_setting(name, node)
        return update_needed

    def _read_setting(self, name: str, node: str) -> bool:
        """ Get a setting, which uses the init value to determine the type. 
        Returns, if file needs tobe updated
        """
        section = self._get_section(node)
        try:
            default_value = self.get(name)
        except Exception:
            default_value = ""
        if isinstance(default_value, dict):  # no dicts supported directly
            return False

        if name not in section:  # write out
            section[name] = str(default_value)
            return True

        value = None
        if isinstance(default_value, bool):
            value = section.getboolean(name)
        elif isinstance(default_value, str):
            value = section.get(name)
        elif isinstance(default_value, float):
            value = float(section.get(name))
        elif isinstance(default_value, int):
            value = int(section.get(name))
        if value is None:  # dict type, value will be taken as a string
            self._logger.error(
                f"Settings: Setting {name} to write is unknown", )
            return False
        if value == "" and default_value:
            value = default_value
        # autosave must be disabled temporarily, 
        # otherwise we overwrite the other settings in the file
        auto_save = self._auto_save
        self._auto_save = False
        self._values[node][name] = value
        self._auto_save = auto_save
        return False

    def _write_setting(self, name, node):
        """ Helper function to write a setting. """
        value = self.get(name)
        if isinstance(value, dict):
            return  # dicts are read only currently

        section = self._get_section(node)
        section[name] = str(value)
