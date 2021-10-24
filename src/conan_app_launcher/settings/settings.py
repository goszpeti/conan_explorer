import configparser
from pathlib import Path
from typing import Union

from conan_app_launcher.base import Logger
from conan_app_launcher.settings import (
    LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS, GRID_COLUMNS, GRID_ROWS)


class Settings():
    """
    Settings mechanism with an ini file to use as a storage.
    File and entries are automatically created from the default value of the class.
    """

    # internal constants
    _GENERAL_SECTION_NAME = "General"
    _VIEW_SECTION_NAME = "View"

    def __init__(self, ini_file: Path):
        """
        Read config.ini file to load settings.
        Verify config.ini existence, if folder is passed.
        """
        self._logger = Logger()
        self._parser = configparser.ConfigParser()
        self._ini_file_path = ini_file
        # create Settings ini file, if not available for first start
        if not self._ini_file_path.is_file():
            self._ini_file_path.open('a').close()
            self._logger.debug('Settings: Creating settings ini-file')
        else:
            self._logger.debug(f'Settings: Using {self._ini_file_path}')

        ### default setting values ###
        self._values = {
            self._GENERAL_SECTION_NAME: {
                    LAST_CONFIG_FILE: "",
                },
            self._VIEW_SECTION_NAME: {
                    DISPLAY_APP_CHANNELS: True,
                    DISPLAY_APP_VERSIONS: True,
                    GRID_ROWS: 20,
                    GRID_COLUMNS: 4,
            },
        }

        self._read_ini()

    def get(self, name: str) -> Union[str, int, float, bool]:
        """ Get a specific setting """
        value = None
        for section in self._values:
            if name in self._values[section]:
                value = self._values[section].get(name)
                break
        return value

    def get_string(self, name: str) -> str:
        return str(self.get(name))

    def get_int(self, name: str) -> int:
        return int(self.get(name))

    def get_float(self, name: str) -> float:
        return float(self.get(name))

    def get_bool(self, name: str) -> bool:
        return bool(self.get(name))

    def set(self, setting_name: str, value):
        """ Set the value of a specific setting """
        if setting_name in self._values.keys() and isinstance(value, dict): # dict type setting
            self._values[setting_name].update(value)
        else:
            for section in self._values.keys():
                if setting_name in self._values[section]:
                    self._values[section][setting_name] = value
                    break
        # autosave
        self.save_to_file()

    def save_to_file(self):
        """ Save all user modifiable settings to file. """
        for section in self._values.keys():
            for setting in self._values[section]:
                self._write_setting(setting, section)

        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _read_ini(self):
        """ Read settings ini with configparser. """
        self._parser.read(self._ini_file_path, encoding="UTF-8")

        for section in self._values.keys():
            if not self._values[section]: # empty section - this is a user filled dict
                self._read_dict_setting(section)
            for setting in self._values[section]:
                self._read_setting(setting, section)

        # write file - to record defaults, if missing
        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _get_section(self, section_name) -> configparser.SectionProxy:
        """ Helper function to get a section from ini, or create it, if it does not exist."""
        if section_name not in self._parser:
            self._parser.add_section(section_name)
        return self._parser[section_name]

    def _read_dict_setting(self, section_name):
        """ 
        Helper function to get a dict style setting.
        Dict settings are section itself and are read dynamically.
        """
        section = self._get_section(section_name)

        for setting_name in section.keys():
            self._read_setting(setting_name, section_name)

    def _read_setting(self, setting_name, section_name):
        """ Helper function to get a setting, which uses the init value to determine the type. """
        section = self._get_section(section_name)
        default_value = self.get(setting_name)
        if isinstance(default_value, dict):  # no dicts supported directly
           return

        if not setting_name in section:  # write out
            section[setting_name] = str(default_value)
            return

        value = None
        if isinstance(default_value, bool):
            value = section.getboolean(setting_name)
        elif isinstance(default_value, str):
            value = section.get(setting_name)
        elif isinstance(default_value, float):
            value = float(section.get(setting_name))
        elif isinstance(default_value, int):
            value = int(section.get(setting_name))
        if value is None: # dict type, value will be taken as a string
            value = section.get(setting_name)
            self.set(section_name, {setting_name: value})
            return

        self.set(setting_name, value)

    def _write_setting(self, setting_name, section_name):
        """ Helper function to write a setting. """
        value = self.get(setting_name)
        if isinstance(value, dict):
            return  # dicts are read only currently

        section = self._get_section(section_name)
        if not setting_name in section:
            self._logger.error("Setting %s to write is unkonwn", setting_name)
        section[setting_name] = str(value)
