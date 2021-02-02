""" Contains the class for a clickable Qt label"""

from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from conan_app_launcher import ICON_SIZE
import conan_app_launcher as this


Qt = QtCore.Qt


class AppButton(QtWidgets.QPushButton):

    """ Qt label, which can react on a mouse click """
    # this signal is used to connect to backend functions.
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent, image: Path = None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent)
        icons_path = this.asset_path / "icons"

        self._image = image
        self._greyed_out = True  # Must be ungreyed, when available
        self.set_icon(image)
        self.setFlat(True)
        self.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.grey_icon()
        self.menu = QtWidgets.QMenu()

        self.add_action = QtWidgets.QAction("Add new app", self)
        self.add_action.setIcon(QtGui.QIcon(str(icons_path / "add_link.png")))
        self.menu.addAction(self.add_action)

        self.edit_action = QtWidgets.QAction("Edit", self)
        self.edit_action.setIcon(QtGui.QIcon(str(icons_path / "edit.png")))
        self.menu.addAction(self.edit_action)

        self.remove_action = QtWidgets.QAction("Remove", self)
        self.remove_action.setIcon(QtGui.QIcon(str(icons_path / "delete.png")))
        self.menu.addAction(self.remove_action)

        # self.installEventFilter(self)
        self.setWindowFlags(flags)

    def ungrey_icon(self):
        self._greyed_out = False
        self.setDisabled(False)

    def grey_icon(self):
        self._greyed_out = True
        self.setDisabled(True)

    def set_icon(self, image: Path):
        if not image or not image.exists():
            return
        self._image = image
        if self._image.suffix == ".ico":
            icon = QtGui.QIcon(str(self._image))
            resized_pixmap = icon.pixmap(icon.actualSize(QtCore.QSize(512, 512)))
            image = resized_pixmap.toImage()
            self.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            image = QtGui.QPixmap(str(self._image)).toImage()
            icon = QtGui.QPixmap.fromImage(image).scaled(
                ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation)
            self._ic = QtGui.QIcon(icon)
            self.setIcon(self._ic)

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        """ Right click context menu for disabled button """
        # if event.type() == QtCore.QEvent.MouseButtonPress:
        # works currently with overriding the motion sensor
        if event.button() == Qt.RightButton:
            self.menu.exec_(event.globalPos())
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        return super().mouseReleaseEvent(event)

    # def mousePressEvent(self, event):  # override QPushButton
    #     """ Callback to emitting the clicked signal, so "clicked" can be used to connect any function. """
    #     if event.button() == Qt.LeftButton:
    #         super().mousePressEvent(event)
    #         # make the button a little bit smaller to emulate a "clicked" effect - only if ungreyed:
    #         if not self._greyed_out:
    #             smaller_size = int(ICON_SIZE-(ICON_SIZE/32))
    #             self.setPixmap(self.pixmap().scaled(smaller_size, smaller_size,
    #                                                 transformMode=Qt.SmoothTransformation))

    # def mouseReleaseEvent(self, event):  # override QPushButton
    #     """ reset size of icon form mousePressEvent """
    #     if event.button() == Qt.LeftButton:
    #         super().mouseReleaseEvent(event)
    #         # need to use the original image here, otherwise the quality degrades over multiple clicks
    #         if not self._greyed_out:
    #             self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(
    #                 ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))
    #         # emit the click signal now, so the click effect plays before
    #         self.clicked.emit()
