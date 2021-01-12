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

        self.installEventFilter(self)
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

    def eventFilter(self, source, event):  # pylint: disable=invalid-name
        """ Right click context menu for disabled button """
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # works currently with overriding the motion sensor
            if event.button() == Qt.RightButton:
                self.menu.exec_(event.globalPos())
        return super().eventFilter(source, event)
