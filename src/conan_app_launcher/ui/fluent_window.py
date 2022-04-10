import platform
if platform.system() == "Windows":
    import ctypes
    from ctypes.wintypes import MSG
from enum import Enum
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar, Union

# uses Logger, settings and theming related functions
from conan_app_launcher import app
from conan_app_launcher.app import asset_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.settings import FONT_SIZE
from .widgets import AnimatedToggle

from PyQt5.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation, QRect, QSize, Qt
from PyQt5.QtGui import QHoverEvent, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, 
                            QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from .common import get_themed_asset_image

from .fluent_window_ui import Ui_MainWindow

LEFT_MENU_MIN_WIDTH = 80
LEFT_MENU_MAX_WIDTH = 300
RIGHT_MENU_MIN_WIDTH = 0
RIGHT_MENU_MAX_WIDTH = 300

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

class ThemedWidget():
    def __init__(self) -> None:
        self._icon_map: Dict[Union[QPushButton, QLabel], str] = {}  # for re-theming

    @property
    def icon_map(self):
        return self._icon_map

    def add_themed_icon(self, widget: Union[QPushButton, QLabel], asset_rel_path: str):
        widget.setIcon(QIcon(get_themed_asset_image(asset_rel_path)))
        self.icon_map[widget] = asset_rel_path

    def reload_themed_icons(self):
        for widget, asset_rel_path in self.icon_map.items():
            widget.setIcon(QIcon(get_themed_asset_image(asset_rel_path)))


class FluentWindow(QMainWindow, ThemedWidget):

    class RightSubMenu(QWidget, ThemedWidget):
        TOGGLE_WIDTH = 70
        TOGGLE_HEIGHT = 50

        def __init__(self, name: str = ""):
            super().__init__()
            self.name = name
            self.setLayout(QVBoxLayout(self))
            self.layout().addItem(QSpacerItem(
                20, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))
            self.layout().setContentsMargins(0, 4, 0, 0)

        def add_custom_menu_entry(self, widget: QWidget):
            """ Very basic custom entry, no extra functions """
            self.layout().insertWidget(self.layout().count() - 1, widget)

        def add_named_custom_entry(self, name: str, widget: QWidget):
            """ Creates a Frame with a text label and a custom widget under it and adds it to the menu """
            label = QLabel(name)
            label.adjustSize() # adjust layout according to size and throw a warning, if too big?
            widget.adjustSize()
            widget.setMinimumHeight(50)
            widget.setMaximumHeight(100)

            frame = QFrame(self)
            if label.width() > (RIGHT_MENU_MAX_WIDTH - widget.width() - 10):  # 10 for margin
                frame.setLayout(QVBoxLayout(frame))
            else:
                frame.setLayout(QHBoxLayout(frame))
            label.setMaximumHeight(50)

            if label.width() > RIGHT_MENU_MAX_WIDTH:
                Logger().debug(f"{str(name)} right side menu exceeds max width!")
            frame.layout().setContentsMargins(0, 0, 0, 0)
            frame.layout().addWidget(label)
            frame.layout().addWidget(widget)
            self.add_custom_menu_entry(frame)

        def add_toggle_menu_entry(self, name: str, target: Callable, initial_state: bool):
            toggle = AnimatedToggle(self)
            toggle.setMinimumSize(self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT)
            toggle.setMaximumSize(self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT)
            toggle.setChecked(initial_state)
            toggle.stateChanged.connect(target)
            self.add_named_custom_entry(name, toggle)
            return toggle


        def add_button_menu_entry(self, name: str, target: Callable, asset_icon:str="", shortcut: Optional[QKeySequence]=None, parent=None):
            """ Adds a button with an icon and links with a callable. Optionally can have a key shortcut. """
            button = QPushButton(self)
            button.setObjectName(name + "_submenu")
            button.setMinimumSize(QSize(64, 50))
            button.setMaximumHeight(50)
            button.setLayoutDirection(Qt.LeftToRight)
            if asset_icon:
                self.add_themed_icon(button, asset_icon)
            button.setIconSize(QSize(32, 32))
            button.setText(name)  # "  " +
            font_size = app.active_settings.get_int(FONT_SIZE) # - 2 # TODO
            button.setStyleSheet(f"text-align:left;font-size:{font_size}pt")
            # insert before spacer
            self.layout().insertWidget(self.layout().count() - 1, button)

            button.clicked.connect(target)

            if not shortcut:
                return button
            # use global shortcut instead of button.setShortcut -> Works from anywhere
            shortcut_obj = QShortcut(shortcut, parent)
            shortcut_obj.activated.connect(target)
            button.setText(f"{button.text()} ({shortcut.toString()})")
            return button

        
        # TODO add embeddable widgets like buttons, etc

    class PageStore():
        """ Saves all relevant information for pages accessible from the left menu and provides easy 
        retrieval methods for all members.
         """

        def __init__(self) -> None:
            self._page_widgets: Dict[str, Tuple[QPushButton, QWidget, Optional[FluentWindow.RightSubMenu]]] = {}

        def get_page_by_name(self, name: str) -> QWidget:
            return self._page_widgets[name][1]

        def get_button_by_name(self, name: str) -> QPushButton:
            return self._page_widgets[name][0]

        def get_right_menu_by_name(self, name: str) -> "Optional[FluentWindow.RightSubMenu]":
            return self._page_widgets[name][2]

        def get_right_menu_by_type(self, type: Type) -> "Optional[FluentWindow.RightSubMenu]":
            for _, (_, page, rm) in self._page_widgets.items():
                if isinstance(page, type):
                    return rm
            raise Exception(f"{type} not in page_widgets!")

        def get_button_by_type(self, type: Type) -> QPushButton:
            for _, (button, page, _) in self._page_widgets.items():
                if isinstance(page, type):
                    return button
            raise Exception(f"{type} not in page_widgets!")

        T = TypeVar('T')
        def get_page_by_type(self, type: Type[T]) -> T:
            for _, (_, page, _) in self._page_widgets.items():
                if isinstance(page, type):
                    return page
            raise Exception(f"{type} not in page_widgets!")
        
        def get_all_buttons(self):
            buttons = []
            for button, _, _ in self._page_widgets.values():
                buttons.append(button)
            return buttons

        def add_new_page(self, name, button, page, right_sub_menu):
            self._page_widgets[name] = (button, page, right_sub_menu)


    def __init__(self, title_text: str="", native_windows_fcns=True, rounded_corners=True):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self._use_native_windows_fcns = True if platform.system() == "Windows" and native_windows_fcns else False
        # all buttons and widgets to be able to shown on the main page (from settings and left menu)
        self.page_widgets = FluentWindow.PageStore()

        # resize related variables
        self._resize_press = 0
        self._resize_direction = ResizeDirection.default
        self._resize_point = QPoint()
        self._last_geometry = QRect()
        self.title_text = title_text

        self.ui.left_menu_frame.setMinimumWidth(LEFT_MENU_MIN_WIDTH)
        self.ui.toggle_left_menu_button.setMaximumWidth(LEFT_MENU_MIN_WIDTH)
        self.ui.settings_button.setMaximumWidth(LEFT_MENU_MIN_WIDTH)

        self.add_themed_icon(self.ui.toggle_left_menu_button, "icons/menu_stripes.png")
        self.add_themed_icon(self.ui.settings_button, "icons/settings.png")
        self.add_themed_icon(self.ui.right_menu_top_back_button, "icons/back.png")
        self.add_themed_icon(self.ui.right_menu_bottom_back_button, "icons/back.png")

        self.ui.minimize_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "minus.png"))))
        self.ui.close_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "close.png"))))
        # window buttons
        self.ui.restore_max_button.clicked.connect(self.maximize_restore)
        self.ui.minimize_button.clicked.connect(self.showMinimized)
        self.ui.close_button.clicked.connect(self.close)

        self.ui.left_menu_top_subframe.mouseMoveEvent = self.move_window
        self.ui.top_frame.mouseMoveEvent = self.move_window
        self.ui.top_frame.mouseDoubleClickEvent = self.maximize_restore

        self.ui.toggle_left_menu_button.clicked.connect(self.toggle_left_menu)
        self.ui.settings_button.clicked.connect(self.toggle_right_menu)
        self.ui.page_info_label.setText("")

        # initial maximize state
        self.set_restore_max_button_state()
        self.enable_windows_native_animations()

        # minimize settings window buttons
        self.ui.right_menu_bottom_back_button.hide()
        self.ui.right_menu_top_back_button.hide()

        # connect right menu bottom back bottom
        self.ui.right_menu_bottom_back_button.clicked.connect(
            lambda: self.ui.right_menu_bottom_content_sw.setCurrentWidget(self.ui.main_settings_page))
        self.ui.right_menu_bottom_back_button.clicked.connect(self.ui.right_menu_bottom_back_button.hide)

        # TODO: needed?
        #self.ui.right_menu_top_content_sw.setCurrentWidget(self.ui.main_top_settings_page)

    def apply_theme(self):
        """ This function must be able to reload all icons from the left and right menu bar. """
        self.reload_themed_icons()
        for submenu in self.ui.right_menu_bottom_content_sw.findChildren(FluentWindow.RightSubMenu):
            submenu.reload_themed_icons()
        for submenu in self.ui.right_menu_top_content_sw.findChildren(FluentWindow.RightSubMenu):
            submenu.reload_themed_icons()

    def move_window(self, event):
        # do nothing if the resize function is active
        if self.cursor().shape() != Qt.ArrowCursor:
            self.eventFilter(None, event) # call this to be able to resize
            return
        if self._use_native_windows_fcns:
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

    def add_left_menu_entry(self, name: str, asset_icon: str, is_upper_menu: bool, page_widget: QWidget, create_page_menu=False):
        button = QPushButton("", self.ui.left_menu_frame)
        self.add_themed_icon(button, asset_icon)
        button.setObjectName(name)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(size_policy)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        button.setToolTip(name)
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet("text-align:middle;")
        button.setCheckable(True)
        page_widget.setMinimumHeight(300) # enable resizing of console on every page

        button.clicked.connect(self.switch_page)

        # add a stacked widget to right menu with title
        rsm = None
        if create_page_menu:
            rsm = FluentWindow.RightSubMenu()
            self.ui.right_menu_top_content_sw.addWidget(rsm)
            rsm.setParent(self.ui.right_menu_top_content_sw)
        self.page_widgets.add_new_page(name, button, page_widget, rsm)

        if is_upper_menu:
           self.ui.left_menu_middle_subframe.layout().addWidget(button)
        else:
            self.ui.left_menu_bottom_subframe.layout().addWidget(button)
        self.ui.page_stacked_widget.addWidget(page_widget)
        page_widget.setParent(self.ui.page_stacked_widget)

    # can only be called for top level menu
    def add_right_bottom_menu_main_page_entry(self, name: str, page_widget: QWidget, asset_icon:str=""):
        button = self.add_right_menu_entry(name, asset_icon, upper_menu_sw=False)
        self.page_widgets.add_new_page(name, button, page_widget, None)
        self.ui.page_stacked_widget.addWidget(page_widget)
        button.clicked.connect(self.switch_page)
        button.clicked.connect(self.toggle_right_menu)
        page_widget.setParent(self.ui.page_stacked_widget)

    def add_right_menu_sub_menu(self, sub_menu: RightSubMenu, asset_icon: str = "", is_upper_menu=False):
        button = self.add_right_menu_entry(sub_menu.name, asset_icon, upper_menu_sw=False)
        self.ui.right_menu_bottom_content_sw.addWidget(sub_menu)
        sub_menu.setParent(self.ui.right_menu_bottom_content_sw)
        button.clicked.connect(self.ui.right_menu_bottom_back_button.show)
        button.clicked.connect(lambda: self.ui.right_menu_bottom_content_sw.setCurrentWidget(sub_menu))
        return button

    def add_right_menu_entry(self, name: str, asset_icon: str, upper_menu_sw=None):
        button = QPushButton(self.ui.right_menu_frame)
        button.setObjectName(name)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        button.setLayoutDirection(Qt.LeftToRight)
        if asset_icon:
            self.add_themed_icon(button, asset_icon)

        button.setIconSize(QSize(32, 32))
        button.setText("  " + name)
        button.setStyleSheet("text-align:left;")

        if upper_menu_sw:
            # TODO Add a stacked widget page for each main page entry 
            upper_menu_sw.layout().addWidget(button)
        else:
            self.ui.main_settings_page.layout().insertWidget(self.ui.main_settings_page.layout().count()-1, button)
        return button

    def add_right_menu_line(self, is_upper_menu=False):

        line = QFrame(self.ui.right_menu_frame)
        line.setMidLineWidth(3)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        if is_upper_menu:
            # TODO Add a stacked widget page for each main page entry
            self.ui.right_menu_top_content_sw.addWidget(line)
        else:
            self.ui.main_settings_page.layout().insertWidget(self.ui.main_settings_page.layout().count()-1, line)


    def switch_page(self):
        sender_button: QPushButton = self.sender()
        name = sender_button.objectName()
        page = self.page_widgets.get_page_by_name(name)
        # switch page_stacked_widget to the saved page
        self.ui.page_stacked_widget.setCurrentWidget(page)
        # TODO change button stylings - reset old selections and highlight new one
        for button in self.page_widgets.get_all_buttons():
            button.setChecked(False)

        sender_button.setChecked(True)
        self.ui.page_title.setText(name)
        self.ui.page_info_label.setText("")

        rm = self.page_widgets.get_right_menu_by_name(name)
        if not rm:
        # check page settings at minimize if not needed
            self.ui.right_menu_top_frame.hide()
        else:
            self.ui.right_menu_top_content_sw.setCurrentWidget(rm)

        if self.ui.settings_button.isChecked():
            self.toggle_right_menu()


    def toggle_left_menu(self):
        width = self.ui.left_menu_frame.width()

        # switch extended and minimized state
        if width == LEFT_MENU_MIN_WIDTH:
            width_to_set = LEFT_MENU_MAX_WIDTH
            maximize = True
        else:
            width_to_set = LEFT_MENU_MIN_WIDTH
            maximize = False

        self.left_anim = QPropertyAnimation(self.ui.left_menu_frame, b"minimumWidth")
        self.left_anim.setDuration(200)
        self.left_anim.setStartValue(width)
        self.left_anim.setEndValue(width_to_set)
        self.left_anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.left_anim.start()

        # hide title
        if maximize:
            self.ui.title_label.setText(self.title_text)
        else:
            self.ui.title_label.setText("")

        # hide menu button texts
        for button in self.ui.left_menu_middle_subframe.findChildren(QPushButton): # name, (button, _) in self.page_entries.items():
            if maximize:
                button.setText(button.objectName())
                button.setStyleSheet("text-align:left;")
            else:
                button.setText("")
                button.setStyleSheet("text-align:middle;")

        if self.ui.settings_button.isChecked():
            self.toggle_right_menu()

    def toggle_right_menu(self):
        width = self.ui.right_menu_frame.width()
        if width == RIGHT_MENU_MIN_WIDTH:
            width_to_set = RIGHT_MENU_MAX_WIDTH
        else:
            width_to_set = RIGHT_MENU_MIN_WIDTH
            self.ui.settings_button.setChecked(False)

        self.right_anim = QPropertyAnimation(self.ui.right_menu_frame, b"minimumWidth")
        self.right_anim.setDuration(200)
        self.right_anim.setStartValue(width)
        self.right_anim.setEndValue(width_to_set)
        self.right_anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.right_anim.start()


    def mousePressEvent(self, event): # override
        """ Helper for moving window to know mouse position """
        self.drag_position = event.globalPos()

    def nativeEvent(self, eventType, message):
        """ Platform native events """
        # TODO crashes on Linux sometimes...
        if self._use_native_windows_fcns:
            msg = MSG.from_address(message.__int__())
            if msg.message == 131:  # ignore WM_NCCALCSIZE event. Suppresses native Window drawing of title-bar.
                return True, 0
        return super().nativeEvent(eventType, message)

    def eventFilter(self, source: QObject, event: QEvent):
        """ Implements window resizing """
        if self.isMaximized(): # no resize when maximized
            return super().eventFilter(source, event)
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

    def maximize_restore(self, a0=False): # dummy arg to be used asn an event slot  TODO: better solution
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.set_restore_max_button_state()

    def set_restore_max_button_state(self):
        if self.isMaximized():
            self.ui.restore_max_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "restore.png"))))
        else:
            self.ui.restore_max_button.setIcon(QIcon(QPixmap(str(asset_path / "icons" / "maximize.png"))))
