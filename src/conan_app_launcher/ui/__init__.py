import os
from pathlib import Path

from conan_app_launcher.app.logger import Logger

# compile uic files, if needed
from conan_app_launcher import DEBUG_LEVEL
if DEBUG_LEVEL > 0:
    current_dir = Path(__file__).parent
    for ui_file in current_dir.glob("**/*.ui"):
        py_ui_file = Path("NULL")
        try:
            py_ui_file = ui_file.parent / (ui_file.stem + "_ui.py")
            if py_ui_file.exists() and py_ui_file.stat().st_mtime > ui_file.stat().st_mtime:
                continue
            Logger().debug("Converting " + str(py_ui_file))
            os.system(f"pyuic5 -o {str(py_ui_file)} {str(ui_file)}")
        except Exception as e:
            Logger().warning(f"Can't convert {str(py_ui_file)}: {str(e)}")
