
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import ICON_SIZE, asset_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core import open_in_file_manager, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS)
from conan_app_launcher.ui.common import get_themed_asset_icon, measure_font_width
from conan_app_launcher.ui.dialogs.reorder_dialog.reorder_dialog import ReorderDialog
from conan_app_launcher.ui.views.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.widgets import ClickableIcon, RoundedMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QLayout,
                               QMessageBox, QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from .dialogs import AppEditDialog

if TYPE_CHECKING:
    from .tab import TabList, TabList  # TabGrid

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"

current_dir = Path(__file__).parent


class ListAppLink(QFrame):
    """ Represents a clickable button + info for an executable in a conan package.
    |- Button with Icon (clickable to start executable)
    |- Package version(s)
    |- Package user(s)
    |- Package channel(s)
    |- Vertical Spacer (to enforce vertical size)
    Hovering shows the Conan reference.
    Rightclick context menu has the following elements:
    - Show in File Manager
    - Add new App Link
    - Edit
    - Remove App Link
    - Reorder App Links
    """
    icon_size: int
    MAX_WIDTH = 150
    MAX_HEIGHT = 150

    def __init__(self, parent: Optional[QWidget], parent_tab: "TabList", model: UiAppLinkModel, icon_size=ICON_SIZE):
        super().__init__(parent)
        self.setObjectName(repr(self))
        self.icon_size = icon_size
        self.model = model
        self._parent_tab = parent_tab  # save parent - don't use qt signals ands slots

        self.setLayout(QHBoxLayout(self))
        self.layout().setSpacing(3)
        self.setMinimumHeight(self.MAX_HEIGHT)
        self.setMaximumHeight(self.MAX_HEIGHT)

        size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(size_policy)

        self._left_frame = QFrame(self)  # contains the app button
        self._center_frame = QFrame(self)  # contains the name
        self._center_right_frame = QFrame(self)  # contains data vertically
        self._right_frame = QFrame(self)  # buttons

        self._left_frame.setLayout(QVBoxLayout(self._left_frame))
        self._center_frame.setLayout(QVBoxLayout(self._center_frame))
        self._center_right_frame.setLayout(QVBoxLayout(self._center_right_frame))
        self._right_frame.setLayout(QVBoxLayout(self._right_frame))

        self._left_frame.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self._center_frame.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self._center_right_frame.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self._right_frame.layout().setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

        self._left_frame.setMaximumWidth(self.max_width())
        self._left_frame.setMinimumWidth(self.max_width())
        self._left_frame.layout().setContentsMargins(0, 0, 0, 5)
        self._center_frame.setMinimumWidth(200)

        self._right_frame.setMinimumWidth(200)
        self._right_frame.setMaximumWidth(200)

        self._app_button = ClickableIcon(self, asset_path / "icons" / "no-access.png")
        self._left_frame.layout().addWidget(self._app_button)

        self._app_name = QLabel(self._left_frame)
        self._app_version = QLabel(self._center_frame)
        self._app_user = QLabel(self._center_frame)
        self._app_channel = QLabel(self._center_frame)
        self._app_version.setMinimumWidth(100)

        self._center_frame.layout().addWidget(self._app_name)

        self._center_right_frame.layout().addWidget(self._app_version)
        self._center_right_frame.layout().addWidget(self._app_user)
        self._center_right_frame.layout().addWidget(self._app_channel)

        self._app_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._app_user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._app_channel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._app_name.setMinimumWidth(2*self.max_width())
        self._app_button.setMinimumWidth(self.max_width())
        self._app_button.setMaximumWidth(self.max_width())

        self._edit_button = QPushButton("Edit ", self)
        self._remove_button = QPushButton("Remove ", self)
        self._edit_button.setIcon(QIcon(get_themed_asset_icon("icons/edit.png")))
        self._remove_button.setIcon(QIcon(get_themed_asset_icon("icons/delete.png")))
        self._edit_button.setMinimumWidth(200)
        self._edit_button.setMaximumWidth(200)
        self._remove_button.setMinimumWidth(200)
        self._remove_button.setMaximumWidth(200)

        self._right_frame.layout().addWidget(self._edit_button)
        self._right_frame.layout().addWidget(self._remove_button)
        self.layout().addWidget(self._left_frame)
        self.layout().addWidget(self._center_frame)
        self.layout().addWidget(self._center_right_frame)
        self.layout().addWidget(self._right_frame)
        self.layout().setStretch(1, 1)  # enables stretching of app_name

        self._app_name.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding,
                                                 QSizePolicy.Policy.Fixed))

        self._app_version.setSizePolicy(size_policy)
        self._app_user.setSizePolicy(size_policy)
        self._app_channel.setSizePolicy(size_policy)

        self._left_frame.setSizePolicy(size_policy)
        self._center_frame.setSizePolicy(size_policy)
        self._center_right_frame.setSizePolicy(size_policy)
        self._right_frame.setSizePolicy(size_policy)

        self._edit_button.clicked.connect(self.open_edit_dialog)
        self._remove_button.clicked.connect(self.remove)
        self._app_name.setWordWrap(True)

        # add sub widgets
        self._app_button.setMinimumHeight(self.icon_size + 10)
        self._app_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._app_button.customContextMenuRequested.connect(self.on_context_menu_requested)

        # connect signals
        self._app_button.clicked.connect(self.on_click)
        self._init_context_menu()

    @classmethod
    def max_width(cls) -> int:
        return cls.MAX_WIDTH

    def _init_context_menu(self):
        """ Setup context menu. """
        self.menu = RoundedMenu()
        self.open_fm_action = QAction("Show in File Manager", self)
        self.open_fm_action.setIcon(QIcon(get_themed_asset_icon("icons/file_explorer.png")))
        self.menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.menu.addSeparator()

        self.add_action = QAction("Add new App Link", self)
        self.add_action.setIcon(QIcon(get_themed_asset_icon("icons/add_link.png")))
        self.menu.addAction(self.add_action)
        self.add_action.triggered.connect(self.open_app_link_add_dialog)

        self.edit_action = QAction("Edit", self)
        self.edit_action.setIcon(QIcon(get_themed_asset_icon("icons/edit.png")))
        self.menu.addAction(self.edit_action)
        self.edit_action.triggered.connect(self.open_edit_dialog)

        self.remove_action = QAction("Remove App Link", self)
        self.remove_action.setIcon(QIcon(get_themed_asset_icon("icons/delete.png")))
        self.menu.addAction(self.remove_action)
        self.remove_action.triggered.connect(self.remove)

        self.menu.addSeparator()

        self.reorder_action = QAction("Reorder App Links", self)
        self.reorder_action.setIcon(QIcon(get_themed_asset_icon("icons/rearrange.png")))
        self.reorder_action.triggered.connect(self.on_move)

        self.menu.addAction(self.reorder_action)

    def load(self):
        self.model.register_update_callback(self.apply_conan_info)
        self._apply_new_config()

    def on_move(self):
        move_dialog = ReorderDialog(parent=self, model=self.model.parent)
        ret = move_dialog.exec()
        if ret == QDialog.DialogCode.Accepted:
            self._parent_tab.redraw(force=True)

    def delete(self):
        self._app_name.close()
        self._app_version.close()
        self._app_user.close()
        self._app_channel.close()
        self._app_button.close()

    def resizeEvent(self, event):
        self.split_name_into_lines()
        super().resizeEvent(event)

    def split_name_into_lines(self):
        """ Calculate, how text can be split into multiple lines, based on the current width"""
        max_width = self._app_name.width()
        px = measure_font_width(self._app_name.text())
        new_length = int(len(self.model.name) * (max_width-10) / px)
        if len(self._app_name.text().split("\n")[0]) > new_length > len(self.model.name) or \
                new_length-1 == len(self._app_name.text().split("\n")[0]):
            return
        name = self.word_wrap(self.model.name, new_length)
        self._app_name.setText(name)

    @staticmethod
    def word_wrap(text: str, max_length: int) -> str:
        split_name = text.split(" ")
        name = ""  # split long titles
        for word in split_name:
            if len(word) < max_length:
                new_word = word
            else:
                n_to_short = int(len(word) / max_length) + int(len(word) % max_length > 0)
                new_word = ""
                for i in range(n_to_short):
                    new_word += word[max_length*i:max_length*(i+1)] + "\n"
                new_word = new_word[:-1]  # remove last \n
            name += " " + new_word if name else new_word
        return name

    def on_context_menu_requested(self, position):
        self.menu.exec(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        self._app_name.setText(self.model.name)
        self._app_button.setToolTip(self.model.conan_ref)
        self._app_button.set_icon(self.model.get_icon())
        self.update_versions_info_visible()
        # self.update_users_info_visible()
        # self.update_channels_info_visible()

        self.apply_conan_info()  # update with offline information

    def open_app_link_add_dialog(self):
        self._parent_tab.open_app_link_add_dialog()

    def open_edit_dialog(self, model: Optional[UiAppLinkModel] = None):
        if model:
            self.model = model
        edit_app_dialog = AppEditDialog(self.model, parent=self)
        reply = edit_app_dialog.exec()
        if reply == AppEditDialog.DialogCode.Accepted:
            # grey icon, so update from cache can ungrey it, if the path is correct
            self._app_button.grey_icon()
            self.model.load_from_cache()
            # now apply gui config with resolved paths
            self._apply_new_config()
        del edit_app_dialog  # call delete manually for faster thread cleanup

    def remove(self):
        # last link can't be deleted!
        if len(self.model.parent.apps) == 1:
            msg = QMessageBox(parent=self)  # self._parent_tab
            msg.setWindowTitle("Info")
            msg.setText("Can't delete the last link!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            return

        # confirmation dialog
        message_box = QMessageBox(parent=self)  # self.parentWidget())
        message_box.setWindowTitle("Delete app link")
        message_box.setText(f"Are you sure, you want to delete the link \"{self.model.name}\"?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            self.model.parent.apps.remove(self.model)
            self._parent_tab.app_links.remove(self)

            self.model.save()
            self._parent_tab.redraw(force=True)

    def update_icon(self):
        self._app_button.set_icon(self.model.get_icon())
        self._app_button.ungrey_icon()

    def update_versions_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_VERSIONS):
            self._app_version.show()
        else:
            self._app_version.setHidden(True)

    def update_users_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_USERS):
            self._app_user.show()
        else:
            self._app_user.setHidden(True)

    def update_channels_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel.show()
        else:
            self._app_channel.setHidden(True)

    def on_click(self):
        """ Callback for opening the executable on click """
        if not self.model.get_executable_path().is_file():
            Logger().error(
                f"Can't find file in package {self.model.conan_ref}:\n    {str(self.model._executable)}")
        run_file(self.model.get_executable_path(), self.model.is_console_application, self.model.args)

    def apply_conan_info(self):
        """ Update with new conan data """
        self.update_icon()
        self._app_version.setText(self.model.conan_ref)
        self._app_user.setText(str(self.model.package_folder))
        self._app_channel.setText(str(self.model.conan_options))
