import platform
import re
from pathlib import Path
from typing import Tuple
from distutils import version

import conan_app_launcher.app as app
from conan_app_launcher import base_path
from conan_app_launcher.settings import FONT_SIZE, GUI_STYLE, GUI_STYLE_DARK

from jinja2 import Template
from PyQt5.QtWidgets import QApplication


def configure_theme(qss_template_path: Path, font_size_pt: int, user_color: str, window_border_radius: int) -> str:
    """ Configure the given qss file with the set options and return it as a string """

    qss_template = None
    with open(qss_template_path, "r") as fd:
        qss_template = Template(fd.read())
    qss_content = qss_template.render(MAIN_FONT_SIZE=font_size_pt, USER_COLOR=user_color,
                                      WINDOW_BORDER_RADIUS=window_border_radius)
    return qss_content


def activate_theme(qt_app: QApplication):
    """ Apply the theme from the current settings and apply all related view options """

    style_file = "light_style.qss.in"
    if app.active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
        style_file = "dark_style.qss.in"
    user_color = get_user_theme_color()
    window_border_radius = 0

    # enable rounded corners under Win 11 (main version number is still 10 - thanks MS!)
    if platform.system() == "Windows" and version.StrictVersion(platform.version()) >= version.StrictVersion("10.0.22000"):
        window_border_radius = 7

    user_color_str = f"rgb({user_color[0]},{user_color[1]},{user_color[2]})"
    style_sheet = configure_theme(base_path / "ui" / style_file,
                                  app.active_settings.get_int(FONT_SIZE), user_color_str, window_border_radius)

    qt_app.setStyleSheet(style_sheet)


def set_style_sheet_option(style_sheet: str, option: str, value: str, object: str="") -> str:
    """ Helper for QSS related functions """
    # empty string key is the one associated to the current object
    qss = {}
    # parse to the next "{"
    obj_split_sheet = style_sheet.split("{")
    current_object = ""
    for section in obj_split_sheet:
        next_objectname = ""
        subsections = section.split("}")
        if len(subsections) > 1:
            # last line before } is next object name
            next_objectname = subsections[-1].splitlines()[-1].strip()
        entries = "".join(subsections).strip().split(";")
        for entry in entries:
            # filter // and /* */ comments
            clean_lines = re.sub("\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$", "", entry).strip().splitlines()
            if not clean_lines or next_objectname == clean_lines[0]:
                continue
            style = clean_lines[0].split(":", 1)
            if len(style) < 2:
                # TODO log warning?
                print("WARNING")
                continue
            if not current_object in qss:
                qss[current_object] = {}
            qss[current_object][style[0]] = style[1]
        current_object = next_objectname
    # set value
    qss.get(object, {})[option] = value
    # convert back to qss
    new_style_sheet = ""
    for object_name, entries in qss.items():
        if object_name:
            new_style_sheet += object_name + " {"
        for qss_opt, value in entries.items():
            new_style_sheet += f"{qss_opt}:{value};"
        if object_name:
            new_style_sheet += "}"
    return new_style_sheet


def get_user_theme_color() -> Tuple[int,int,int]: # RGB
    """ Returns black per default """
    if platform.system() == "Windows":
        # get theme color
        from winreg import (HKEY_CURRENT_USER, ConnectRegistry, OpenKey,
                            QueryValueEx)
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(reg, r"Control Panel\Colors")
        value = QueryValueEx(key, "Hilight")[0]  # Windows Theme Hilight color for border color in rgb
        return tuple(value.split(" ")[0:3])
    return 0,0,0
