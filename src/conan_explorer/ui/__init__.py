from conan_explorer import DEBUG_LEVEL, INVALID_PATH
import os
from pathlib import Path

from .main_window import BaseSignals
from .fluent_window import FluentWindow
from .plugin import PluginInterfaceV1, PluginFile, PluginDescription


def compile_ui_file_if_newer(ui_file: Path):
    from conan_explorer.app.logger import Logger
    py_ui_file = ui_file.parent / (ui_file.stem + "_ui.py")
    if py_ui_file.exists() and py_ui_file.stat().st_mtime > ui_file.stat().st_mtime:
        return
    Logger().debug("Converting " + str(py_ui_file))
    os.system(f"pyside6-uic -o {str(py_ui_file)} {str(ui_file)}")


# compile uic files, if needed
if DEBUG_LEVEL > 0:
    current_dir = Path(__file__).parent
    for ui_file in current_dir.glob("**/*.ui"):
        py_ui_file = Path(INVALID_PATH)
        try:
            compile_ui_file_if_newer(ui_file)
        except Exception as e:
            from conan_explorer.app.logger import Logger
            Logger().warning(f"Can't convert {str(py_ui_file)}: {str(e)}")
