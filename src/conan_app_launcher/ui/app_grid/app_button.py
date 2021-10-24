""" Contains the class for a clickable Qt label"""

from pathlib import Path
from typing import Optional

from conan_app_launcher import ICON_SIZE
from conan_app_launcher.base import Logger
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
        self.set_icon(image)
        self.setFlat(True)
        self.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.grey_icon()
        self.setWindowFlags(flags)

    def ungrey_icon(self):
        self._greyed_out = False
        self.setDisabled(False)

    def grey_icon(self):
        self._greyed_out = True  # TODO solve this
        # self.setDisabled(True)

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

    def mousePressEvent(self, event):  # override QPushButton
        """ Callback to emitting the clicked signal, so "clicked" can be used to connect any function. """
        super().mousePressEvent(event)
        # make the button a little bit smaller to emulate a "clicked" effect - only if ungreyed:
        # if not self._greyed_out and event.button() == Qt.RightButton:
        #    smaller_size = int(ICON_SIZE-(ICON_SIZE/32))
        #    self.setPixmap(self.pixmap().scaled(smaller_size, smaller_size,
        #                                        transformMode=Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):  # override QPushButton
        """ reset size of icon form mousePressEvent """
        super().mouseReleaseEvent(event)
        # need to use the original image here, otherwise the quality degrades over multiple clicks
        # if not self._greyed_out:
        #    self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(
        #        ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))

        # if event.button() == Qt.RightButton:
        #    self.menu.exec_(event.globalPos())
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        return super().mouseReleaseEvent(event)
