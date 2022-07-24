from pathlib import Path

from conan_app_launcher import ICON_SIZE
from conan_app_launcher.app.logger import Logger
from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QFileIconProvider

import conan_app_launcher.app as app
from conan_app_launcher.settings import GUI_STYLE, GUI_STYLE_DARK  # using global module pattern


def get_themed_asset_image(image_rel_path: str) -> str:
    if app.active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
        return get_inverted_asset_image(app.asset_path / image_rel_path)
    return str(app.asset_path / image_rel_path)


def get_inverted_asset_image(image_path: Path):
    """ Inverts a given image and saves it beside the original one with _inv in the name.
    To be used for icons to switch between light and dark mode themes. """
    inverted_img_path = image_path.parent / ((image_path.with_suffix('').name + "_inv") + image_path.suffix)

    if not inverted_img_path.exists():
        img = QImage(str(image_path))
        img.invertPixels()
        img.save(str(inverted_img_path))
    return str(inverted_img_path)


def get_icon_from_image_file(image_path: Path) -> QIcon:
    if image_path.suffix == ".ico":
        return QIcon(str(image_path))
    else:
        pixmap = QPixmap(str(image_path)).toImage()
        icon = QPixmap.fromImage(pixmap).scaled(
            ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation)
        return QIcon(icon)


def extract_icon(file_path: Path) -> QIcon:
    """
    Extract icons from a file and save them to specified dir.
    There must be a main qt application created, otherwise the call will crash!
    """

    if file_path.is_file():
        icon_provider = QFileIconProvider()
        file_info = QFileInfo(str(file_path))
        icon = icon_provider.icon(file_info)
        return icon
    else:
        Logger().debug(f"File {str(file_path)} for icon extraction does not exist.")
    return QIcon()


def get_platform_icon(profile_name: str) -> QIcon:
    """ Return an Icon based on the profile name.
    TODO: This would be better done with a settings object.
    """
    profile_name = profile_name.lower()
    if "win" in profile_name: # I hope people have no random win"s" in their profilename
        return QIcon(get_themed_asset_image("icons/windows.png"))
    elif "linux" in profile_name:
        return QIcon(get_themed_asset_image("icons/linux.png"))
    elif "android" in profile_name:
        return QIcon(get_themed_asset_image("icons/android.png"))
    elif "macos" in profile_name:
        return QIcon(get_themed_asset_image("icons/mac_os.png"))
    else:
        return QIcon(get_themed_asset_image("icons/default_pkg.png"))
