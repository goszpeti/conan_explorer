
""" Use constants in class, so they don't need to be separately accessed """

from abc import abstractmethod
from typing import Optional, Tuple

from conan_explorer import PathLike

GENERAL_SECTION_NAME = "General"
VIEW_SECTION_NAME = "View"
PLUGINS_SECTION_NAME = "Plugins"

# Constants for option names (value is the entry name/id)
### General
LAST_CONFIG_FILE = "last_config_file"
FILE_EDITOR_EXECUTABLE = "file_editor"
AUTO_INSTALL_QUICKLAUNCH_REFS = "auto_install_quicklaunch"
DEFAULT_INSTALL_PROFILE = "default_install_profile"

### View
FONT_SIZE = "font_size"
GUI_STYLE = "style"
# style choices
GUI_STYLE_MATERIAL = "material"
GUI_STYLE_FLUENT = "fluent"

GUI_MODE = "mode"
# mode choices
GUI_MODE_DARK = "dark"
GUI_MODE_LIGHT = "light"

WINDOW_SIZE = "window_size"
CONSOLE_SPLIT_SIZES = "console_split_sizes"
LAST_VIEW = "last_view"
AUTO_OPEN_LAST_VIEW = "auto_open_last_view"

# Implementation types for factory
SETTINGS_INI_TYPE = "ini"
SETTINGS_QT_TYPE = "qt"  # Try this out, see issue #56


def settings_factory(type: str, source: PathLike) -> "SettingsInterface":

    if type == SETTINGS_INI_TYPE:
        from conan_explorer.settings.ini_file import IniSettings
        implementation = IniSettings(source)
    elif type == SETTINGS_QT_TYPE:
        raise NotImplementedError
    else:
        raise NotImplementedError
    return implementation

# Interface for Settings to implement


class SettingsInterface():
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
    def get_settings_from_node(self, node: str) -> Tuple[str]:
        """ Get all settings names from a hierachical node.
        If it is non-hierarchical, the name arg should be ignored and all settings returned.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> "str | int | float | bool":
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
    def set(self, name: str, value: "str|int|float|bool"):
        """ Set the value of an existing setting """
        raise NotImplementedError

    @abstractmethod
    def add(self, name: str, value: "str|int|float|bool", node: Optional[str] = None):
        """ Add a new setting """
        raise NotImplementedError

    @abstractmethod
    def remove(self, name: str):
        """ Remove a setting """
        raise NotImplementedError
