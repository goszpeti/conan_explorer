from pathlib import Path

import xml.dom.minidom as dom
from conan_app_launcher import ICON_SIZE
from conan_app_launcher.app.logger import Logger
from PySide6.QtCore import QFileInfo, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage, QPicture, QPainter
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtSvg import QSvgRenderer

import conan_app_launcher.app as app
from conan_app_launcher.settings import GUI_STYLE, GUI_STYLE_DARK  # using global module pattern


def get_asset_image_path(image_path: str) -> Path:
    asset_path = Path("NULL")
    if (app.asset_path / image_path).exists():  # relative path
        asset_path = app.asset_path / image_path
    else:  # absolute path
        asset_path = Path(image_path)
        if not asset_path.exists():
            Logger().warning(f"Can't find image: {str(asset_path)}")
    return asset_path

def get_themed_asset_icon(image_path: str) -> QIcon:
    asset_path = get_asset_image_path(image_path)
    if app.active_settings.get_string(GUI_STYLE).lower() == GUI_STYLE_DARK:
        if asset_path.suffix == ".svg":
            asset_path = draw_svg_with_color(asset_path)
        else:
            asset_path = get_inverted_asset_image(asset_path)
    return get_icon_from_image_file(asset_path)


def get_inverted_asset_image(image_path: Path) -> Path:
    """ Inverts a given image and saves it beside the original one with _inv in the name.
    To be used for icons to switch between light and dark mode themes. """
    inverted_img_path = image_path.parent / ((image_path.with_suffix('').name + "_inv") + image_path.suffix)

    if not inverted_img_path.exists():
        img = QImage(str(image_path))
        img.invertPixels()
        img.save(str(inverted_img_path))
    return inverted_img_path


def get_icon_from_image_file(image_path: Path) -> QIcon:
    if image_path.suffix == ".ico":
        return QIcon(str(image_path))
    else:
        image = QPixmap(str(image_path)).toImage()
        pixmap = QPixmap.fromImage(image).scaled(
            ICON_SIZE, ICON_SIZE, mode=Qt.TransformationMode.SmoothTransformation)
        return QIcon(pixmap)


def draw_svg_with_color(svg_path: Path, color="white", scale: float = 1.0) -> Path:
    """
    Sets an svg in the desired color for a QtWidget.
    :param color: the disired color as a string in html compatible name
    :param shadow: draws a drop shadow
    :param scale: multiplicator for scaling the image
    """
    if not svg_path or not svg_path.exists():
        Logger().error("Cannot draw invalid SVG file: %s", repr(svg_path))
        return Path("NULL")

    # read svg as xml and get the drawing
    with open(svg_path) as svg:
        svg_content = "".join(svg.readlines())
        svg_content = svg_content.replace("\t", "")
    svg_dom = dom.parseString("".join(svg_content))
    svg_drawing = svg_dom.getElementsByTagName("path")

    # set color in the dom element
    svg_drawing[0].setAttribute("fill", color)

    # create temporary svg and read into pyqt svg graphics object
    new_svg_path = svg_path.parent /  Path(svg_path.stem + "_" + color + svg_path.suffix)
    with open(new_svg_path, "w+") as new_svg:
        new_svg.write(svg_dom.toxml())
    return new_svg_path



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
    if "win" in profile_name:  # I hope people have no random win"s" in their profilename
        return QIcon(get_themed_asset_icon("icons/windows.png"))
    elif "linux" in profile_name:
        return QIcon(get_themed_asset_icon("icons/linux.png"))
    elif "android" in profile_name:
        return QIcon(get_themed_asset_icon("icons/android.png"))
    elif "macos" in profile_name:
        return QIcon(get_themed_asset_icon("icons/mac_os.png"))
    else:
        return QIcon(get_themed_asset_icon("icons/default_pkg.png"))
