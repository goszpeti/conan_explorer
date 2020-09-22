""" Contains the class for a clickable Qt label"""

from PyQt5 import QtCore, QtWidgets, QtGui
Qt = QtCore.Qt
from pathlib import Path
from conan_app_launcher.config import ICON_SIZE

class ClickableLabel(QtWidgets.QLabel, QtWidgets.QPushButton):
    """ Qt label, which can react on a mouse click """
    # overrides base QT behaviour. Needs to be a class variable.
    def __init__(self, parent, image:Path=None, flags=QtCore.Qt.WindowFlags()):
        QtWidgets.QLabel.__init__(self, parent=parent, flags=flags)
        QtWidgets.QPushButton.__init__(self, parent=parent)
        self._image = image
        self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))

    def mousePressEvent(self, event):  # pylint: disable=unused-argument, invalid-name
        """ Callback to emitting the clicked signal, so "clicked" can be used to connect any function. """
        super().mousePressEvent(event)

        # px = self._px #.scaled(62, 62) #, transformMode=Qt.traSmoothTransformation)
        # #pixmap = QtGui.QPixmap(self._px.size())
        # #QGraphicsPixmapItem* item(scene->addPixmap(*pix)); // Save the returned item
        # painter = QtGui.QPainter(px)
        # so = QtGui.QPainter().CompositionMode_DestinationOver
        # painter.setCompositionMode(so)
        # painter.fillRect(0,0,64,64, Qt.darkBlue)
        # #paint.drawRect()
        # #self.paint(painter, None, None)
        # painter.end()
        smaller_size = ICON_SIZE-(ICON_SIZE/32)
        self.setPixmap(self.pixmap().scaled(smaller_size, smaller_size, transformMode=Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))


