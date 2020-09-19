import configparser
import logging
from pathlib import Path

from app_grid_conan.config import PROG_NAME
from app_grid_conan.settings import (FONT_SCALING)


class Settings():
    """
    Settings mechanism with an ini file to use as a storage.
    File and entries are automatically created form the defaulkt value of the class.
    """

    # internal constants
    _GUI_SECTION_NAME = "GUI"
    _GENERAL_SECTION_NAME = "General"

    def __init__(self, ini_folder=None):
        """
        Read config.ini file to load settings.
        Verify config.ini existence, if folder is passed.
        """
        self._logger = logging.getLogger(PROG_NAME)
        self._parser = configparser.ConfigParser()
        self._ini_file_path = Path()
        if ini_folder is not None:
            ini_folder = Path(ini_folder)
            self._ini_file_path = ini_folder / "config.ini"
        # create Settings ini file, if not available for first start
        if not self._ini_file_path.is_file():
            self._ini_file_path.open('a').close()
            self._logger.warning('Settings: Creating settings ini-file')
        else:
            self._logger.info('Settings: Using %s', self._ini_file_path)

        ### default setting values ###
        self._values = {
            # general

            # gui
            FONT_SCALING: 1,
        }

        self._read_ini()

    def get(self, name: str):
        """ Get a specific setting """
        return self._values.get(name, None)  # TODO Name checking Error

    def set(self, name: str, value):
        """ Get a specific setting """
        self._values[name] = value  # TODO Name and type checking Error

    def _read_ini(self):
        """ Read settings ini with configparser. """
        self._parser.read(self._ini_file_path, encoding="UTF-8")

        general_section = self._get_section(self._GENERAL_SECTION_NAME)

        gui_section = self._get_section(self._GUI_SECTION_NAME)
        self._read_option(FONT_SCALING, gui_section)

        # write file - to record defaults, if missing
        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _get_section(self, section_name):
        """ Helper function to get a section from ini, or create it, if it does not exist."""
        if section_name not in self._parser:
            self._parser.add_section(section_name)
        return self._parser[section_name]

    def _read_option(self, option_name, section):
        """ Helper function to get an option, which uses the init value to determine the type. """
        default_value = self._values[option_name]
        if not option_name in section:
            section[option_name] = str(default_value)
            return

        value = None
        if isinstance(default_value, bool):
            value = section.getboolean(option_name)
        elif isinstance(default_value, str):
            value = section.get(option_name)
        elif isinstance(default_value, float):
            value = float(section.get(option_name))
        elif isinstance(default_value, int):
            value = int(section.get(option_name))
        if value is None:
            raise Exception("Unsupported type " +
                            str(type(default_value)) + " of setting " + option_name)
        self._values[option_name] = value

    def save_all_options(self):
        """ Save all user modifiable options to file. """
        self._write_option(FONT_SCALING, self._GUI_SECTION_NAME)

        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _write_option(self, option_name, section_name):
        """ Helper function to write an option. """
        section = self._get_section(section_name)
        if not option_name in section:
            self._logger.error("Option %s to write is unkonwn", option_name)
        section[option_name] = str(self._values[option_name])
