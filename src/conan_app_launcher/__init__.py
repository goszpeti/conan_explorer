"""
Contains global constants and basic/ui variables.
"""
from .__version__ import VERSION
from pathlib import Path

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:  # pragma: no cover
    from .components import ConanWorker, ConanInfoCache, TabConfigEntry, ConanApi
    from .components.conan_worker import ConanWorkerElement
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
# TODO this is not an issue anymore!
base_path: Path = Path("NULL")
asset_path: Path = Path("NULL")

qt_app: Optional["QtWidgets.QApplication"] = None
main_window: Optional["QtWidgets.QMainWindow"] = None
conan_api: Optional["ConanApi"] = None
conan_worker: Optional["ConanWorker"] = None
cache: Optional["ConanInfoCache"] = None
active_settings: Optional["Settings"] = None # can't name it settings - will clash with settings module
tab_configs: List["TabConfigEntry"] = []

def get_all_conan_refs():
    conan_refs: List[ConanWorkerElement] = []
    for tab in tab_configs:
        for app in tab.get_app_entries():
            ref_dict: ConanWorkerElement = {"reference": str(app.conan_ref), "options": app.conan_options}
            if ref_dict not in conan_refs:
                conan_refs.append(ref_dict)
    return conan_refs
