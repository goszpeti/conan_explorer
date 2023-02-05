""" Common ui classes, and functions """

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.settings import FONT_SIZE
from PySide6.QtGui import QFontMetrics, QFont

from .icon import extract_icon, get_icon_from_image_file, get_inverted_asset_image, get_platform_icon, get_themed_asset_icon, get_asset_image_path
from .loading import AsyncLoader
from .logger import init_qt_logger, remove_qt_logger
from .model import TreeModel, TreeModelItem, FileSystemModel
from .theming import activate_theme, configure_theme, get_user_theme_color


def measure_font_width(text: str) -> int:
    """ Return the width of a text in pixels woth the current font and default fontsize """
    fs = app.active_settings.get_int(FONT_SIZE)
    font = QFont()
    font.setPointSize(fs)
    fm = QFontMetrics(font)
    return fm.horizontalAdvance(text)
