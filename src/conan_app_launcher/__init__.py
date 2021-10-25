"""
Contains global constants and basic/ui variables.
"""
__version__ = "1.0.0b7"

from pathlib import Path

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from .components import ConanWorker, ConanInfoCache, TabConfigEntry
    from .settings import Settings
    from PyQt5 import QtWidgets

### Global constants ###
PROG_NAME = "conan_app_launcher"
ICON_SIZE = 60
INVALID_CONAN_REF = "Invalid/NA@NA/NA"
DEFAULT_GRID_CONFIG_FILE_NAME = "cal_ui.json"
SETTINGS_FILE_NAME = ".cal_config"
CACHE_FILE_NAME = "cache.json"

# Feature flags
ADD_TAB_BUTTON = False  # FIXME currently not working
ADD_APP_LINK_BUTTON = False # FIXME currently not working
SEARCH_APP_VERSIONS_IN_LOCAL_CACHE = True
USE_LOCAL_INTERNAL_CACHE = True
USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH = True

# 0: No debug, 1 = debug logging on
DEBUG_LEVEL = 0

### Global variables ###

# paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file
base_path: Path = Path("NULL")
asset_path: Path = Path("NULL")

qt_app: Optional["QtWidgets.QApplication"] = None
main_window: Optional["QtWidgets.QMainWindow"] = None
conan_worker: Optional["ConanWorker"] = None
cache: Optional["ConanInfoCache"] = None
settings: Optional["Settings"] = None
tab_configs: List["TabConfigEntry"] = []
