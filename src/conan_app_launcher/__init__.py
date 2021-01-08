"""
Contains global constants and basic/ui variables.
"""
__version__ = "0.6.1"

from pathlib import Path

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .components import ConanWorker
    from PyQt5 import QtWidgets

### Global constants ###
PROG_NAME = "conan_app_launcher"
ICON_SIZE = 64

### Global variables ###
# 0: No debug, 1 = debug logging on
DEBUG_LEVEL = 0

# paths to find folders - points to the folder of this file
# must be initialized later, otherwise setup.py can't parse this file
base_path: Path = Path("NULL")
default_icon: Path = Path("NULL")

# qt_application instance
qt_app: Optional["QtWidgets.QApplication"] = None
conan_worker: Optional["ConanWorker"] = None
