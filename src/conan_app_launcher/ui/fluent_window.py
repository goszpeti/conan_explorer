import enum
from .common import get_user_theme_color, set_style_sheet_option
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple
from ctypes.wintypes import MSG
import ctypes
import platform
from PyQt5 import uic
from PyQt5.QtCore import QPoint, QRect, Qt, QPropertyAnimation, QSize, QEasingCurve, QObject, QEvent
from PyQt5.QtWidgets import QPushButton, QWidget, QMainWindow, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtGui import QColor, QIcon, QPixmap, QMouseEvent, QHoverEvent
from conan_app_launcher.app import asset_path
from enum import Enum


class ResizeDirection(Enum):
    default = 0
    top = 1
    left = 2
    right = 3
    bottom = 4
    top_left = 5
    top_right = 6
    bottom_left = 7
    bottom_right = 8

class FluentWindow(QMainWindow):

    def __init__(self, title_text: str="", native_windows_fcns=True, rounded_corners=True):
        super().__init__()
        current_dir = Path(__file__).parent
        self.ui = uic.loadUi(current_dir / "main_window.ui", baseinstance=self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.use_native_windows_fcns = True if platform.system() == "Windows" and native_windows_fcns else False
        self.left_menu_buttons: Dict[str, Tuple[QPushButton, QWidget]] = {}
        color = get_user_theme_color()  # TODO CSS
        self.button_highlight_color = "#B7B7B7"
        self.left_menu_min_size = 70
        self.left_menu_max_size = 220
        self.right_menu_min_size = 0
        self.right_menu_max_size = 200

        # resize related variables
        self._resize_press = 0
        self._resize_direction = ResizeDirection.default
        self._resize_point = QPoint()
        self._last_geometry = QRect()
        self.title_text = title_text

        # hint the included gui elements
        self.page_stacked_widget: QStackedWidget
        #QtWin.enableBlurBehindWindow(self)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.98)
        # TODO this really expensive
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setColor(QColor(68, 68, 68))
        effect.setBlurRadius(10)
        #self.setGraphicsEffect(effect)

        # window buttons
        self.ui.restore_max_button.clicked.connect(self.maximize_restore)
        self.ui.minimize_button.clicked.connect(self.showMinimized)
        self.ui.close_button.clicked.connect(self.close)

        self.ui.left_menu_top_subframe.mouseMoveEvent = self.move_window
        self.ui.top_frame.mouseMoveEvent = self.move_window

        self.ui.toggle_left_menu_button.clicked.connect(self.toggle_left_menu)
        self.ui.settings_button.clicked.connect(self.toggle_right_menu)
        self.page_info_label.setText("")

        # initial maximize state
        self.set_restore_max_button_state()
        self.enable_windows_native_animations()


    def move_window(self, event):
        # do nothing if the resize function is active
        if self.cursor().shape() != Qt.ArrowCursor:
            self.eventFilter(None, event) # call this to be able to resize
            return
        if self.use_native_windows_fcns:
            # enables Windows snap functions
            ctypes.windll.user32.ReleaseCapture()
            # emit native move signal with the following constants:
            # WM_SYSCOMMAND = 274, SC_MOVE = 61456 + HTCAPTION = 2
            ctypes.windll.user32.SendMessageA(int(self.window().winId()), 274, 61458, 0)
        else:
            # if maximized, return to normal be able to move
            if self.isMaximized():
                self.maximize_restore()
            # qt move
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_position)
                self.drag_position = event.globalPos()
                event.accept()

    def enable_windows_native_animations(self):
        if platform.system() != "Windows":
            return
        # sets up thickframe and other needed flag for WIN-Arrow functions an animations to work
        # needs custom resizing and border suppresion functions to work
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 65536
        WS_CAPTION = 12582912
        CS_DBLCLKS = 8
        WS_THICKFRAME = 262144
        WS_BORDER = 8388608
        style = ctypes.windll.user32.GetWindowLongA(int(self.winId()), GWL_STYLE)
        ctypes.windll.user32.SetWindowLongA(int(self.winId()), GWL_STYLE,
            style| WS_BORDER | WS_MAXIMIZEBOX | WS_CAPTION | CS_DBLCLKS | WS_THICKFRAME)

    def add_left_menu_entry(self, name: str, icon: QIcon, is_upper_menu: bool, page_widget: QWidget):
        button = QPushButton(self)
        button.setObjectName(name)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(size_policy)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        button.setLayoutDirection(Qt.LeftToRight)
        button.setToolTip(name)
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet("text-align:middle;")
        button.setCheckable(True)
        #page_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        page_widget.setMinimumHeight(300) # enable resizing of console on every page

        button.clicked.connect(self.switch_page)
        self.left_menu_buttons[name] = (button, page_widget)

        if is_upper_menu:
           self.ui.left_menu_middle_subframe.layout().addWidget(button)
        else:
            self.ui.left_menu_bottom_subframe.layout().addWidget(button)
        self.page_stacked_widget.addWidget(page_widget)

    def add_settings_menu_entry(self, name: str, widget: QWidget, icon=None, main_page_widget=False):
        button = QPushButton(self)
        button.setObjectName(name)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        button.setLayoutDirection(Qt.LeftToRight)
        button.setToolTip(name)
        if icon:
            button.setIcon(icon)
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet("text-align:middle;")

        self.right_menu_stacked_widget.addWidget(widget)
        if main_page_widget:
            self.page_stacked_widget.addWidget(widget)

        else:
            self.right_menu_back_button.setMinimumWidth(32)
            self.right_menu_back_button.setMaximumWidth(32)


    def switch_page(self):
        button = self.sender()
        name = button.objectName()
        _, page = self.left_menu_buttons[name]
        # switch page_stacked_widget to the saved page
        self.page_stacked_widget.setCurrentWidget(page)
        # TODO change button stylings - reset old selections and highlight new one
        for _ ,(inactive_button, _) in self.left_menu_buttons.items():
            inactive_button.setChecked(False)
            #inactive_button.setStyleSheet(set_style_sheet_option(
            #    inactive_button.styleSheet(), "background-color", "transparent"))

        #button.setStyleSheet(set_style_sheet_option(button.styleSheet(), "background-color", "#B7B7B7"))
        button.setChecked(True)
        self.page_title.setText(name)
        self.page_info_label.setText("")

    def toggle_left_menu(self):
        width = self.ui.left_menu_frame.width()

        # switch extended and minimized state
        if width == self.left_menu_min_size:
            width_to_set = self.left_menu_max_size
            maximize = True
        else:
            width_to_set = self.left_menu_min_size
            maximize = False

        self.animation = QPropertyAnimation(self.ui.left_menu_frame, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(width_to_set)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

        # hide title
        if maximize:
            self.title_label.setText(self.title_text)
        else:
            self.title_label.setText("")

        # hide menu button texts
        for name, (button, _) in self.left_menu_buttons.items():
            if maximize:
                button.setText(name)
                button.setStyleSheet("text-align:left;")
            else:
                button.setText("")
                button.setStyleSheet("text-align:middle;")


    def toggle_right_menu(self):
        width = self.ui.right_menu_frame.width()
        if width == self.right_menu_min_size:
            width_to_set = self.right_menu_max_size
        else:
            width_to_set = self.right_menu_min_size

        self.animation = QPropertyAnimation(self.ui.right_menu_frame, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(width)
        self.animation.setEndValue(width_to_set)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def mousePressEvent(self, event): # override
        """ Helper for moving window to know mouse position """
        self.drag_position = event.globalPos()

    def nativeEvent(self, eventType, message):
        """ Platform native events """
        if self.use_native_windows_fcns:
            msg = MSG.from_address(message.__int__())
            if msg.message == 131:  # ignore WM_NCCALCSIZE event. Suppresses native Window drawing of title-bar.
                return True, 0
        return QWidget.nativeEvent(self, eventType, message)

    def eventFilter(self, source: QObject, event: QEvent):
        """ Implements window resizing """
        if event.type() == event.HoverMove: # QtGui.QHoverEvent
            if self._resize_press == 0:
                self.handle_resize_cursor(event)  # cursor position control for cursor shape setup
        elif event.type() == event.MouseButtonPress: # QtGui.QMouseEvent
            self._resize_press = 1
            self._resize_point = self.mapToGlobal(event.pos()) # save the starting point of resize
            self._last_geometry = self.geometry()
        elif event.type() == event.MouseButtonRelease:  # QtGui.QMouseEvent
            self._resize_press = 0
            self.handle_resize_cursor(event)
        elif event.type() == event.MouseMove:
            if self.cursor().shape() != Qt.ArrowCursor:
                self.resizing(event)

        return super().eventFilter(source, event)

    def handle_resize_cursor(self, event: QHoverEvent, x_offset=10, y_offset=8):
        # using relative position, since the event can only be fired inside of the Window
        rect = self.rect()  # rect()
        top_left = rect.topLeft()
        top_right = rect.topRight()
        bottom_left = rect.bottomLeft()
        bottom_right = rect.bottomRight()
        position = event.pos() # relative pos to window
        width = self.width()
        height = self.height()
        
        if position in QRect(top_left.x() + x_offset, top_left.y(), width - 2*x_offset, y_offset):
            self._resize_direction = ResizeDirection.top
            self.setCursor(Qt.SizeVerCursor)
        elif position in QRect(bottom_left.x() + x_offset, bottom_left.y(), width - 2*x_offset, -y_offset):
            self._resize_direction = ResizeDirection.bottom
            self.setCursor(Qt.SizeVerCursor)
        elif position in QRect(top_right.x() - x_offset, top_right.y() + y_offset, x_offset, height - 2*y_offset):
            self._resize_direction = ResizeDirection.right
            self.setCursor(Qt.SizeHorCursor)
        elif position in QRect(top_left.x() + x_offset, top_left.y() + y_offset, -x_offset, height - 2*y_offset):
            self._resize_direction = ResizeDirection.left
            self.setCursor(Qt.SizeHorCursor)
        elif position in QRect(top_right.x(), top_right.y(), -x_offset, y_offset):
            self._resize_direction = ResizeDirection.top_right
            self.setCursor(Qt.SizeBDiagCursor)
        elif position in QRect(bottom_left.x(), bottom_left.y(), x_offset, -y_offset):
            self._resize_direction = ResizeDirection.bottom_left
            self.setCursor(Qt.SizeBDiagCursor)
        elif position in QRect(top_left.x(), top_left.y(), x_offset, y_offset):
            self._resize_direction = ResizeDirection.top_left
            self.setCursor(Qt.SizeFDiagCursor)
        elif position in QRect(bottom_right.x(), bottom_right.y(), -x_offset, -y_offset):
            self._resize_direction = ResizeDirection.bottom_right
            self.setCursor(Qt.SizeFDiagCursor)
        else: # no resize
            self.setCursor(Qt.ArrowCursor)

    def resizing(self, event):
        if self._resize_direction == ResizeDirection.top:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_height = self._last_geometry.height() - current_point.y()
            if new_height > self.minimumHeight():
                self.setGeometry(self._last_geometry.x(), self._last_geometry.y() +
                                 current_point.y(), self._last_geometry.width(), new_height)
            return
        elif self._resize_direction == ResizeDirection.bottom:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_height = self._last_geometry.height() + current_point.y()
            self.resize(self._last_geometry.width(), new_height)
            return
        elif self._resize_direction == ResizeDirection.right:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() + current_point.x()
            self.resize(new_width, self._last_geometry.height())
            return
        elif self._resize_direction == ResizeDirection.left:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() - current_point.x()
            if new_width > self.minimumWidth():
                self.setGeometry(self._last_geometry.x() + current_point.x(),
                                 self._last_geometry.y(), new_width, self._last_geometry.height())
            return
        elif self._resize_direction == ResizeDirection.top_right:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() + current_point.x()
            new_height = self._last_geometry.height() - current_point.y()
            if new_height > self.minimumHeight():
                self.setGeometry(self._last_geometry.x(), self._last_geometry.y() +
                                 current_point.y(), new_width, new_height)
            return
        elif self._resize_direction == ResizeDirection.bottom_right:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() + current_point.x()
            new_height = self._last_geometry.height() + current_point.y()
            self.setGeometry(self._last_geometry.x(), self._last_geometry.y(), new_width, new_height)
            return
        elif self._resize_direction == ResizeDirection.bottom_left:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() - current_point.x()
            new_height = self._last_geometry.height() + current_point.y()
            if new_width > self.minimumWidth():
                self.setGeometry(self._last_geometry.x() + current_point.x(),
                                 self._last_geometry.y(), new_width, new_height)
            return
        elif self._resize_direction == ResizeDirection.top_left:
            current_point = self.mapToGlobal(event.pos()) - self._resize_point
            new_width = self._last_geometry.width() - current_point.x()
            new_height = self._last_geometry.height() - current_point.y()
            if new_height > self.minimumHeight() and new_width > self.minimumWidth():
                self.setGeometry(self._last_geometry.x() + current_point.x(),
                                 self._last_geometry.y() + current_point.y(), new_width, new_height)
            return

    def maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            #self.resize(self.width()+1, self.height()+1)
        else:
            self.showMaximized()
        self.set_restore_max_button_state()

    def set_restore_max_button_state(self):
        if self.isMaximized():
            self.ui.restore_max_button.setToolTip("Restore")
            self.ui.restore_max_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "restore.png"))))
        else:
            self.ui.restore_max_button.setToolTip("Maximize")
            self.ui.restore_max_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "maximize.png"))))
