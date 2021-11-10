""" Contains the class for a clickable Qt label"""

from pathlib import Path
from typing import Optional

from conan_app_launcher import ICON_SIZE
from conan_app_launcher.logger import Logger
from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt


class AppButton(QtWidgets.QPushButton):

    """ Qt label, which can react on a mouse click """
    # this signal is used to connect to backend functions.
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent, image: Path = None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent)

        self._image = image
        self._greyed_out = True  # Must be ungreyed, when available
        self._grey_effect = QtWidgets.QGraphicsColorizeEffect()
        self._grey_effect.setColor(QtGui.QColor(128, 128, 128))
        self.setGraphicsEffect(self._grey_effect)

        self.set_icon(image)
        self.setFlat(True)
        self.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.grey_icon()
        self.setWindowFlags(flags)

    def ungrey_icon(self):
        self._greyed_out = False
        self._grey_effect.setEnabled(False)

    def grey_icon(self):
        self._greyed_out = True  # no context menu
        self._grey_effect.setEnabled(True)

    def set_icon(self, image: Optional[Path]):
        Logger().debug("Setting icon to " + str(image))
        if not image or not image.exists():
            return
        self._image = image
        if self._image.suffix == ".ico":
            icon = QtGui.QIcon(str(self._image))
            self.setIcon(icon)
        else:
            pixmap = QtGui.QPixmap(str(self._image)).toImage()
            icon = QtGui.QPixmap.fromImage(pixmap).scaled(
                ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation)
            self._ic = QtGui.QIcon(icon)
            self.setIcon(self._ic)

    def mouseReleaseEvent(self, event):  # override QPushButton
        """ reset size of icon form mousePressEvent """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        return super().mouseReleaseEvent(event)
