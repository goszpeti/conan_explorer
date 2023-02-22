import platform
from pathlib import Path

import conan_app_launcher.app as app
from conan_app_launcher import base_path
from conan_app_launcher.core.system import is_windows_11
from conan_app_launcher.settings import FONT_SIZE, GUI_MODE, GUI_MODE_LIGHT, GUI_MODE_DARK, GUI_STYLE, GUI_STYLE_FLUENT, GUI_STYLE_MATERIAL
from conan_app_launcher.app.logger import Logger

from jinja2 import Template
from PySide6.QtWidgets import QApplication


def configure_theme(qss_template_path: Path, font_size_pt: int, user_color: str, window_border_radius: int) -> str:
    """ Configure the given qss file with the set options and return it as a string """

    qss_template = None
    with open(qss_template_path, "r") as fd:
        qss_template = Template(fd.read())
    qss_content = qss_template.render(MAIN_FONT_SIZE=font_size_pt, USER_COLOR=user_color,
                                      WINDOW_BORDER_RADIUS=window_border_radius)
    return qss_content


def get_gui_dark_mode() -> bool:
    gui_mode = app.active_settings.get_string(GUI_MODE).lower()
    if gui_mode not in [GUI_MODE_DARK, GUI_MODE_LIGHT]:
        Logger().warning("Theming: Can't read GUI mode, setting it to light.")
        return False
    return True if gui_mode == GUI_MODE_DARK else False


def get_gui_style():
    gui_style = app.active_settings.get_string(GUI_STYLE).lower()
    if gui_style not in [GUI_STYLE_FLUENT, GUI_STYLE_MATERIAL]:
        Logger().warning("Theming: Can't read GUI style, setting it to material.")
        app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)
        return GUI_STYLE_MATERIAL
    return gui_style

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
        except:
            Logger().warning("Theming: Can't read user accent color, setting it to black.")
            return "#000000"
        try:
            abgr_color = hex(int(value))
            if len(abgr_color) < 9:  # wrong format, return default
                return "#000000"
            # convert abgr to rgb
            rgb_color = abgr_color[-2:] + abgr_color[-4:-2] + abgr_color[-6:-4]
        except:
            Logger().warning("Theming: Can't convert read user accent color, setting it to black.")
            return "#000000"
        return "#" + rgb_color
    return "#000000"
