import platform

if platform.system() == "Windows":
    import ctypes
    from ctypes.wintypes import MSG

from enum import Enum
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar, Union

# uses Logger, settings and theming related functions
from conan_app_launcher.app import asset_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core.system import is_windows_11

from PyQt5.QtCore import (QEasingCurve, QEvent, QObject, QPoint,
                          QPropertyAnimation, QRect, QSize, Qt)
from PyQt5.QtGui import QHoverEvent, QIcon, QKeySequence, QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QShortcut, QSizePolicy,
                             QStackedWidget, QVBoxLayout, QWidget)

from ..common import get_themed_asset_image
from ..widgets import AnimatedToggle



def get_display_scaling():
    if platform.system() == "Windows":
        return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    else: # TODO not yet implemented for Linux
        return 2.2


LEFT_MENU_MIN_WIDTH = 80
LEFT_MENU_MAX_WIDTH = int(310 + 20*(2/get_display_scaling()))
RIGHT_MENU_MIN_WIDTH = 0
RIGHT_MENU_MAX_WIDTH = int(200 + 200*(2/get_display_scaling()))

def gen_obj_name(name: str) -> str:
    """ Generates an object name from a menu title or name (spaces to underscores and lowercase) """
    return name.replace(" ", "_").lower()


class WidgetNotFoundException(Exception):
    """ Raised, when a widget searched for, ist in the parent container. """
    pass


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
        self._icon_map: Dict[QPushButton, str] = {}  # for re-theming

    @property
    def icon_map(self):
        return self._icon_map

    def add_themed_icon(self, widget: QPushButton, asset_rel_path: str):
        widget.setIcon(QIcon(get_themed_asset_image(asset_rel_path)))
        self.icon_map[widget] = asset_rel_path

    def reload_themed_icons(self):
        for widget, asset_rel_path in self.icon_map.items():
            widget.setIcon(QIcon(get_themed_asset_image(asset_rel_path)))


class SideSubMenu(QWidget, ThemedWidget):
    TOGGLE_WIDTH = 70
    TOGGLE_HEIGHT = 50

    def __init__(self, parent_stacked_widget: QStackedWidget, title: str = "", is_top_level=False):
        QWidget.__init__(self, parent_stacked_widget)
        ThemedWidget.__init__(self)
        from .side_menu_ui import Ui_SideMenu  # need to resolve circular import
        self.ui = Ui_SideMenu()
        self.ui.setupUi(self)

        self.parent_stacked_widget = parent_stacked_widget
        self.parent_stacked_widget.addWidget(self)
        self.title = title
        self.is_top_level = is_top_level
        self.set_title(title)
        self._content_layout = self.ui.content_frame_layout
        self.add_themed_icon(self.ui.side_menu_title_button, "icons/back.png")

        if is_top_level:
            self.ui.side_menu_title_button.hide()  # off per default
 

    def set_title(self, title: str):
        self.ui.side_menu_title_label.setText(title)

    def enable_collapsible(self) -> bool:
        """
        Enable this side menu being collapsed. The side_menu_title_button will be used for this,
        so this must be a top level menu, otherwise the back button could not be operated anymore.
        """
        if not self.is_top_level:
            return False
        self.add_themed_icon(self.ui.side_menu_title_button, "icons/expand.png")
        self.ui.side_menu_title_button.clicked.connect(self.on_expand_minimize)  # off per default
        return True

    def on_expand_minimize(self):
        """ The title button can be used to minimize a submenu """
        if self.ui.side_menu_content_frame.height() > 0:
            self.ui.side_menu_content_frame.setMaximumHeight(0)
            self.add_themed_icon(self.ui.side_menu_title_button, "icons/forward.png")
        else:
            self.add_themed_icon(self.ui.side_menu_title_button, "icons/expand.png")
            self.ui.side_menu_content_frame.setMaximumHeight(4096)

    def get_menu_entry_by_name(self, name: str) -> Optional[QWidget]:
        return self.findChildren(QWidget, gen_obj_name(name))[0]

    def add_custom_menu_entry(self, widget: QWidget, name: Optional[str] = None):
        """ Very basic custom entry, no extra functions """
        if name:
            widget.setObjectName(gen_obj_name(name))
        self._content_layout.insertWidget(self._content_layout.count() - 1, widget)

    def add_menu_line(self):
        line = QFrame(self)
        line.setMidLineWidth(3)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.add_custom_menu_entry(line, "line")  # TODO give them an index?

    def add_named_custom_entry(self, name: str, widget: QWidget):
        """ Creates a Frame with a text label and a custom widget under it and adds it to the menu """
        label = QLabel(text=name, parent=self)
        label.adjustSize()  # adjust layout according to size and throw a warning, if too big?
        label.setObjectName(gen_obj_name(name) + "_label")
        widget.adjustSize()
        widget.setMinimumHeight(50)
        widget.setMaximumHeight(100)
        widget.setObjectName(gen_obj_name(name) + "_widget")

        frame = QFrame(self)
        if label.width() > (RIGHT_MENU_MAX_WIDTH - widget.width() - 30):  # aggressive 30 px padding
            frame.setLayout(QVBoxLayout(frame))
        else:
            frame.setLayout(QHBoxLayout(frame))
        label.setMaximumHeight(50)

        if label.width() > RIGHT_MENU_MAX_WIDTH:
            Logger().debug(f"{str(name)} right side menu exceeds max width!")
        frame.layout().setContentsMargins(5, 0, 5, 0)
        frame.layout().setSpacing(4)
        frame.layout().addWidget(label)
        frame.layout().addWidget(widget)
        self.add_custom_menu_entry(frame, name)

    def add_toggle_menu_entry(self, name: str, target: Callable, initial_state: bool):
        toggle = AnimatedToggle(self)
        toggle.setMinimumSize(self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT)
        toggle.setMaximumSize(self.TOGGLE_WIDTH, self.TOGGLE_HEIGHT)
        toggle.setChecked(initial_state)
        toggle.stateChanged.connect(target)
        self.add_named_custom_entry(name, toggle)
        return toggle

    def add_sub_menu(self, sub_menu: "SideSubMenu", asset_icon: str = ""):
        button = self.add_button_menu_entry(sub_menu.title, sub_menu.ui.side_menu_title_button.show, asset_icon)
        button.clicked.connect(lambda: self.parent_stacked_widget.setCurrentWidget(sub_menu))
        sub_menu.ui.side_menu_title_button.clicked.connect(lambda: self.parent_stacked_widget.setCurrentWidget(self))
        return button

    def add_button_menu_entry(self, name: str, target: Callable, asset_icon: str = "",
                              shortcut: Optional[QKeySequence] = None, shortcut_parent: Optional[QWidget]=None):
        """ Adds a button with an icon and links with a callable. Optionally can have a key shortcut. """
        button = QPushButton(self)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        if asset_icon:
            self.add_themed_icon(button, asset_icon)
        button.setIconSize(QSize(32, 32))
        button.setText(name)
        button.setStyleSheet(f"text-align:left")
        # insert before spacer
        self.add_custom_menu_entry(button, name)

        button.clicked.connect(target)

        if not shortcut:
            return button
        assert shortcut_parent, "Add shortcut_parent if shortcut is True!"

        # use global shortcut instead of button.setShortcut -> Works from anywhere
        shortcut_obj = QShortcut(shortcut, shortcut_parent)
        shortcut_obj.activated.connect(target)
        button.setText(f"{button.text()} ({shortcut.toString()})")
        return button


class FluentWindow(QMainWindow, ThemedWidget):

    class PageStore():
        """ Saves all relevant information for pages accessible from the left menu and provides easy 
        retrieval methods for all members.
        """

        def __init__(self) -> None:
            self._page_widgets: Dict[str, Tuple[QPushButton, QWidget, Optional[SideSubMenu], str]] = {}

        def get_button_by_name(self, name: str) -> QPushButton:
            return self._page_widgets[gen_obj_name(name)][0]

        def get_page_by_name(self, name: str) -> QWidget:
            return self._page_widgets[gen_obj_name(name)][1]

        def get_side_menu_by_name(self, name: str) -> "Optional[SideSubMenu]":
            return self._page_widgets[gen_obj_name(name)][2]

        def get_display_name_by_name(self, name: str) -> str:
            return self._page_widgets[gen_obj_name(name)][3]

        def get_side_menu_by_type(self, type: Type) -> "Optional[SideSubMenu]":
            for _, (_, page, menu, _) in self._page_widgets.items():
                if isinstance(page, type):
                    return menu
            raise WidgetNotFoundException(f"{type} not in page_widgets!")

        def get_button_by_type(self, type: Type) -> QPushButton:
            for _, (button, page, _, _) in self._page_widgets.items():
                if isinstance(page, type):
                    return button
            raise WidgetNotFoundException(f"{type} not in page_widgets!")

        T = TypeVar('T')
        def get_page_by_type(self, type: Type[T]) -> T:
            for _, (_, page, _, _), in self._page_widgets.items():
                if isinstance(page, type):
                    return page
            raise WidgetNotFoundException(f"{type} not in page_widgets!")

        def get_all_buttons(self):
            buttons = []
            for button, _, _, _ in self._page_widgets.values():
                buttons.append(button)
            return buttons

        def get_all_pages(self):
            pages = []
            for _, (_, page, _, _), in self._page_widgets.items():
                pages.append(page)
            return pages

        def add_new_page(self, name, button, page, right_sub_menu):
            self._page_widgets[gen_obj_name(name)] = (button, page, right_sub_menu, name)

    def __init__(self, title_text: str = "", native_windows_fcns=True, rounded_corners=True):
        super().__init__()
        from .fluent_window_ui import Ui_MainWindow  # need to resolve circular import
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.main_general_settings_menu = SideSubMenu(
            self.ui.right_menu_bottom_content_sw, "General Settings", True)
        self.ui.right_menu_bottom_content_sw.addWidget(self.main_general_settings_menu)
        self.ui.right_menu_bottom_content_sw.setCurrentWidget(self.main_general_settings_menu)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        if is_windows_11() or platform.system() == "Linux": # To hide black edges around the border rounding
            self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._use_native_windows_fcns = True if platform.system() == "Windows" and native_windows_fcns else False
        # all buttons and widgets to be able to shown on the main page (from settings and left menu)
        self.page_widgets = FluentWindow.PageStore()

        # resize related variables
        self._resize_press = 0
        self._resize_direction = ResizeDirection.default
        self._resize_point = QPoint()
        self._last_geometry = QRect()
        self.title_text = title_text
        self.drag_position = None

        self.ui.left_menu_frame.setMinimumWidth(LEFT_MENU_MIN_WIDTH)
        menu_margins = self.ui.left_menu_bottom_subframe.layout().contentsMargins()
        button_offset = menu_margins.right() + menu_margins.left()
        # fix buttons sizes, so they don't expand on togglling the menu
        self.ui.toggle_left_menu_button.setMinimumWidth(LEFT_MENU_MIN_WIDTH - button_offset)
        self.ui.toggle_left_menu_button.setMaximumWidth(LEFT_MENU_MIN_WIDTH - button_offset)
        self.ui.settings_button.setMinimumWidth(LEFT_MENU_MIN_WIDTH - button_offset)
        self.ui.settings_button.setMaximumWidth(LEFT_MENU_MIN_WIDTH - button_offset)

        self.add_themed_icon(self.ui.toggle_left_menu_button, "icons/menu_stripes.png")
        self.add_themed_icon(self.ui.settings_button, "icons/settings.png")

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

        # clear default strings
        self.ui.page_info_label.setText("")
        self.ui.title_label.setText("")

        # initial maximize state
        self.set_restore_max_button_state()
        self.enable_windows_native_animations()

    def apply_theme(self):
        """ This function must be able to reload all icons from the left and right menu bar. """
        self.reload_themed_icons()
        for submenu in self.ui.right_menu_bottom_content_sw.findChildren(SideSubMenu):
            submenu.reload_themed_icons()
        for submenu in self.ui.right_menu_top_content_sw.findChildren(SideSubMenu):
            submenu.reload_themed_icons()

    def move_window(self, a0):
        event = a0
        # do nothing if the resize function is active
        if self.cursor().shape() != Qt.ArrowCursor:
            self.eventFilter(self, event)  # call this to be able to resize
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
                self.maximize_restore(None)
            # qt move
            if event.buttons() == Qt.LeftButton:
                if self.drag_position is None:
                    return
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
                                            style | WS_BORDER | WS_MAXIMIZEBOX | WS_CAPTION | CS_DBLCLKS | WS_THICKFRAME)

    def add_left_menu_entry(self, name: str, asset_icon: str, is_upper_menu: bool, page_widget: QWidget, create_page_menu=False):
        button = QPushButton("", self.ui.left_menu_frame)
        self.add_themed_icon(button, asset_icon)
        button.setObjectName(gen_obj_name(name))
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(size_policy)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        button.setToolTip(name)
        button.setIconSize(QSize(32, 32))
        button.setStyleSheet("text-align:middle;")
        button.setCheckable(True)
        page_widget.setMinimumHeight(300)  # enable resizing of console on every page

        button.clicked.connect(self.switch_page)

        # add a stacked widget to right menu with title
        right_sub_menu = None
        if create_page_menu:
            right_sub_menu = SideSubMenu(self.ui.right_menu_top_content_sw, name, True)
            self.ui.right_menu_top_content_sw.addWidget(right_sub_menu)
        self.page_widgets.add_new_page(name, button, page_widget, right_sub_menu)

        if is_upper_menu:
            self.ui.left_menu_middle_subframe.layout().addWidget(button)
        else:
            self.ui.left_menu_bottom_subframe.layout().addWidget(button)
        self.ui.page_stacked_widget.addWidget(page_widget)
        page_widget.setParent(self.ui.page_stacked_widget)

    # can only be called for top level menu
    def add_right_bottom_menu_main_page_entry(self, name: str, page_widget: QWidget, asset_icon: str = ""):
        """ Add a main page entry, where the button is in the settings menu"""
        button = self.main_general_settings_menu.add_button_menu_entry(name, self.switch_page, asset_icon)
        self.page_widgets.add_new_page(name, button, page_widget, None)
        self.ui.page_stacked_widget.addWidget(page_widget)
        button.clicked.connect(self.toggle_right_menu)
        page_widget.setParent(self.ui.page_stacked_widget)

    def switch_page(self):
        sender_button = self.sender()
        assert isinstance(sender_button, QPushButton), "Switch page can only be triggered from a button!"
        obj_name = sender_button.objectName()
        page = self.page_widgets.get_page_by_name(obj_name)
        # switch page_stacked_widget to the saved page
        self.ui.page_stacked_widget.setCurrentWidget(page)
        # change button stylings - reset old selections and highlight new one
        for button in self.page_widgets.get_all_buttons():
            button.setChecked(False)

        sender_button.setChecked(True)
        self.ui.page_title.setText(self.page_widgets.get_display_name_by_name(obj_name))
        self.ui.page_info_label.setText("")

        side_menu = self.page_widgets.get_side_menu_by_name(obj_name)
        if not side_menu:
            # check page settings at minimize if not needed
            self.ui.right_menu_top_content_sw.hide()
        else:
            self.ui.right_menu_top_content_sw.show()
            self.ui.right_menu_top_content_sw.setCurrentWidget(side_menu)

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
        # name, (button, _) in self.page_entries.items():
        for button in self.ui.left_menu_middle_subframe.findChildren(QPushButton):
            name = self.page_widgets.get_display_name_by_name(button.objectName())
            if maximize:
                button.setText(name)
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

    def nativeEvent(self, eventType, message): # override
        """ Platform native events """
        if self._use_native_windows_fcns:
            msg = MSG.from_address(message.__int__())
            if msg.message == 131:  # ignore WM_NCCALCSIZE event. Suppresses native Window drawing of title-bar.
                return True, 0
        return super().nativeEvent(eventType, message)

    def eventFilter(self, source: QObject, event: QEvent):  # override
        """ Implements window resizing """
        self.set_restore_max_button_state()
        if self.isMaximized():  # no resize when maximized
            return super().eventFilter(source, event)
        if isinstance(event, QHoverEvent):  # Use isinstance instead of type because of typehinting
            if event.type() == event.HoverMove and self._resize_press == 0:
                self.handle_resize_cursor(event)  # cursor position control for cursor shape setup
        elif isinstance(event, QMouseEvent):
            if event.type() == event.MouseButtonPress:
                if event.button() != Qt.LeftButton:
                    return super().eventFilter(source, event)
                self._resize_press = 1
                self._resize_point = self.mapToGlobal(event.pos())  # save the starting point of resize
                self._last_geometry = self.geometry()
                self.resizing(event)
                self._resize_press = 0

        return super().eventFilter(source, event)

    def handle_resize_cursor(self, event: QHoverEvent, x_offset=10, y_offset=8):
        # using relative position, since the event can only be fired inside of the Window
        rect = self.rect()  # rect()
        top_left = rect.topLeft()
        top_right = rect.topRight()
        bottom_left = rect.bottomLeft()
        bottom_right = rect.bottomRight()
        position = event.pos()  # relative pos to window
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
        else:  # no resize
            self._resize_direction = ResizeDirection.default
            self.setCursor(Qt.ArrowCursor)

    def resizing(self, event):
        window = self.window().windowHandle()
        if self._resize_direction == ResizeDirection.top:
            window.startSystemResize(Qt.TopEdge)
        elif self._resize_direction == ResizeDirection.bottom:
            window.startSystemResize(Qt.BottomEdge)
        elif self._resize_direction == ResizeDirection.right:
            window.startSystemResize(Qt.RightEdge)
        elif self._resize_direction == ResizeDirection.left:
            window.startSystemResize(Qt.LeftEdge)
        elif self._resize_direction == ResizeDirection.top_right:
            window.startSystemResize(Qt.TopEdge | Qt.RightEdge)
        elif self._resize_direction == ResizeDirection.bottom_right:
            window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
        elif self._resize_direction == ResizeDirection.bottom_left:
            window.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
        elif self._resize_direction == ResizeDirection.top_left:
            window.startSystemResize(Qt.TopEdge | Qt.LeftEdge)

    def maximize_restore(self, a0=None):  # dummy arg to be used as an event slot
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_restore_max_button_state(self):
        if self.isMaximized():
            if self.ui.restore_max_button.icon().themeName() == "restore":
                return
            icon = QIcon(QPixmap(str(asset_path / "icons" / "restore.png")))
            icon.setThemeName("restore")
            self.ui.restore_max_button.setIcon(icon)
        else:
            if self.ui.restore_max_button.icon().themeName() == "maximize":
                return
            icon = QIcon(QPixmap(str(asset_path / "icons" / "maximize.png")))
            icon.setThemeName("maximize")
            self.ui.restore_max_button.setIcon(icon)
