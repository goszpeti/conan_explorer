"""
Contains global constants and basic/ui variables.
"""
__version__ = "0.4.0"

from pathlib import Path

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .components.conan import ConanWorker
    from PyQt5 import QtWidgets

### Global constants ###
PROG_NAME = "conan_app_launcher"
ICON_SIZE = 64

### Global variables ###
# 0: No debug, 1 = logging on, 2: remote debugging on
# 3: wait for remote debugger, multiprocessing off
DEBUG_LEVEL = 0

# paths to find folders
base_path: Path = Path()

# qt_application instance
qt_app: Optional["QtWidgets.QApplication"] = None
conan_worker: Optional["ConanWorker"] = None
