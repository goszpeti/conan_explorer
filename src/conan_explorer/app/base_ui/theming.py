import platform
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union

import conan_explorer.app as app
from conan_explorer import base_path
from conan_explorer.app.system import is_windows_11
from conan_explorer.settings import FONT_SIZE, GUI_MODE, GUI_MODE_LIGHT, GUI_MODE_DARK
from conan_explorer.app.logger import Logger

from jinja2 import Template
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase

if TYPE_CHECKING:
    from typing import TypedDict, Protocol, runtime_checkable
else:
    try:
        from typing_extensions import Protocol, TypedDict, runtime_checkable
    except ImportError:
        from typing import Protocol, TypedDict, runtime_checkable


def activate_theme(qt_app: QApplication):
    """ Apply the theme from the current settings and apply all related view options """
    dark_mode = get_gui_dark_mode()
    style_file = "light_style.qss.in"
    if dark_mode:
        style_file = "dark_style.qss.in"
    user_color = get_user_theme_color()
    window_border_radius = 0

    # enable rounded corners under Win 11
    if is_windows_11():
        window_border_radius = 7

    style_sheet = configure_theme(base_path / "ui" / style_file,
            app.active_settings.get_int(FONT_SIZE), user_color, window_border_radius)

    qt_app.setStyleSheet(style_sheet)


def configure_theme(qss_template_path: Path, font_size_pt: int, user_color: str, window_border_radius: int) -> str:
    """ Configure the given qss file with the set options and return it as a string """

    qss_template = None
    register_font("Noto Sans Mono", "NotoSansMono.ttf")
    register_font("Noto Sans", "NotoSans-Regular.ttf")
    with open(qss_template_path, "r") as fd:
        qss_template = Template(fd.read())
    qss_content = qss_template.render(MAIN_FONT_SIZE=font_size_pt, USER_COLOR=user_color,
                                      WINDOW_BORDER_RADIUS=window_border_radius, CONSOLE_FONT_FAMILY="Noto Sans Mono",  FONT_FAMILY="Noto Sans")
    return qss_content


def get_gui_dark_mode() -> bool:
    gui_mode = app.active_settings.get_string(GUI_MODE).lower()
    if gui_mode not in [GUI_MODE_DARK, GUI_MODE_LIGHT]:
        Logger().warning("Theming: Can't read GUI mode, setting it to light.")
        return False
    return True if gui_mode == GUI_MODE_DARK else False

def get_user_theme_color() -> str:  # RGB
    """ Returns black per default """
    if platform.system() == "Windows":
        # get theme color
        from winreg import (HKEY_CURRENT_USER, ConnectRegistry, OpenKey,
                            QueryValueEx)
        try:
            reg = ConnectRegistry(None, HKEY_CURRENT_USER)
            key = OpenKey(reg, r"SOFTWARE\Microsoft\Windows\DWM")
            value = QueryValueEx(key, "AccentColor")[0]  # Windows Theme Hilight color for border color in rgb
        except Exception:
            Logger().warning("Theming: Can't read user accent color, setting it to black.")
            return "#000000"
        try:
            abgr_color = hex(int(value))
            if len(abgr_color) < 9:  # wrong format, return default
                return "#000000"
            # convert abgr to rgb
            rgb_color = abgr_color[-2:] + abgr_color[-4:-2] + abgr_color[-6:-4]
        except Exception:
            Logger().warning("Theming: Can't convert read user accent color, setting it to black.")
            return "#000000"
        return "#" + rgb_color
    return "#000000"


def register_font(font_style_name: str, font_file_name: str) -> "QFont":
    # set up font
    font_file = app.asset_path / "font" / font_file_name
    font_id = QFontDatabase.addApplicationFont(str(font_file))
    qapp = QApplication.instance()
    if qapp is None:
        return QFont()
    font = qapp.font()  # type: ignore
    if font_id != -1:
        font_db = QFontDatabase()
        font_styles = font_db.styles(font_style_name)
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font = font_db.font(font_families[0], font_styles[0], 13)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        else:
            Logger().warning("Can't register selected font file.")
    return font
