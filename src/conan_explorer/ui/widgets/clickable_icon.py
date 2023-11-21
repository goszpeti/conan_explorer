""" Contains the class for a clickable Qt label"""

from pathlib import Path
from typing import Optional

from conan_explorer import ICON_SIZE, INVALID_PATH

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QGraphicsColorizeEffect, QGraphicsPixmapItem
from PySide6.QtGui import QColor, QIcon, QPixmap


class ClickableIcon(QPushButton):
    """
    Qt QPushButton with greyable icon, which can react on a mouse click.
    Has advanced icon handling for displaying the best matching icon.
    """

    # TODO flags
    def __init__(self, parent, image=Path(INVALID_PATH), icon_size=ICON_SIZE):
        super().__init__(parent=parent)

        self._greyed_out = True  # Must be ungreyed, when available
        self._grey_effect = QGraphicsColorizeEffect()
        self._grey_effect.setColor(QColor(128, 128, 128, 128))
        self.setGraphicsEffect(self._grey_effect)

        self.set_icon_from_file(image)
        self.setFlat(True)
        self.setIconSize(QSize(icon_size, icon_size))
        self.grey_icon()

    def ungrey_icon(self):
        self._greyed_out = False
        self._grey_effect.setEnabled(False)

    def grey_icon(self):
        self._greyed_out = True
        self._grey_effect.setEnabled(True)

    def set_icon(self, icon: QIcon):
        # convert biggest image to QPixmap and scale
        sizes = icon.availableSizes()
        if len(sizes) > 0:
            icon_pixmap = icon.pixmap(sizes[-1])
            # embedded icons sometimes not scale up correctly, but only increase the canvas behind the icon,
            #  which looks like crap. With opaqueArea.boundingRect we can query the size of
            #  the non-opaque area - the real image
            pixmap = QGraphicsPixmapItem(icon_pixmap)
            image_rect = pixmap.opaqueArea().boundingRect()
            top_left = image_rect.topLeft()
            # copy the smaller image (crop) - start from 0, this adds some margin
            icon_pixmap = icon_pixmap.copy(0, 0, int(image_rect.width() + top_left.x()),
                                           int(image_rect.height() + top_left.y()))
            self._ic = QIcon(icon_pixmap)
        else:
            self._ic = icon
        self.setIcon(self._ic)

    def set_icon_from_file(self, image: Optional[Path]):
        if not image or not image.exists():
            return
        # Logger().debug("Setting icon to " + str(image))
        self._image = image
        if self._image.suffix == ".ico":
            self._ic = QIcon(str(self._image))
            self.setIcon(self._ic)
        else:
            pixmap = QPixmap(str(self._image)).toImage()
            icon = QPixmap.fromImage(pixmap).scaled(
                ICON_SIZE, ICON_SIZE, mode=Qt.TransformationMode.SmoothTransformation)
            self._ic = QIcon(icon)
            self.setIcon(self._ic)
