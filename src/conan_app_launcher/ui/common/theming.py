from pathlib import Path

import conan_app_launcher.app as app
from conan_app_launcher import base_path
from conan_app_launcher.settings import FONT_SIZE, GUI_STYLE, GUI_STYLE_DARK
from jinja2 import Template
from PyQt5 import QtWidgets


def configure_theme(qss_template_path: Path, font_size_pt: int) -> str:
    """ Configure the given qss file with the set options and return it as a string """

    qss_template = None
    with open(qss_template_path, "r") as fd:
        qss_template = Template(fd.read())
    qss_content = qss_template.render(MAIN_FONT_SIZE=font_size_pt)
    return qss_content


def activate_theme(qt_app: QtWidgets.QApplication):
    """ Apply the theme from the current settings and apply all related view options """

    style_file = "light_style.qss.in"
    if app.active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
        style_file = "dark_style.qss.in"

    style_sheet = configure_theme(base_path / "ui" / style_file, app.active_settings.get_int(FONT_SIZE))

    qt_app.setStyleSheet(style_sheet)
