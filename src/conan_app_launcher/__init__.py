"""
Contains global constants and basic/ui variables.
"""

from pathlib import Path

from PyQt5 import QtWidgets

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .conan import ConanWorker

### Global constants ###
__version__ = "0.1.0"
PROG_NAME = "conan_app_launcher"

### Global variables ###
# 0: No debug, 1 = logging on, display IP in options, 2: remote debugging on
# 3: wait for remote debugger, multiprocessing off
DEBUG_LEVEL = 0
ICON_SIZE = 64

# paths to find folders
base_path: Path = Path()
config_path = Path()

# qt_application instance
qt_app: Optional[QtWidgets.QApplication] = None
conan_worker: Optional["ConanWorker"] = None
