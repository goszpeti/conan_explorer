"""
Contains all basic constants used in the application.
No imports from own modules allowed!
"""
import os
try: # from Python 3.8
    from importlib.metadata import distribution
except:
    from importlib_metadata import distribution

from pathlib import Path
from typing import TypeVar

PathLike = TypeVar("PathLike", str, Path)

### Global constants ###

# load metadata from package info - needs to be installed as editable in dev mode!
PKG_NAME = "conan_app_launcher"
pkg_info = distribution(PKG_NAME)
__version__ = pkg_info.version
REPO_URL = pkg_info.metadata.get("home-page", "")
AUTHOR = pkg_info.metadata.get("author", "")

ICON_SIZE = 60 # Icon size (width and height) in pixels on an Applink
INVALID_CONAN_REF = "Invalid/NA@NA/NA" # used to indicate a conan reference is invalid
SETTINGS_FILE_NAME = ".cal_config" # for storing application settings
DEFAULT_UI_CFG_FILE_NAME = "cal_ui.json"  # for legacy 0.X support
CONAN_LOG_PREFIX = "CONAN: " # logger uses this to indicate a log comes from Conan

# Feature flags
ADD_TAB_BUTTON = False # a fixed "Add tab" button on the AppGrid
ADD_APP_LINK_BUTTON = False  # a fixed "Add AppLink" button on the AppGrid
SEARCH_APP_VERSIONS_IN_LOCAL_CACHE = True # get versions directly from the custom cache
USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH = True  # get pkg paths directly from the custom cache
# use conan worker to also search for the package path - works in a addition to USE_LOCAL_CACHE_FOR_LOCAL_PKG_PATH and also installs
USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL = True

# From ennvar DEBUG - 0: No debug, 1 = debug logging on
DEBUG_LEVEL = int(os.getenv("CAL_DEBUG_LEVEL", "0"))

# Paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file

base_path = Path(__file__).absolute().parent
asset_path = base_path / "assets"
# to be used for all default paths of configuration files, which will be used for multiple versions
user_save_path = Path().home()
