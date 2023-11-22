""" Common ui classes, and functions """

from pathlib import Path
import conan_explorer.app as app
from conan_explorer.conan_wrapper.types import ConanRef
# using global module pattern
from conan_explorer.app.system import execute_cmd, open_file
from conan_explorer.settings import FILE_EDITOR_EXECUTABLE, FONT_SIZE
from PySide6.QtGui import QFontMetrics, QFont

from .icon import extract_icon, get_icon_from_image_file, get_inverted_asset_image, get_platform_icon, draw_svg_with_color
from .logger import init_qt_logger, remove_qt_logger
from .model import TreeModel, TreeModelItem, FileSystemModel, re_register_signal
from .theming import (get_user_theme_color, get_themed_asset_icon, get_asset_image_path, 
                      get_gui_dark_mode, get_gui_style,
                      CanSetIconWidgetProtocol, CanSetPixmapWidgetProtocol, ThemedWidget)
from .syntax_highlighting import ConfigHighlighter


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
