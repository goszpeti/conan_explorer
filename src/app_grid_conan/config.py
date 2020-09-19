"""
Contains global constants and basic/ui variables.
Note: sensors where moved to component handler in base.
"""

from pathlib import Path

from PyQt5 import QtWidgets

### Global constants ###
PROG_NAME = "app_grid_conan"

### Global variables ###
# 0: No debug, 1 = logging on, display IP in options, 2: remote debugging on
# 3: wait for remote debugger, multiprocessing off
DEBUG_LEVEL = 0
ICON_SIZE = 64

# paths to find folders
base_path: Path = Path(__file__).absolute().parent.parent
resource_path: Path = base_path / "resources"
config_path = Path("app_config.json")

# qt_application instance
qt_app: QtWidgets.QApplication = None
