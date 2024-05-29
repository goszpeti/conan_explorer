from pathlib import Path
from PySide6.QtWidgets import QWidget, QDialog, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QCoreApplication


from conan_explorer.ui.common.theming import get_themed_asset_icon

from qtpy.QtGui import QGuiApplication
from qtpy.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSize, QMargins, QRect, Signal
from qtpy.QtGui import QPixmap, QIcon, QColor, QFont, QImage, qRgba, QFontMetrics
from qtpy.QtWidgets import QDialog, QPushButton, QLabel, QGraphicsOpacityEffect, QWidget


class Toast(QDialog):
    __DROP_SHADOW_SIZE = 5
    __spacing = 10
    __offset_x = 20
    __offset_y = 45
    __currently_shown = []
    __queue = []
    __maximum_on_screen = 3
    __UPDATE_POSITION_DURATION = 0.5
    __used = False
    def __init__(self, parent):
        super().__init__(parent)
        from .toast_ui import Ui_Dialog
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.Window |
                            Qt.WindowType.CustomizeWindowHint |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.__drop_shadow_layer_1 = QWidget(self)
        self.__drop_shadow_layer_1.setObjectName('toast-drop-shadow-layer-1')

        self.__drop_shadow_layer_2 = QWidget(self)
        self.__drop_shadow_layer_2.setObjectName('toast-drop-shadow-layer-2')

        self.__drop_shadow_layer_3 = QWidget(self)
        self.__drop_shadow_layer_3.setObjectName('toast-drop-shadow-layer-3')

        self.__drop_shadow_layer_4 = QWidget(self)
        self.__drop_shadow_layer_4.setObjectName('toast-drop-shadow-layer-4')

        self.__drop_shadow_layer_5 = QWidget(self)
        self.__drop_shadow_layer_5.setObjectName('toast-drop-shadow-layer-5')
        # Opacity effect for fading animations
        self.__opacity_effect = QGraphicsOpacityEffect()
        self.__opacity_effect.setOpacity(0.9)
        self.setGraphicsEffect(self.__opacity_effect)
        height = 80
        width = 500
        # Calculate width and height including space for drop shadow
        total_width = width + (Toast.__DROP_SHADOW_SIZE * 2)
        total_height = height + (Toast.__DROP_SHADOW_SIZE * 2)

        # Resize drop shadow
        self.__drop_shadow_layer_1.resize(total_width, total_height)
        self.__drop_shadow_layer_1.move(0, 0)
        self.__drop_shadow_layer_2.resize(total_width - 2, total_height - 2)
        self.__drop_shadow_layer_2.move(1, 1)
        self.__drop_shadow_layer_3.resize(total_width - 4, total_height - 4)
        self.__drop_shadow_layer_3.move(2, 2)
        self.__drop_shadow_layer_4.resize(total_width - 6, total_height - 6)
        self.__drop_shadow_layer_4.move(3, 3)
        self.__drop_shadow_layer_5.resize(total_width - 8, total_height - 8)
        self.__drop_shadow_layer_5.move(4, 4)

        self._ui.icon_label.setPixmap(get_themed_asset_icon("icons/about.svg").pixmap(40, 40))
        self._ui.close_button.setIcon(
            get_themed_asset_icon("icons/close.svg"))

        self.parent().activateWindow()
        self.setStyleSheet(Path(r"C:\Repos\conan_app_launcher\.venv\Lib\site-packages\pyqttoast\css\toast_notification.css").read_text())
        self._ui.time_label.hide()
        self._ui.close_button.clicked.connect(self.hide)

    def show(self):
        """Show the toast notification"""

        # Check if already used
        if self.__used:
            return

        # If max notifications on screen not reached, show notification
        if Toast.__maximum_on_screen > len(Toast.__currently_shown):
            self.__used = True
            Toast.__currently_shown.append(self)

        x,y = self.calc_xy()
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setEndValue(QPoint(x, y))
        self.pos_animation.setDuration(Toast.__UPDATE_POSITION_DURATION)
        self.pos_animation.start()
    def calc_xy(self):
        # Calculate vertical space taken up by all the currently showing notifications
        y_offset = 0
        for n in Toast.__currently_shown:
            if n == self:
                break
            y_offset += n.__notification.height() + Toast.__spacing

        # Get screen
        primary_screen = QGuiApplication.primaryScreen()
        current_screen = primary_screen

        # Calculate x and y position of notification
        x = 0
        y = 0

        x = (current_screen.geometry().width() - self.size().width()
                - Toast.__offset_x + current_screen.geometry().x())
        y = (current_screen.geometry().height()
                - Toast.__currently_shown[0].size().height()
                - Toast.__offset_y + current_screen.geometry().y() - y_offset)
        
        x = int(x - Toast.__DROP_SHADOW_SIZE)
        y = int(y - Toast.__DROP_SHADOW_SIZE)
        return x,y
