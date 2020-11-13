""" Contains the class for a clickable Qt label"""

from conan_app_launcher import ICON_SIZE
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt


class AppButton(QtWidgets.QLabel, QtWidgets.QPushButton):
    # this signal is used to connect to backend functions.
    clicked = QtCore.pyqtSignal()
    # It needs to be a class variable (limitation of Qt)

    """ Qt label, which can react on a mouse click """
    # overrides base QT behaviour. Needs to be a class variable.

    def __init__(self, parent, image: Path = None, flags=QtCore.Qt.WindowFlags()):
        QtWidgets.QLabel.__init__(self, parent=parent, flags=flags)
        QtWidgets.QPushButton.__init__(self, parent=parent)
        self._image = image
        self._greyed_out = True  # Must be ungreyed, when available
        self.set_icon(image)

    def ungrey_icon(self):
        self._greyed_out = False
        self.set_icon(self._image)

    def set_icon(self, image):
        self._image = image
        if self._image.suffix == ".ico":
            icon = QtGui.QIcon(str(self._image))
            resized_pixmap = icon.pixmap(icon.actualSize(QtCore.QSize(512, 512)))
            image = resized_pixmap.toImage()
            if self._greyed_out:
                image = image.convertToFormat(QtGui.QImage.Format_Grayscale8)
            self.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            image = QtGui.QPixmap(str(self._image)).toImage()
            if self._greyed_out:
                image = image.convertToFormat(QtGui.QImage.Format_Grayscale8)
            self.setPixmap(QtGui.QPixmap.fromImage(image).scaled(
                ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))

    def mousePressEvent(self, event):  # pylint: disable=unused-argument, invalid-name
        """ Callback to emitting the clicked signal, so "clicked" can be used to connect any function. """
        super().mousePressEvent(event)
        # make the button a little bit smaller to emulate a "clicked" effect - only if ungreyed:
        if not self._greyed_out:
            smaller_size = int(ICON_SIZE-(ICON_SIZE/32))
            self.setPixmap(self.pixmap().scaled(smaller_size, smaller_size,
                                                transformMode=Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):
        """ reset size of icon form mousePressEvent """
        super().mouseReleaseEvent(event)
        # need to use the original image here, otherwise the quality degrades over multiple clicks
        if not self._greyed_out:
            self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(
                ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))
        # emit the click signal now, so the click effect plays before
        # TODO: emit or not emit?
        self.clicked.emit()
