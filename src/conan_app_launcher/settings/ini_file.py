import configparser
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from conan_app_launcher import PathLike
from conan_app_launcher.app.logger import Logger

from . import (APPLIST_ENABLED, CONSOLE_SPLIT_SIZES, DISPLAY_APP_CHANNELS, DISPLAY_APP_USERS, DISPLAY_APP_VERSIONS,
               ENABLE_APP_COMBO_BOXES, FONT_SIZE, GUI_STYLE, GUI_STYLE_LIGHT,
               LAST_CONFIG_FILE, WINDOW_SIZE, SettingsInterface)


class IniSettings(SettingsInterface):
    """
    Settings mechanism with an ini file to use as a storage.
    File and entries are automatically created from the default value of the class.
    All entries need to be entered in the default values, no runtime registration.
    Settings should be accessed via their constant name.
    """
    # internal constants
    _GENERAL_SECTION_NAME = "General"
    _VIEW_SECTION_NAME = "View"

    def __init__(self, ini_file_path: Optional[PathLike], auto_save=True):
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

        self._logger = Logger()
        self._parser = configparser.ConfigParser()
        # create Settings ini file, if not available for first start
        if not self._ini_file_path.is_file():
            self._ini_file_path.open('a').close()
            self._logger.info('Settings: Creating settings ini-file')
        else:
            self._logger.info(f'Settings: Using {self._ini_file_path}')

        ### default setting values ###
        self._values: Dict[str, Dict[str, Any]] = {
            self._GENERAL_SECTION_NAME: {
                LAST_CONFIG_FILE: "",
            },
            self._VIEW_SECTION_NAME: {
                FONT_SIZE: 12,
                GUI_STYLE: GUI_STYLE_LIGHT,
                ENABLE_APP_COMBO_BOXES: False,
                APPLIST_ENABLED: True,
                DISPLAY_APP_CHANNELS: True,
                DISPLAY_APP_USERS: False,
                DISPLAY_APP_VERSIONS: True,
                WINDOW_SIZE: "0,0,800,600",
                CONSOLE_SPLIT_SIZES: "413,126"
            },
        }

        self._read_ini()

    def set_auto_save(self, value):
        self._auto_save = value

    def get(self, name: str) -> Union[str, int, float, bool]:
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

    def set(self, setting_name: str, value: Union[str, int, float, bool]):
        """ Set the value of a specific setting. Does not write to file, if value is already set. """
        if setting_name in self._values.keys() and isinstance(value, dict):  # dict type setting
            if self._values[setting_name] == value:
                return
            self._values[setting_name].update(value)
        else:
            for section in self._values.keys():
                if setting_name in self._values[section]:
                    if self._values[section][setting_name] == value:
                        return
                    self._values[section][setting_name] = value
                    break
        if self._auto_save:
            self.save()

    def save(self):
        """ Save all user modifiable settings to file. """
        for section in self._values.keys():
            for setting in self._values[section]:
                self._write_setting(setting, section)

        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _read_ini(self):
        """ Read settings ini with configparser. """
        update_needed = False
        try:
            self._parser.read(self._ini_file_path, encoding="UTF-8")
            for section in self._values.keys():
                if not self._values[section]:  # empty section - this is a user filled dict
                    update_needed |= self._read_dict_setting(section)
                for setting in self._values[section]:
                    update_needed |= self._read_setting(setting, section)
        except Exception as e:
            Logger().error(
                f"Settings: Can't read ini file: {str(e)}, trying to delete and create a new one...")
            os.remove(str(self._ini_file_path))  # let an exeception to the user, file can't be deleted

        # write file - to record defaults, if missing
        if not update_needed:
            return
        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _get_section(self, section_name: str) -> configparser.SectionProxy:
        """ Helper function to get a section from ini, or create it, if it does not exist."""
        if section_name not in self._parser:
            self._parser.add_section(section_name)
        return self._parser[section_name]

    def _read_dict_setting(self, section_name: str) -> bool:
        """ 
        Helper function to get a dict style setting.
        Dict settings are section itself and are read dynamically.
        """
        section = self._get_section(section_name)
        update_needed = False
        for setting_name in section.keys():
            update_needed |= self._read_setting(setting_name, section_name)
        return update_needed

    def _read_setting(self, setting_name: str, section_name: str) -> bool:
        """ Helper function to get a setting, which uses the init value to determine the type. 
        Returns, if file needs tobe updated
        """
        section = self._get_section(section_name)
        default_value = self.get(setting_name)
        if isinstance(default_value, dict):  # no dicts supported directly
            return False

        if setting_name not in section:  # write out
            section[setting_name] = str(default_value)
            return True

        value = None
        if isinstance(default_value, bool):
            value = section.getboolean(setting_name)
        elif isinstance(default_value, str):
            value = section.get(setting_name)
        elif isinstance(default_value, float):
            value = float(section.get(setting_name))
        elif isinstance(default_value, int):
            value = int(section.get(setting_name))
        if value is None:  # dict type, value will be taken as a string
            self._logger.error(f"Settings: Setting {setting_name} to write is unknown", )
            return False
        # autosave must be disabled, otherwise we overwrite the other settings in the file
        auto_save = self._auto_save
        self._auto_save = False
        self.set(setting_name, value)
        self._auto_save = auto_save
        return False

    def _write_setting(self, setting_name, section_name):
        """ Helper function to write a setting. """
        value = self.get(setting_name)
        if isinstance(value, dict):
            return  # dicts are read only currently

        section = self._get_section(section_name)
        if setting_name not in section:
            self._logger.error(f"Settings: Setting {setting_name} to write is unknown")
        section[setting_name] = str(value)
