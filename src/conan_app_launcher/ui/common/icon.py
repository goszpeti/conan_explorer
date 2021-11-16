from pathlib import Path

from conan_app_launcher import ICON_SIZE
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
        Logger().debug("File for icon extraction does not exist.")
    return QIcon()
