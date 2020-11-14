import configparser
from pathlib import Path

from conan_app_launcher.base import Logger
from conan_app_launcher.settings import LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS


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
            # general
            LAST_CONFIG_FILE: "",
            # view
            DISPLAY_APP_CHANNELS: True,
            DISPLAY_APP_VERSIONS: True
        }

        self._read_ini()

    def get(self, name: str):
        """ Get a specific setting """
        return self._values.get(name, None)  # TODO Name checking Error

    def set(self, name: str, value):
        """ Set a specific setting """
        self._values[name] = value  # TODO Name and type checking Error

    def save_to_file(self):
        """ Save all user modifiable options to file. """
        # All writeable settings must be listed here!
        self._write_setting(LAST_CONFIG_FILE, self._GENERAL_SECTION_NAME)
        self._write_setting(DISPLAY_APP_CHANNELS, self._VIEW_SECTION_NAME)
        self._write_setting(DISPLAY_APP_CHANNELS, self._VIEW_SECTION_NAME)

        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _read_ini(self):
        """ Read settings ini with configparser. """
        self._parser.read(self._ini_file_path, encoding="UTF-8")

        # All settings and their sections must be listed here!
        general_section = self._get_section(self._GENERAL_SECTION_NAME)
        self._read_setting(LAST_CONFIG_FILE, general_section)
        view_section = self._get_section(self._VIEW_SECTION_NAME)
        self._read_setting(DISPLAY_APP_CHANNELS, view_section)
        self._read_setting(DISPLAY_APP_VERSIONS, view_section)

        # write file - to record defaults, if missing
        with self._ini_file_path.open('w', encoding="utf8") as ini_file:
            self._parser.write(ini_file)

    def _get_section(self, section_name):
        """ Helper function to get a section from ini, or create it, if it does not exist."""
        if section_name not in self._parser:
            self._parser.add_section(section_name)
        return self._parser[section_name]

    def _read_setting(self, name, section):
        """ Helper function to get a setting, which uses the init value to determine the type. """
        default_value = self._values[name]
        if not name in section:
            section[name] = str(default_value)
            return

        value = None
        if isinstance(default_value, bool):
            value = section.getboolean(name)
        elif isinstance(default_value, str):
            value = section.get(name)
        elif isinstance(default_value, float):
            value = float(section.get(name))
        elif isinstance(default_value, int):
            value = int(section.get(name))
        if value is None:
            raise Exception("Unsupported type " +
                            str(type(default_value)) + " of setting " + name)
        self._values[name] = value

    def _write_setting(self, name, section_name):
        """ Helper function to write a setting. """
        section = self._get_section(section_name)
        if not name in section:
            self._logger.error(f"Setting {name} to write is unkonwn")
        section[name] = str(self._values[name])
