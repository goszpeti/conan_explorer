import platform
from conan_app_launcher.settings import GUI_STYLE_FLUENT, GUI_STYLE_MATERIAL

from conan_app_launcher.ui.common.theming import ThemedWidget
from conan_app_launcher.ui.fluent_window import LEFT_MENU_MAX_WIDTH, LEFT_MENU_MIN_WIDTH, RIGHT_MENU_MAX_WIDTH, RIGHT_MENU_MIN_WIDTH, gen_obj_name

if platform.system() == "Windows":
    import ctypes
    from ctypes.wintypes import MSG

from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, TypeVar


# uses Logger, settings and theming related functions
from conan_app_launcher import AUTOCLOSE_SIDE_MENU
from conan_app_launcher.core.system import is_windows_11

from PySide6.QtCore import (QEasingCurve, QEvent, QObject, QPoint,
                            QPropertyAnimation, QRect, QSize, Qt)
from PySide6.QtGui import QHoverEvent, QMouseEvent
from PySide6.QtWidgets import (QMainWindow,
                               QPushButton, QSizePolicy, QWidget)

from ..common import get_themed_asset_icon
from .side_menu import SideSubMenu

if TYPE_CHECKING:
    from ..plugin.plugins import PluginInterfaceV1

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

        def get_side_menu_by_type(self, type_name: Type) -> "Optional[SideSubMenu]":
            for _, (_, page, menu, _) in self._page_widgets.items():
                if isinstance(page, type_name):
                    return menu
            raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

        def get_button_by_type(self, type_name: Type) -> QPushButton:
            for _, (button, page, _, _) in self._page_widgets.items():
                if isinstance(page, type_name):
                    return button
            raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

        T = TypeVar('T')

        def get_page_by_type(self, type_name: Type[T]) -> T:
            for _, (_, page, _, _), in self._page_widgets.items():
                if page.__class__.__name__ == type_name.__name__:
                    return page  # type: ignore
            raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

        def get_all_buttons(self):
            buttons = []
            for button, _, _, _ in self._page_widgets.values():
                buttons.append(button)
            return buttons

        def get_all_pages(self) -> List["PluginInterfaceV1"]:
            pages = []
            for _, (_, page, _, _), in self._page_widgets.items():
                pages.append(page)
            return pages

        def add_new_page(self, name: str, button, page, right_sub_menu):
            self._page_widgets[gen_obj_name(name)] = (button, page, right_sub_menu, name)

        def remove_page_by_name(self, name: str):
            button, widget, menu, _ = self._page_widgets[gen_obj_name(name)]
            button.hide()
            widget.hide()
            button.deleteLater()
            widget.deleteLater()
            if menu:
                menu.deleteLater()

    def __init__(self, title_text: str = "", native_windows_fcns=True):
        QMainWindow.__init__(self)
        ThemedWidget.__init__(self, None)
        from .fluent_window_ui import Ui_MainWindow  # need to resolve circular import
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.main_general_settings_menu = SideSubMenu(
            self.ui.right_menu_bottom_content_sw, "General Settings", True)
        self.ui.right_menu_bottom_content_sw.addWidget(self.main_general_settings_menu)
        self.ui.right_menu_bottom_content_sw.setCurrentWidget(self.main_general_settings_menu)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint | # type: ignore
                            Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)
        if is_windows_11() or platform.system() == "Linux":  # To hide black edges around the border rounding
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._use_native_windows_fcns = True if platform.system() == "Windows" and native_windows_fcns else False
        # all buttons and widgets to be able to shown on the main page (from settings and left menu)
        self.page_widgets = FluentWindow.PageStore()

        # resize related variables
        self._resize_press = 0
        self._resize_direction = ResizeDirection.default
        self._resize_point = QPoint()
        self._last_geometry = QRect()
        self.title_text = title_text
        self.drag_position: Optional[QPoint] = None

        self.ui.left_menu_frame.setMinimumWidth(LEFT_MENU_MIN_WIDTH)
        self.ui.left_menu_frame.setMaximumWidth(LEFT_MENU_MIN_WIDTH)
        menu_margins = self.ui.left_menu_bottom_subframe.layout().contentsMargins()
        button_offset = menu_margins.right() + menu_margins.left()
        # fix buttons sizes, so they don't expand on togglling the menu
        self.ui.toggle_left_menu_button.setMinimumWidth(LEFT_MENU_MIN_WIDTH - button_offset)
        self.ui.toggle_left_menu_button.setMaximumWidth(LEFT_MENU_MIN_WIDTH - button_offset)

        self.ui.settings_button.setFixedWidth(LEFT_MENU_MIN_WIDTH - button_offset)

        self.set_themed_icon(self.ui.toggle_left_menu_button, "icons/menu_stripes.svg")
        self.set_themed_icon(self.ui.settings_button, "icons/settings.svg")

        self.set_themed_icon(self.ui.minimize_button, "icons/minus.svg")
        self.set_themed_icon(self.ui.close_button, "icons/close.svg")
        from ..common.theming import get_gui_style
        style = get_gui_style()
        if style == GUI_STYLE_FLUENT:
            self.ui.close_button.setIconSize(QSize(16, 16))

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
        # self.ui.page_info_label.setText("")
        self.ui.title_label.setText("")

        # initial maximize state
        self.set_restore_max_button_state()
        self.enable_windows_native_animations()

    def nativeEvent(self, eventType, message):  # override
        """ Platform native events """
        retval = QMainWindow.nativeEvent(self, eventType, message)
        if str(eventType) == "b'windows_generic_MSG'":
            # message.setsize(8)
            msg = MSG.from_address(message.__int__())
            if msg.message == 131:  # ignore WM_NCCALCSIZE event. Suppresses native Window drawing of title-bar.
                return True, 0
        return retval, 0

    def mousePressEvent(self, event: QMouseEvent):  # override
        """ Helper for moving window to know mouse position (Non Windows) """
        self.drag_position = event.globalPosition().toPoint()

    def apply_theme(self):
        """ This function must be able to reload all icons from the left and right menu bar. """
        self.reload_themed_icons()
        self.set_restore_max_button_state(force=True)
        for submenu in self.ui.right_menu_bottom_content_sw.findChildren(SideSubMenu):
            submenu.reload_themed_icons()  # type: ignore
        for submenu in self.ui.right_menu_top_content_sw.findChildren(SideSubMenu):
            submenu.reload_themed_icons()  # type: ignore

    def move_window(self, event: QMouseEvent):
        # do nothing if the resize function is active
        if self.cursor().shape() != Qt.CursorShape.ArrowCursor:
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
            if event.buttons() == Qt.MouseButton.LeftButton:
                if self.drag_position is None:
                    return
                self.move(self.pos() + event.globalPosition().toPoint() - self.drag_position)  # type: ignore
                self.drag_position = event.globalPosition().toPoint()
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
                                            style | WS_BORDER | WS_THICKFRAME | WS_MAXIMIZEBOX | CS_DBLCLKS | WS_CAPTION)

    def add_left_menu_entry(self, name: str, asset_icon: str, is_upper_menu: bool, page_widget: QWidget, create_page_menu=False):
        button = QPushButton("", self.ui.left_menu_frame)
        self.set_themed_icon(button, asset_icon)
        button.setObjectName(gen_obj_name(name))
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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

        # update page settings view
        side_menu = self.page_widgets.get_side_menu_by_name(obj_name)
        if not side_menu:
            self.ui.right_menu_top_content_sw.hide()
        else:
            self.ui.right_menu_top_content_sw.show()
            self.ui.right_menu_top_content_sw.setCurrentWidget(side_menu)
        if AUTOCLOSE_SIDE_MENU:
            if self.ui.settings_button.isChecked():
                self.toggle_right_menu()

    def toggle_left_menu(self):
        width = self.ui.left_menu_frame.width()

        # switch extended and minimized state
        if width < LEFT_MENU_MAX_WIDTH:
            width_to_set = LEFT_MENU_MAX_WIDTH
            maximize = True
        else:
            width_to_set = LEFT_MENU_MIN_WIDTH
            maximize = False

        self.left_anim = QPropertyAnimation(self.ui.left_menu_frame, b"minimumWidth")  # type: ignore
        self.left_anim.setDuration(400)
        self.left_anim.setStartValue(width)
        self.left_anim.setEndValue(width_to_set)
        self.left_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.left_anim.start()

        # hide title
        if maximize:
            self.ui.title_label.setText(self.title_text)
        else:
            self.ui.title_label.setText("")

        # hide menu button texts
        # name, (button, _) in self.page_entries.items():
        for button in self.ui.left_menu_middle_subframe.findChildren(QPushButton):
            if not isinstance(button, QPushButton):
                return
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
        if width < RIGHT_MENU_MAX_WIDTH:
            width_to_set = RIGHT_MENU_MAX_WIDTH
        else:
            width_to_set = RIGHT_MENU_MIN_WIDTH
            self.ui.settings_button.setChecked(False)
        self.right_anim = QPropertyAnimation(self.ui.right_menu_frame, b"minimumWidth")  # type: ignore
        self.right_anim.setDuration(400)
        self.right_anim.setStartValue(width)
        self.right_anim.setEndValue(width_to_set)
        self.right_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.right_anim.start()

    def eventFilter(self, source: QObject, event: QEvent):  # override
        """ Implements window resizing """
        self.set_restore_max_button_state()
        if self.isMaximized():  # no resize when maximized
            return super().eventFilter(source, event)
        if isinstance(event, QHoverEvent):  # Use isinstance instead of type because of typehinting
            if event.type() == event.Type.HoverMove and self._resize_press == 0:
                self.handle_resize_cursor(event)  # cursor position control for cursor shape setup
        elif isinstance(event, QMouseEvent):
            if event.type() == event.Type.MouseButtonPress:
                if event.button() != Qt.MouseButton.LeftButton:
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
        position = event.position().toPoint()  # relative pos to window
        width = self.width()
        height = self.height()

        if QRect(top_left.x() + x_offset, top_left.y(), width - 2*x_offset, y_offset).contains(position):
            self._resize_direction = ResizeDirection.top
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif QRect(bottom_left.x() + x_offset, bottom_left.y(), width - 2*x_offset, -y_offset).contains(position):
            self._resize_direction = ResizeDirection.bottom
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif QRect(top_right.x() - x_offset, top_right.y() + y_offset, x_offset, height - 2*y_offset).contains(position):
            self._resize_direction = ResizeDirection.right
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif QRect(top_left.x() + x_offset, top_left.y() + y_offset, -x_offset, height - 2*y_offset).contains(position):
            self._resize_direction = ResizeDirection.left
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif QRect(top_right.x(), top_right.y(), -x_offset, y_offset).contains(position):
            self._resize_direction = ResizeDirection.top_right
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif QRect(bottom_left.x(), bottom_left.y(), x_offset, -y_offset).contains(position):
            self._resize_direction = ResizeDirection.bottom_left
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif QRect(top_left.x(), top_left.y(), x_offset, y_offset).contains(position):
            self._resize_direction = ResizeDirection.top_left
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif QRect(bottom_right.x(), bottom_right.y(), -x_offset, -y_offset).contains(position):
            self._resize_direction = ResizeDirection.bottom_right
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:  # no resize
            self._resize_direction = ResizeDirection.default
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def resizing(self, event):
        window = self.window().windowHandle()
        if self._resize_direction == ResizeDirection.top:
            window.startSystemResize(Qt.Edge.TopEdge)
        elif self._resize_direction == ResizeDirection.bottom:
            window.startSystemResize(Qt.Edge.BottomEdge)
        elif self._resize_direction == ResizeDirection.right:
            window.startSystemResize(Qt.Edge.RightEdge)
        elif self._resize_direction == ResizeDirection.left:
            window.startSystemResize(Qt.Edge.LeftEdge)
        elif self._resize_direction == ResizeDirection.top_right:
            window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.RightEdge)
        elif self._resize_direction == ResizeDirection.bottom_right:
            window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.RightEdge)
        elif self._resize_direction == ResizeDirection.bottom_left:
            window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.LeftEdge)
        elif self._resize_direction == ResizeDirection.top_left:
            window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.LeftEdge)

    def maximize_restore(self, event=None):  # dummy arg to be used as an event slot
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_restore_max_button_state(self, force=False):
        if self.isMaximized():
            if self.ui.restore_max_button.icon().themeName() == "restore" and not force:
                return
            icon = get_themed_asset_icon("icons/restore.svg")
            icon.setThemeName("restore")
            self.ui.restore_max_button.setIcon(icon)
        else:
            if self.ui.restore_max_button.icon().themeName() == "maximize" and not force:
                return
            icon = get_themed_asset_icon("icons/maximize.svg")
            icon.setThemeName("maximize")
            self.ui.restore_max_button.setIcon(icon)
