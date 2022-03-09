from tkinter.tix import Tree
from .common.theming import get_user_theme_color, set_style_sheet_option
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple
from ctypes.wintypes import MSG
import ctypes
import platform
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QPoint, QRect, Qt, QPropertyAnimation, QSize, QEasingCurve, QObject, QEvent
from PyQt5.QtWidgets import QPushButton, QWidget, QMainWindow, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy
from conan_app_launcher.app import asset_path

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
        self._resize_direction = 0
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
        effect.setColor(QtGui.QColor(68, 68, 68))
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

    def add_left_menu_entry(self, name: str, icon: QtGui.QIcon, is_upper_menu: bool, page_widget: QWidget):
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
        #hovermoveevent
        if event.type() == event.HoverMove: # QtGui.QHoverEvent
            if self._resize_press == 0:
                self.handle_resize_cursor(event)  # cursor position control for cursor shape setup
        elif event.type() == event.MouseButtonPress: # QtGui.QMouseEvent
            self._resize_press = 1
            self._resize_point = self.mapToGlobal(event.pos())
            self._last_geometry = self.geometry()
        elif event.type() == event.MouseButtonRelease:  # QtGui.QMouseEvent
            self._resize_press = 0
            self.handle_resize_cursor(event)
        elif event.type() == event.MouseMove:
            if self.cursor().shape() != Qt.ArrowCursor:
                self.resizing(event)

        return super().eventFilter(source, event)

    def handle_resize_cursor(self, event: QtGui.QMouseEvent, offset=5):
        rect = self.rect()
        top_left = rect.topLeft()
        top_right = rect.topRight()
        bottom_left = rect.bottomLeft()
        bottom_right = rect.bottomRight()
        pos = event.pos()

        #top
        if pos in QRect(QPoint(top_left.x()+offset, top_left.y()), QPoint(top_right.x()-offset, top_right.y()+offset)):
            self.setCursor(Qt.SizeVerCursor)
            self._resize_direction = 1
        #bottom
        elif pos in QRect(QPoint(bottom_left.x()+offset, bottom_left.y()), QPoint(bottom_right.x()-offset, bottom_right.y()-offset)):
            self.setCursor(Qt.SizeVerCursor)
            self._resize_direction = 2
        #right
        elif pos in QRect(QPoint(top_right.x()-offset, top_right.y()+offset), QPoint(bottom_right.x(), bottom_right.y()-offset)):
            self.setCursor(Qt.SizeHorCursor)
            self._resize_direction = 3
        #left
        elif pos in QRect(QPoint(top_left.x()+offset, top_left.y()+offset), QPoint(bottom_left.x(), bottom_left.y()-offset)):
            self.setCursor(Qt.SizeHorCursor)
            self._resize_direction = 4
        #top_right
        elif pos in QRect(QPoint(top_right.x(), top_right.y()), QPoint(top_right.x()-offset, top_right.y()+offset)):
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_direction = offset
        #bottom_left
        elif pos in QRect(QPoint(bottom_left.x(), bottom_left.y()), QPoint(bottom_left.x()+offset, bottom_left.y()-offset)):
            self.setCursor(Qt.SizeBDiagCursor)
            self._resize_direction = 6
        #top_left
        elif pos in QRect(QPoint(top_left.x(), top_left.y()), QPoint(top_left.x()+offset, top_left.y()+offset)):
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_direction = 7
        #bottom_right
        elif pos in QRect(QPoint(bottom_right.x(), bottom_right.y()), QPoint(bottom_right.x()-offset, bottom_right.y()-offset)):
            self.setCursor(Qt.SizeFDiagCursor)
            self._resize_direction = 8
        #default
        else:
            self.setCursor(Qt.ArrowCursor)

    def resizing(self, event):
        #top_resize
        if self._resize_direction == 1:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first = self._last_geometry.height()
            first -= last.y()
            Y = self._last_geometry.y()
            Y += last.y()
            if first > self.minimumHeight():
                self.setGeometry(self._last_geometry.x(), Y, self._last_geometry.width(), first)
            return
        #bottom_resize
        if self._resize_direction == 2:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first = self._last_geometry.height()
            first += last.y()
            self.resize(self._last_geometry.width(), first)
            return
        #right_resize
        if self._resize_direction == 3:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first = self._last_geometry.width()
            first += last.x()
            self.resize(first, self._last_geometry.height())
            return
        #left_resize
        if self._resize_direction == 4:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first = self._last_geometry.width()
            first -= last.x()
            X = self._last_geometry.x()
            X += last.x()

            if first > self.minimumWidth():
                self.setGeometry(X, self._last_geometry.y(), first, self._last_geometry.height())
            return
        #top_right_resize
        if self._resize_direction == 5:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first_width = self._last_geometry.width()
            first_height = self._last_geometry.height()
            first_Y = self._last_geometry.y()
            first_width += last.x()
            first_height -= last.y()
            first_Y += last.y()

            if first_height > self.minimumHeight():
                self.setGeometry(self._last_geometry.x(), first_Y, first_width, first_height)
            return
        #bottom_right_resize
        if self._resize_direction == 6:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first_width = self._last_geometry.width()
            first_height = self._last_geometry.height()
            first_X = self._last_geometry.x()
            first_width -= last.x()
            first_height += last.y()
            first_X += last.x()

            if first_width > self.minimumWidth():
                self.setGeometry(first_X, self._last_geometry.y(), first_width, first_height)
            return
        #top_left_resize
        if self._resize_direction == 7:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first_width = self._last_geometry.width()
            first_height = self._last_geometry.height()
            first_X = self._last_geometry.x()
            first_Y = self._last_geometry.y()
            first_width -= last.x()
            first_height -= last.y()
            first_X += last.x()
            first_Y += last.y()

            if first_height > self.minimumHeight() and first_width > self.minimumWidth():
                self.setGeometry(first_X, first_Y, first_width, first_height)
            return
        #bottom_right_resize
        if self._resize_direction == 8:
            last = self.mapToGlobal(event.pos())-self._resize_point
            first_width = self._last_geometry.width()
            first_height = self._last_geometry.height()
            first_width += last.x()
            first_height += last.y()

            self.setGeometry(self._last_geometry.x(), self._last_geometry.y(), first_width, first_height)
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
            self.ui.restore_max_button.setIcon(QtGui.QIcon(QtGui.QPixmap(str(asset_path / "icons" / "restore.png"))))
        else:
            self.ui.restore_max_button.setToolTip("Maximize")
            self.ui.restore_max_button.setIcon(QtGui.QIcon(QtGui.QPixmap(str(asset_path / "icons" / "maximize.png"))))
