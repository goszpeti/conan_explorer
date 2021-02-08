"""
Contains global constants and basic/ui variables.
"""
__version__ = "1.0.0b0"

from pathlib import Path

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .components import ConanWorker
    from PyQt5 import QtWidgets

### Global constants ###
PROG_NAME = "conan_app_launcher"
ICON_SIZE = 60
INVALID_CONAN_REF = "Invalid/NA@NA/NA"


### Global variables ###
# 0: No debug, 1 = debug logging on
DEBUG_LEVEL = 0

# paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file
base_path: Path = Path("NULL")
asset_path: Path = Path("NULL")

# qt_application instance
qt_app: Optional["QtWidgets.QApplication"] = None
main_window: Optional["QtWidgets.QMainWindow"] = None
conan_worker: Optional["ConanWorker"] = None
current_config_file_path = Path("NULL")
