"""
Contains all basic constants used in the application.
No imports from own modules allowed! This is done to resolve circular dependencies.
"""
import os
import shutil
import platform
try:  # from Python 3.8
    from importlib.metadata import distribution, PackageNotFoundError
except ImportError:
    from importlib_metadata import distribution, PackageNotFoundError  # type: ignore
from pathlib import Path
from typing import TypeVar

PathLike = TypeVar("PathLike", str, Path)

### Global constants ###

# load metadata from package info - needs to be installed as editable in dev mode!
PKG_NAME = "conan_app_launcher"
APP_NAME = "Conan Explorer"

try:
    pkg_info = distribution(PKG_NAME)
    __version__ = pkg_info.version
    REPO_URL = pkg_info.metadata.get("home-page", "")  # type: ignore
    AUTHOR = pkg_info.metadata.get("author", "")  # type: ignore
except PackageNotFoundError:  # pragma: no cover
    # For local usecases, when there is no distribution
    __version__ = "1.0.0"
    REPO_URL = ""
    AUTHOR = ""

ICON_SIZE = 64  # Icon size (width and height) in pixels on an Applink
MAX_FONT_SIZE = 16
MIN_FONT_SIZE = 8
INVALID_PATH = "Unknown"
INVALID_CONAN_REF = "Invalid/0.0.1@NA/NA"  # used to indicate a conan reference is invalid
SETTINGS_FILE_NAME = "settings"  # for storing application settings
LEGACY_SETTINGS_FILE_NAME = ".cal_config"  # for backwards compatibility till 1.4.1
DEFAULT_UI_CFG_FILE_NAME = "ui_cfg"  # no extension from 1.4.1
LEGACY_UI_CFG_FILE_NAME = "cal_ui.json"  # for backwards compatibility till 1.4.1
CONAN_LOG_PREFIX = "CONAN: "  # logger uses this to indicate a log comes from Conan
BUILT_IN_PLUGIN = "built-in"

# Feature flags
SEARCH_APP_VERSIONS_IN_LOCAL_CACHE = True  # get versions directly from the custom cache
USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH = True  # get pkg paths directly from the custom cache TODO can't handle options
# use conan worker to also search for the package path - works in a addition to USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH and also installs
USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL = True
AUTOCLOSE_SIDE_MENU = False
ENABLE_GUI_STYLES = False

# From ennvar DEBUG - 0: No debug, 1 = debug logging on, 2 = disable true async loading
DEBUG_LEVEL = int(os.getenv("CAL_DEBUG_LEVEL", "0"))

# Conan version
conan_pkg_info = distribution("conan")
conan_version = conan_pkg_info.version

# Paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file

base_path = Path(__file__).absolute().parent
asset_path = base_path / "assets"
# to be used for all default paths of configuration files, which will be used for multiple versions
# noninvasive storage, legacy will be moved
legacy_user_save_path = Path().home()
user_save_path = Path(os.getenv("XDG_CONFIG_HOME", str(legacy_user_save_path / ".config"))) / PKG_NAME if platform.system() == "Linux" \
    else Path(os.getenv("APPDATA", str(legacy_user_save_path))) / PKG_NAME

# user path migration - move settings and default gui file
# ui file loading will handle patching the settings, if the default gui file was used
if user_save_path != legacy_user_save_path:
    os.makedirs(str(user_save_path), exist_ok=True)
    # don't copy if the migrated files already exist
    if (legacy_user_save_path / LEGACY_SETTINGS_FILE_NAME).exists() and \
            not (user_save_path / (SETTINGS_FILE_NAME + ".ini")).exists():
        print(f"INFO: Moving application settings file from {str(user_save_path)} to {str(legacy_user_save_path)}")
        shutil.move(str(legacy_user_save_path / LEGACY_SETTINGS_FILE_NAME),
                    str(user_save_path / (SETTINGS_FILE_NAME + ".ini")))
    if (legacy_user_save_path / LEGACY_UI_CFG_FILE_NAME).exists() and \
            not (user_save_path / (DEFAULT_UI_CFG_FILE_NAME + ".json")).exists():
        print(f"INFO: Moving default ui config file from {str(user_save_path)} to {str(legacy_user_save_path)}")
        shutil.move(str(legacy_user_save_path / LEGACY_UI_CFG_FILE_NAME),
                    str(user_save_path / (DEFAULT_UI_CFG_FILE_NAME + ".json")))
