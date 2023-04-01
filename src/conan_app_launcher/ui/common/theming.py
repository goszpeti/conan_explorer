import platform
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union

import conan_app_launcher.app as app
from conan_app_launcher import base_path
from conan_app_launcher.app.system import is_windows_11
from conan_app_launcher.settings import FONT_SIZE, GUI_MODE, GUI_MODE_LIGHT, GUI_MODE_DARK, GUI_STYLE, GUI_STYLE_FLUENT, GUI_STYLE_MATERIAL
from conan_app_launcher.app.logger import Logger

from jinja2 import Template
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QIcon, QPixmap, QImage, QFont, QFontDatabase
from PySide6.QtCore import QSize

from conan_app_launcher.ui.common.icon import draw_svg_with_color, get_icon_from_image_file, get_inverted_asset_image


if TYPE_CHECKING:
    from typing import TypedDict, Protocol, runtime_checkable
else:
    try:
        from typing_extensions import Protocol, TypedDict, runtime_checkable
    except ImportError:
        from typing import Protocol, TypedDict, runtime_checkable

@runtime_checkable
class CanSetIconWidgetProtocol(Protocol):
    def setIcon(self, icon: Union[QIcon, QPixmap]) -> None: ...


@runtime_checkable
class CanSetPixmapWidgetProtocol(Protocol):
    def setPixmap(self, arg__1: Union[QPixmap, QImage, str]) -> None: ...


def get_asset_image_path(image_path: str) -> Path:
    asset_path = Path(image_path)
    if asset_path.exists():  # absolute path - return immediately
        return asset_path

    asset_path = app.asset_path / image_path
    if not asset_path.exists():  # try in style
        asset_path = asset_path.parent / get_gui_style() / asset_path.name

    if not asset_path.exists():
        Logger().warning(f"Can't find image: {str(asset_path)}")
    return asset_path


def get_themed_asset_icon(image_path: str, force_light_mode=False, force_dark_mode=False) -> QIcon:
    asset_path = get_asset_image_path(image_path)
    if force_dark_mode or (get_gui_dark_mode() and not force_light_mode):
        if asset_path.suffix == ".svg":
            asset_path = draw_svg_with_color(asset_path)
        else:
            asset_path = get_inverted_asset_image(asset_path)
    return get_icon_from_image_file(asset_path)

class ThemedWidget(QWidget):
    class IconInfo(TypedDict):
        asset_path: str
        size: Optional[Tuple[int, int]]

    def __init__(self, parent=None) -> None:
        if parent is not None:  # signals, it is already a widget
            super().__init__(parent)
        self._icon_map: Dict[Union[CanSetIconWidgetProtocol, CanSetPixmapWidgetProtocol],
                             ThemedWidget.IconInfo] = {}  # widget: {name, size} for re-theming

    def set_themed_icon(self, widget: Union[CanSetIconWidgetProtocol, CanSetPixmapWidgetProtocol],
                        asset_path: str, size: Optional[Tuple[int, int]] = None,
                        force_dark_mode=False, force_light_mode=False):
        """ 
        Applies an icon to a widget and inverts it, when theming is toggled to dark mode.
        For that reload_themed_icons must be called.
        Size only applies for pixmaps.
        """
        icon = get_themed_asset_icon(asset_path, force_light_mode, force_dark_mode)
        if isinstance(widget, CanSetIconWidgetProtocol):
            widget.setIcon(icon)
        elif isinstance(widget, CanSetPixmapWidgetProtocol):
            if size is None:
                size = (20, 20)
            widget.setPixmap(icon.pixmap(*size))
        self._icon_map[widget] = {"asset_path": asset_path, "size": size}

    def reload_themed_icons(self):
        for widget, info in self._icon_map.items():
            asset_rel_path = info["asset_path"]
            size = info["size"]
            icon = get_themed_asset_icon(asset_rel_path)
            if isinstance(widget, CanSetIconWidgetProtocol):
                widget.setIcon(icon)
            elif isinstance(widget, CanSetPixmapWidgetProtocol):
                widget.setPixmap(icon.pixmap(QSize(*size)))


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


def register_font(font_style_name: str, font_file_name: str) -> QFont:
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
