"""
Contains all basic constants used in the application.
No imports from own modules allowed!
"""
import os
from pathlib import Path
from typing import TypeVar

PathLike = TypeVar("PathLike", str, Path)

### Global constants ###
from .__version__ import __version__

PROG_NAME = "conan_app_launcher"
ICON_SIZE = 60
INVALID_CONAN_REF = "Invalid/NA@NA/NA"
SETTINGS_FILE_NAME = ".cal_config"
DEFAULT_UI_CFG_FILE_NAME = "cal_ui.json"  # for legacy 0.X support

# Feature flags
ADD_TAB_BUTTON = False  # FIXME currently not working
ADD_APP_LINK_BUTTON = False  # FIXME currently not working
SEARCH_APP_VERSIONS_IN_LOCAL_CACHE = True
USE_LOCAL_INTERNAL_CACHE = True
USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH = True

# From ennvar DEBUG - 0: No debug, 1 = debug logging on
DEBUG_LEVEL = int(os.getenv("CAL_DEBUG_LEVEL", "0"))

# Paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file
base_path = Path(__file__).absolute().parent
asset_path = base_path / "assets"
# to be used for all default paths of configuration files, which will be used for multiple versions
user_save_path = Path().home()
