""" Contains the class for a clickable Qt label"""

from pathlib import Path

from conan_app_launcher import ICON_SIZE
from PyQt5 import QtCore, QtGui, QtWidgets
from . import app_edit

Qt = QtCore.Qt


class AppButton(QtWidgets.QLabel, QtWidgets.QPushButton):

    """ Qt label, which can react on a mouse click """
    # this signal is used to connect to backend functions.
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent, image: Path = None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent)
        self.setWindowFlags(flags)
        self._image = image
        self._greyed_out = True  # Must be ungreyed, when available
        self.set_icon(image)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        quitAction = QtWidgets.QAction("Edit", self)
        quitAction.triggered.connect(self.disp_edit_dialog)
        self.addAction(quitAction)

    def disp_edit_dialog(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setModal(True)
        edit = app_edit.Ui_Dialog()
        edit.setupUi(self.dialog)
        self.dialog.show()

    def ungrey_icon(self):
        self._greyed_out = False
        self.set_icon(self._image)

    def grey_icon(self):
        self._greyed_out = True
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

    # def contextMenuEvent(self, event):  # override QPushButton
    #     menu = QtWidgets.QMenu(self)
    #     quitAction = menu.addAction("Quit")
    #     action = menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == quitAction:
    #         print("Quit")

    def mousePressEvent(self, event):  # override QPushButton
        """ Callback to emitting the clicked signal, so "clicked" can be used to connect any function. """
        super().mousePressEvent(event)
        # make the button a little bit smaller to emulate a "clicked" effect - only if ungreyed:
        if not self._greyed_out:
            smaller_size = int(ICON_SIZE-(ICON_SIZE/32))
            self.setPixmap(self.pixmap().scaled(smaller_size, smaller_size,
                                                transformMode=Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):  # override QPushButton
        """ reset size of icon form mousePressEvent """
        super().mouseReleaseEvent(event)
        # need to use the original image here, otherwise the quality degrades over multiple clicks
        if not self._greyed_out:
            self.setPixmap(QtGui.QPixmap(str(self._image)).scaled(
                ICON_SIZE, ICON_SIZE, transformMode=Qt.SmoothTransformation))
        # emit the click signal now, so the click effect plays before
        self.clicked.emit()
