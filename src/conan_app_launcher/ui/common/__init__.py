""" Common ui classes, and functions """

from pathlib import Path
import conan_app_launcher.app as app
from conan_app_launcher.conan_wrapper.types import ConanRef
from conan_app_launcher.app.system import execute_cmd, open_file  # using global module pattern
from conan_app_launcher.settings import FILE_EDITOR_EXECUTABLE, FONT_SIZE
from PySide6.QtGui import QFontMetrics, QFont

from .icon import extract_icon, get_icon_from_image_file, get_inverted_asset_image, get_platform_icon
from .logger import init_qt_logger, remove_qt_logger
from .model import TreeModel, TreeModelItem, FileSystemModel
from .theming import activate_theme, configure_theme, get_user_theme_color, CanSetIconWidgetProtocol, CanSetPixmapWidgetProtocol, ThemedWidget, get_themed_asset_icon, get_asset_image_path, get_gui_dark_mode, get_gui_style


def measure_font_width(text: str) -> int:
    """ Return the width of a text in pixels woth the current font and default fontsize """
    fs = app.active_settings.get_int(FONT_SIZE)
    font = QFont()
    font.setPointSize(fs)
    fm = QFontMetrics(font)
    return fm.horizontalAdvance(text)


def show_conanfile(conan_ref: str):
    conanfile = app.conan_api.get_conanfile_path(ConanRef.loads(conan_ref))
    editor = app.active_settings.get_string(FILE_EDITOR_EXECUTABLE)
    if not editor or not Path(editor).exists():
        open_file(conanfile)
        return  
    execute_cmd([editor, str(conanfile)], False)
