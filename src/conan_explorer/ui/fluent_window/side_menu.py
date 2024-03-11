

from typing import Callable, Optional
from conan_explorer.app.logger import Logger
from conan_explorer.ui.common import ThemedWidget
from PySide6.QtWidgets import (QStackedWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
                               QPushButton, QSizePolicy, QWidget, QSpacerItem)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import QSize, Qt

from conan_explorer.ui.widgets.toggle import AnimatedToggle
from . import RIGHT_MENU_MAX_WIDTH, gen_obj_name


class SideSubMenu(ThemedWidget):

    def __init__(self, parent_stacked_widget: QStackedWidget, title: str = "", is_top_level=False):
        super().__init__(parent_stacked_widget)
        from .side_menu_ui import Ui_SideMenu  # need to resolve circular import
        self.ui = Ui_SideMenu()
        self.ui.setupUi(self)

        self.parent_stacked_widget = parent_stacked_widget
        self.parent_stacked_widget.addWidget(self)
        self.title = title
        self.is_top_level = is_top_level
        self.set_title(title)
        self._content_layout = self.ui.content_frame_layout
        self.set_themed_icon(self.ui.side_menu_title_button, "icons/back.svg")

        if is_top_level:
            self.ui.side_menu_title_button.hide()  # off per default

    def reset_widgets(self):
        while (self._content_layout.count() > 1):
            widget = self._content_layout.takeAt(0)
            if widget in [None, self.ui.side_menu_spacer]:
                continue
            self._content_layout.removeItem(widget)

    def set_title(self, title: str):
        self.ui.side_menu_title_label.setText(title)

    def enable_collapsible(self) -> bool:
        """
        Enable this side menu being collapsed. The side_menu_title_button will be used for this,
        so this must be a top level menu, otherwise the back button could not be operated anymore.
        """
        if not self.is_top_level:
            return False
        self.set_themed_icon(
            self.ui.side_menu_title_button, "icons/expand.svg")
        self.ui.side_menu_title_button.clicked.connect(
            self.on_expand_minimize)  # off per default
        return True

    def on_expand_minimize(self):
        """ The title button can be used to minimize a submenu """
        if self.ui.side_menu_content_frame.height() > 0:
            self.ui.side_menu_content_frame.setMaximumHeight(0)
            self.set_themed_icon(
                self.ui.side_menu_title_button, "icons/forward.svg")
        else:
            self.set_themed_icon(
                self.ui.side_menu_title_button, "icons/expand.svg")
            self.ui.side_menu_content_frame.setMaximumHeight(4096)

    def get_menu_entry_by_name(self, name: str) -> Optional[QWidget]:
        return self.findChild(QWidget, gen_obj_name(name))  # type:ignore

    def add_custom_menu_entry(self, widget: QWidget, name: Optional[str] = None):
        """ Very basic custom entry, no extra functions """
        if name:
            widget.setObjectName(gen_obj_name(name))
        self._content_layout.insertWidget(
            self._content_layout.count() - 1, widget)

    def add_menu_line(self):
        line = QFrame(self)
        line.setMidLineWidth(3)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.add_custom_menu_entry(line, "line")

    def add_named_custom_entry(self, name: str, widget: QWidget, asset_icon: str = "", force_v_layout=False):
        """ Creates a Frame with a text label and a custom widget under it and adds it to the menu """
        label = QLabel(text=name, parent=self)
        label.adjustSize()  # adjust layout according to size and throw a warning, if too big?
        label.setObjectName(gen_obj_name(name) + "_label")
        label.setMaximumHeight(30)
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        label.setSizePolicy(size_policy)
        icon = None
        if asset_icon:
            icon = QLabel(parent=self)
            icon.setObjectName(gen_obj_name(name) + "_icon")
            self.set_themed_icon(icon, asset_icon)
        widget.adjustSize()
        widget.setMinimumHeight(50)
        widget.setMaximumHeight(100)
        widget.setObjectName(gen_obj_name(name) + "_widget")

        frame = QFrame(self)
        if force_v_layout or label.width() > (RIGHT_MENU_MAX_WIDTH - widget.width() - 30):  # aggressive 30 px padding
            layout = QVBoxLayout(frame)
            frame.setLayout(layout)
            if icon is not None:  # in vmode the icon still needs to be placed in the 
                # same row, so we need an extra h-layout
                horizontal_layout = QHBoxLayout()
                horizontal_layout.addWidget(icon)
                horizontal_layout.addWidget(label)
                horizontal_layout.addSpacerItem(QSpacerItem(
                    40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
                layout.addLayout(horizontal_layout)
                layout.setStretch(1, 1)
            else:
                layout.addWidget(label)
        else:
            layout = QHBoxLayout(frame)
            frame.setLayout(layout)
            if icon is not None:
                layout.addWidget(icon)
            layout.addWidget(label)
            layout.setStretch(1, 1)

        if label.width() > RIGHT_MENU_MAX_WIDTH:
            Logger().debug(f"{str(name)} right side menu exceeds max width!")
        frame.layout().setContentsMargins(5, 0, 5, 0)
        frame.layout().setSpacing(4)

        frame.layout().addWidget(widget)
        self.add_custom_menu_entry(frame, name)

    def add_toggle_menu_entry(self, name: str, target: Callable, initial_state: bool, asset_icon: str = ""):
        toggle = AnimatedToggle(self)
        toggle.setChecked(initial_state)
        toggle.stateChanged.connect(target)
        self.add_named_custom_entry(name, toggle, asset_icon, force_v_layout=True)
        return toggle

    def add_sub_menu(self, sub_menu: "SideSubMenu", asset_icon: str = ""):
        button = self.add_button_menu_entry(
            sub_menu.title, sub_menu.ui.side_menu_title_button.show, asset_icon)
        button.clicked.connect(
            lambda: self.parent_stacked_widget.setCurrentWidget(sub_menu))
        sub_menu.ui.side_menu_title_button.clicked.connect(
            lambda: self.parent_stacked_widget.setCurrentWidget(self))
        sub_menu.setObjectName(gen_obj_name(sub_menu.title) + "_widget")
        return button

    def add_button_menu_entry(self, name: str, target: Callable, asset_icon: str = "",
                              shortcut: Optional[QKeySequence] = None, shortcut_parent: Optional[QWidget] = None):
        """ Adds a button with an icon and links with a callable. Optionally can have a key shortcut. """
        button = QPushButton(self)
        button.setMinimumSize(QSize(64, 50))
        button.setMaximumHeight(50)
        if asset_icon:
            self.set_themed_icon(button, asset_icon)
        button.setText(name)
        button.setStyleSheet("text-align:left")
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
        shortcut_obj.setContext(Qt.ShortcutContext.ApplicationShortcut)

        return button
