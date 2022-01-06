from pathlib import Path

from conan_app_launcher import ICON_SIZE, asset_path
from conan_app_launcher.logger import Logger
from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFileIconProvider


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


def get_platform_icon(profile_name) -> QIcon:
    icons_path = asset_path / "icons"
    profile_name = profile_name.lower()
    if "windows" in profile_name:
        return QIcon(str(icons_path / "windows.png"))
    elif "linux" in profile_name:
        return QIcon(str(icons_path / "linux.png"))
    elif "android" in profile_name:
        return QIcon(str(icons_path / "android.png"))
    elif "macos" in profile_name:
        return QIcon(str(icons_path / "mac_os.png"))
    else:
        return QIcon(str(icons_path / "default_pkg.png"))
