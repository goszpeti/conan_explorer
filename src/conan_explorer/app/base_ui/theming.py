from pathlib import Path

from jinja2 import Template
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication

import conan_explorer.app as app
from conan_explorer import base_path
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import is_windows_11
from conan_explorer.settings import FONT_SIZE, GUI_MODE, GUI_MODE_DARK, GUI_MODE_LIGHT


def activate_theme(qt_app: QApplication):
    """Apply the theme from the current settings and apply all related view options"""
    dark_mode = get_gui_dark_mode()
    style_file = "light_style.qss.in"
    if dark_mode:
        style_file = "dark_style.qss.in"
    try:
        # since Qt 6.6
        user_color = QPalette().accent().color().name()
    except Exception:
        user_color = "#000000"
    window_border_radius = 0

    # enable rounded corners under Win 11
    if is_windows_11():
        window_border_radius = 7

    # apply palette for correct icon theme detection under new windows platform plugin
    if dark_mode:
        qt_app.setPalette(QPalette(QColor("#000000")))
    else:
        qt_app.setPalette(QPalette(QColor("#FFFFFF")))

    style_sheet = configure_theme(
        base_path / "ui" / style_file,
        app.active_settings.get_int(FONT_SIZE),
        user_color,
        window_border_radius,
    )

    qt_app.setStyleSheet(style_sheet)


def configure_theme(
    qss_template_path: Path, font_size_pt: int, user_color: str, window_border_radius: int
) -> str:
    """Configure the given qss file with the set options and return it as a string"""

    qss_template = None
    register_font("Noto Sans Mono", "NotoSansMono.ttf")
    register_font("Noto Sans", "NotoSans-Regular.ttf")
    with open(qss_template_path, "r") as fd:
        qss_template = Template(fd.read())
    qss_content = qss_template.render(
        MAIN_FONT_SIZE=font_size_pt,
        USER_COLOR=user_color,
        WINDOW_BORDER_RADIUS=window_border_radius,
        CONSOLE_FONT_FAMILY="Noto Sans Mono",
        FONT_FAMILY="Noto Sans",
    )
    return qss_content


def get_gui_dark_mode() -> bool:
    gui_mode = app.active_settings.get_string(GUI_MODE).lower()
    if gui_mode not in [GUI_MODE_DARK, GUI_MODE_LIGHT]:
        Logger().warning("Theming: Can't read GUI mode, setting it to light.")
        return False
    return True if gui_mode == GUI_MODE_DARK else False


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
            font = font_db.font(font_families[0], font_styles[0], 11)
            font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
            font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
            # this applies the changes on the font!
            qapp.setFont(font)  # type: ignore
        else:
            Logger().warning("Can't register selected font file.")
    return font
