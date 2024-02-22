from pathlib import Path
from typing import (Dict, Optional, Protocol, Tuple, TypedDict, Union,
                    runtime_checkable)

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QWidget

import conan_explorer.app as app
 # reimport for usage in other files
from conan_explorer.app.base_ui.theming import get_gui_dark_mode, get_user_theme_color
from conan_explorer.app.logger import Logger
from conan_explorer.settings import (GUI_STYLE, GUI_STYLE_FLUENT,
                                     GUI_STYLE_MATERIAL)
from conan_explorer.ui.common import (draw_svg_with_color,
                                      get_icon_from_image_file,
                                      get_inverted_asset_image)


@runtime_checkable
class CanSetIconWidgetProtocol(Protocol):
    def setIcon(self, icon: Union[QIcon, QPixmap]) -> None: ...


@runtime_checkable
class CanSetPixmapWidgetProtocol(Protocol):
    def setPixmap(self, arg__1: Union[QPixmap, QImage, str]) -> None: ...


def get_gui_style():
    gui_style = app.active_settings.get_string(GUI_STYLE).lower()
    if gui_style not in [GUI_STYLE_FLUENT, GUI_STYLE_MATERIAL]:
        Logger().warning("Theming: Can't read GUI style, setting it to material.")
        app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)
        return GUI_STYLE_MATERIAL
    return gui_style

def get_asset_image_path(image_path: str) -> Path:
    asset_path = Path(image_path)
    if asset_path.exists():  # absolute path - return immediately
        return asset_path

    asset_path = app.asset_path / image_path
    if not asset_path.exists():  # try in style
        asset_path = asset_path.parent / get_gui_style() / asset_path.name

    if not asset_path.exists():
        Logger().warning(f"Can't find image: {str(asset_path)}")
        # set to an existing placeholder image to avoid crashes
        asset_path = app.asset_path / "icons/global/conan_logo.svg" 
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

