
""" Use constants in class, so they don't need to be separately accessed """

from abc import ABC, abstractmethod
from typing import Union

from conan_app_launcher import PathLike

# Constants for option names (value is the entry name/id)
# General
LAST_CONFIG_FILE = "last_config_file"
# Views
DISPLAY_APP_VERSIONS = "disp_app_versions"
DISPLAY_APP_USERS = "disp_app_users"
DISPLAY_APP_CHANNELS = "disp_app_channels"
APPLIST_ENABLED = "enable_app_list"

# enable combobox for app user/channel/version
ENABLE_APP_COMBO_BOXES = "enable_app_link_combo_boxes"
FONT_SIZE = "font_size"
GUI_STYLE = "style"
# style choices
GUI_STYLE_DARK = "dark"
GUI_STYLE_LIGHT = "light"

WINDOW_SIZE = "window_size"
CONSOLE_SPLIT_SIZES = "console_split_sizes"

# Implementation types for factory
SETTINGS_INI_TYPE = "ini"
SETTINGS_QT_TYPE = "qt"  # Try this out, see issue #56


def settings_factory(type: str, source: PathLike) -> "SettingsInterface":

    if type == SETTINGS_INI_TYPE:
        from conan_app_launcher.settings.ini_file import IniSettings
        implementation = IniSettings(source)
    elif type == SETTINGS_QT_TYPE:
        raise NotImplementedError
    else:
        raise NotImplementedError
    return implementation

# Interface for Settings to implement


class SettingsInterface(ABC):
    """
    Abstract Class to implement settings mechanisms.
    Source artefact location is passed by constructor and not changeable.
    """

    @abstractmethod
    def set_auto_save(self, value):
        """ Enable auto save feature, so every value change triggers a save. """
        raise NotImplementedError

    @abstractmethod
    def save(self):
        """ Save all user modifiable settings. """
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> Union[str, int, float, bool]:
        """ Default getter, not good for typing """
        raise NotImplementedError

    @abstractmethod
    def get_string(self, name: str) -> str:
        """ Get a string cast to a string """
        raise NotImplementedError

    @abstractmethod
    def get_int(self, name: str) -> int:
        """ Get a string cast to an int """
        raise NotImplementedError

    @abstractmethod
    def get_float(self, name: str) -> float:
        """ Get a string cast to a float """
        raise NotImplementedError

    @abstractmethod
    def get_bool(self, name: str) -> bool:
        """ Get a string cast to a bool """
        raise NotImplementedError

    @abstractmethod
    def set(self, setting_name: str, value: Union[str, int, float, bool]):
        """ Set the value of a specific setting """
        raise NotImplementedError
