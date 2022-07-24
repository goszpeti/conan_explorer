
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import ICON_SIZE, asset_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core import open_in_file_manager, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS,
                                         ENABLE_APP_COMBO_BOXES, FONT_SIZE)
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.dialogs.reorder_dialog.reorder_dialog import ReorderDialog
from conan_app_launcher.ui.views.app_grid.model import UiAppLinkModel
from conan_app_launcher.ui.widgets import ClickableIcon, RoundedMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFontMetrics, QFont
from PyQt5.QtWidgets import (QAction, QComboBox, QDialog, QFrame, QHBoxLayout,
                             QLabel, QLayout, QMessageBox, QPushButton,
                             QSizePolicy, QVBoxLayout, QWidget)

from .dialogs import AppEditDialog
from abc import ABC

if TYPE_CHECKING:  # pragma: no cover
    from.tab import TabBase, TabGrid, TabList

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"

current_dir = Path(__file__).parent


class AppLinkBase(QFrame):
    """ Represents a clickable button + info or combo box for an executable in a conan package.
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
    _max_width = 175

    def __init__(self, parent: Optional[QWidget], parent_tab: "TabBase", model: UiAppLinkModel, icon_size=ICON_SIZE):
        super().__init__(parent)
        self.setObjectName(repr(self))
        self.icon_size = icon_size
        self.model = model
        self._parent_tab = parent_tab  # save parent - don't use qt signals ands slots

        self._app_button: ClickableIcon
        self._app_name: QLabel
        self._app_version: QWidget
        self._app_user: QWidget
        self._app_channel: QWidget

    @classmethod
    def max_width(cls) -> int:
        return cls._max_width

    def _init_app_link(self):
        """ Initialize all subwidgets with default values. """
        self._app_name.setWordWrap(True)

        # add sub widgets
        self._app_button.setMinimumHeight(self.icon_size + 10)
        self._app_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self._app_button.customContextMenuRequested.connect(self.on_context_menu_requested)

        # connect signals
        self._app_button.clicked.connect(self.on_click)
        self._init_context_menu()


    def _init_context_menu(self):
        """ Setup context menu. """
        self.menu = RoundedMenu()
        self.open_fm_action = QAction("Show in File Manager", self)
        self.open_fm_action.setIcon(QIcon(get_themed_asset_image("icons/file-explorer.png")))
        self.menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.menu.addSeparator()

        self.add_action = QAction("Add new App Link", self)
        self.add_action.setIcon(QIcon(get_themed_asset_image("icons/add_link.png")))
        self.menu.addAction(self.add_action)
        self.add_action.triggered.connect(self.open_app_link_add_dialog)

        self.edit_action = QAction("Edit", self)
        self.edit_action.setIcon(QIcon(get_themed_asset_image("icons/edit.png")))
        self.menu.addAction(self.edit_action)
        self.edit_action.triggered.connect(self.open_edit_dialog)

        self.remove_action = QAction("Remove App Link", self)
        self.remove_action.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
        self.menu.addAction(self.remove_action)
        self.remove_action.triggered.connect(self.remove)

        self.menu.addSeparator()

        self.reorder_action = QAction("Reorder App Links", self)
        self.reorder_action.setIcon(QIcon(get_themed_asset_image("icons/rearrange.png")))
        self.reorder_action.triggered.connect(self.on_move)

        self.menu.addAction(self.reorder_action)

    def load(self):
        self.model.register_update_callback(self.update_conan_info)
        self._apply_new_config()

    def on_move(self):
        move_dialog = ReorderDialog(parent=self, model=self.model.parent)
        ret = move_dialog.exec()
        if ret == QDialog.Accepted:
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
        fs = app.active_settings.get_int(FONT_SIZE)
        font = QFont()
        font.setPointSize(fs)
        fm = QFontMetrics(font)
        px = fm.horizontalAdvance(self._app_name.text())
        new_length = int(len(self.model.name) * (max_width-10) / px)
        if len(self._app_name.text().split("\n")[0]) > new_length > len(self.model.name) or \
               new_length-1 == len(self._app_name.text().split("\n")[0]):
            return
        name = self.word_wrap(self.model.name, new_length)
        self._app_name.setText(name)

    @staticmethod
    def word_wrap(text:str, max_length:int) -> str:
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
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        self._app_name.setText(self.model.name)
        self._app_button.setToolTip(self.model.conan_ref)
        self._app_button.set_icon(self.model.get_icon())
        self.update_versions_info_visible()
        self.update_users_info_visible()
        self.update_channels_info_visible()

        self.update_conan_info()  # initial update with offline information

    def open_app_link_add_dialog(self):
        self._parent_tab.open_app_link_add_dialog()

    def open_edit_dialog(self, model: Optional[UiAppLinkModel] = None):
        if model:
            self.model = model
        edit_app_dialog = AppEditDialog(self.model, parent=self)
        reply = edit_app_dialog.exec_()
        if reply == AppEditDialog.Accepted:
            # grey icon, so update from cache can ungrey it, if the path is correct
            self._app_button.grey_icon()
            self.model.update_from_cache()
            # now apply gui config with resolved paths
            self._apply_new_config()
        del edit_app_dialog  # call delete manually for faster thread cleanup

    def remove(self):
        # last link can't be deleted!
        if len(self.model.parent.apps) == 1:
            msg = QMessageBox(parent=self)  # self._parent_tab
            msg.setWindowTitle("Info")
            msg.setText("Can't delete the last link!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            return

        # confirmation dialog
        message_box = QMessageBox(parent=self) # self.parentWidget())
        message_box.setWindowTitle("Delete app link")
        message_box.setText(f"Are you sure, you want to delete the link \"{self.model.name}\"?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setIcon(QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            self.hide()
            self.model.parent.apps.remove(self.model)
            self._parent_tab.app_links.remove(self)

            self.model.save()
            self._parent_tab.redraw(force=True)

    def update_conan_info(self):
        """ Update with new conan data """
        pass
      
    def update_icon(self):
        if self.model.get_executable_path().is_file():
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
                f"Can't find file in package {self.model.conan_ref}:\n    {str(self.model.get_executable_path())}")
        run_file(self.model.get_executable_path(), self.model.is_console_application, self.model.args)

class ListAppLink(AppLinkBase):
    _max_width = 130


    def __init__(self, parent: Optional[QWidget], parent_tab: "TabList", model: UiAppLinkModel, icon_size=ICON_SIZE, ):
        super().__init__(parent, parent_tab, model, icon_size)
        self.setLayout(QHBoxLayout(self))
        self._init_app_link()

    def _init_app_link(self):
        self.layout().setSpacing(3)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)

        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)

        self._left_frame = QFrame(self)
        self._center_frame = QFrame(self)
        self._center_right_frame = QFrame(self)
        self._right_frame = QFrame(self)

        self._left_frame.setLayout(QVBoxLayout(self._left_frame))
        self._center_frame.setLayout(QVBoxLayout(self._center_frame))
        self._center_right_frame.setLayout(QVBoxLayout(self._center_right_frame))
        self._right_frame.setLayout(QVBoxLayout(self._right_frame))

        self._left_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._center_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._center_right_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._right_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

        self._left_frame.setMaximumWidth(self.max_width())
        self._left_frame.setMinimumWidth(self.max_width())
        self._left_frame.layout().setContentsMargins(0, 0, 0, 5)
        self._center_frame.setMinimumWidth(200)

        self._right_frame.setMinimumWidth(200)
        self._right_frame.setMaximumWidth(200)

        self._app_button = ClickableIcon(self, asset_path / "icons" / "app.png")
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

        self._app_name.setAlignment(Qt.AlignLeft)
        self._app_version.setAlignment(Qt.AlignCenter)
        self._app_user.setAlignment(Qt.AlignCenter)
        self._app_channel.setAlignment(Qt.AlignCenter)

        self._app_name.setMinimumWidth(2*self.max_width())
        self._app_button.setMinimumWidth(self.max_width())
        self._app_button.setMaximumWidth(self.max_width())

        self._edit_button = QPushButton("Edit ", self)
        self._remove_button = QPushButton("Remove ", self)
        self._edit_button.setIcon(QIcon(get_themed_asset_image("icons/edit.png")))
        self._remove_button.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
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
        self.layout().setStretch(1,1) # enbales stretching of app_name

        self._app_name.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                         QSizePolicy.Fixed))

        self._app_version.setSizePolicy(size_policy)
        self._app_user.setSizePolicy(size_policy)
        self._app_channel.setSizePolicy(size_policy)

        self._left_frame.setSizePolicy(size_policy)
        self._center_frame.setSizePolicy(size_policy)
        self._center_right_frame.setSizePolicy(size_policy)
        self._right_frame.setSizePolicy(size_policy)

        self._edit_button.clicked.connect(self.open_edit_dialog)
        self._remove_button.clicked.connect(self.remove)
        super()._init_app_link()


    def update_conan_info(self):
        """ Update with new conan data """ # TODO should be in model!
        self.update_icon()
        self._app_version.setText(self.model.version)
        self._app_user.setText(self.model.user)
        self._app_channel.setText(self.model.channel)


class GridAppLink(AppLinkBase):
    _max_width = 200


    def __init__(self, parent: Optional[QWidget], parent_tab: "TabGrid", model: UiAppLinkModel, icon_size=ICON_SIZE):
        super().__init__(parent, parent_tab, model, icon_size)
        self.setLayout(QVBoxLayout(self))
        self._lock_cboxes = False  # lock combo boxes to ignore changes of conanref
        self._combo_boxes_enabled = app.active_settings.get_bool(ENABLE_APP_COMBO_BOXES)
        self._init_app_link()

    def _init_app_link(self):
        self.layout().setSpacing(3)
        self.setMaximumWidth(self.max_width())
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.Expanding)
        self._app_button = ClickableIcon(self, asset_path / "icons" / "app.png")  # _left_frame
        self._app_name = QLabel(self)
        if self._combo_boxes_enabled:
            self._app_version = QComboBox(self)
            self._app_user = QComboBox(self)
            self._app_channel = QComboBox(self)
        else:
            self._app_version = QLabel(self)
            self._app_user = QLabel(self)
            self._app_channel = QLabel(self)
            self._app_version.setAlignment(Qt.AlignHCenter)
            self._app_user.setAlignment(Qt.AlignHCenter)
            self._app_channel.setAlignment(Qt.AlignHCenter)
        self._app_name.setAlignment(Qt.AlignHCenter)

        self.layout().addWidget(self._app_button)
        self.layout().addWidget(self._app_name)
        self.layout().addWidget(self._app_version)
        self.layout().addWidget(self._app_user)
        self.layout().addWidget(self._app_channel)
        self._app_name.setMaximumWidth(self.max_width())
        self._app_version.setMaximumWidth(self.max_width())
        self._app_user.setMaximumWidth(self.max_width())
        self.setSizePolicy(size_policy)

        self._app_button.setSizePolicy(size_policy)
        self._app_name.setSizePolicy(size_policy)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.Fixed)
        self._app_version.setSizePolicy(size_policy)
        self._app_user.setSizePolicy(size_policy)
        self._app_channel.setSizePolicy(size_policy)

        if self._combo_boxes_enabled:
            self._app_version.currentIndexChanged.connect(self.on_ref_cbox_selected)
            self._app_user.currentIndexChanged.connect(self.on_ref_cbox_selected)
            self._app_channel.currentIndexChanged.connect(self.on_ref_cbox_selected)
        super()._init_app_link()

    def _apply_new_config(self):
        if self._combo_boxes_enabled:
            self._lock_cboxes = True
            self._app_channel.clear()
            self._app_channel.addItem(self.model.channel)
            self._app_version.clear()
            self._app_version.addItem(self.model.version)
            self._app_user.clear()
            self._app_user.addItem(self.model.user)
            self._lock_cboxes = False
        else:
            self._app_channel.setText(self.model.channel)
            self._app_version.setText(self.model.version)
            self._app_user.setText(self.model.user)
        super()._apply_new_config()

    @classmethod
    def max_width(cls) -> int:
        """ Max width depending on cbox (needed for tab to precalculate full width) """
        enable_combo_boxes = app.active_settings.get_bool(ENABLE_APP_COMBO_BOXES)
        max_width = cls._max_width
        if enable_combo_boxes:
            max_width += 50
        return max_width

    def on_ref_cbox_selected(self, index: int):
        """ Update combo boxes """
        if self._lock_cboxes:
            return
        if index == -1:  # on clear
            return
        self._lock_cboxes = True
        re_eval_channel = False
        self._app_button.grey_icon()
        if self.model.version != self._app_version.currentText():
            self.model.lock_changes = True
            self.model.version = self._app_version.currentText()
            self.model.user = self.model.INVALID_DESCR  # invalidate, must be evaluated again for new version
        if self.model.user != self._app_user.currentText():
            self.model.lock_changes = True
            if self.model.user == self.model.INVALID_DESCR:
                self.model.update_from_cache()
                # update user to match version
                self._app_user.clear()  # reset cbox
                users = self.model.users
                if not users:
                    users = self.model.INVALID_DESCR
                self._app_user.addItems(users)
            re_eval_channel = True  # re-eval channel. can't use INVALID_DESCR, since it is also a valid user choice
            self.model.user = self._app_user.currentText()
        if self.model.channel != self._app_channel.currentText() or re_eval_channel:
            self.model.lock_changes = True
            if re_eval_channel:
                self.model.channel = self.model.INVALID_DESCR  # eval for channels
                # update channels to match version
                self._app_channel.clear()  # reset cbox
                self._app_channel.addItems(self.model.channels)
                # add tooltip for channels, in case it is too long
                for i in range(0, len(self.model.channels)):
                    self._app_channel.setItemData(i+1, self.model.channels[i], Qt.ToolTipRole)
                self._app_channel.setCurrentIndex(0)
            else:
                # remove entry NA after setting something other - NA should always have index 0
                if self._app_channel.itemText(0) == self.model.INVALID_DESCR:
                    self._app_channel.removeItem(0)
                # normal switch
                self.model.lock_changes = False
                self.model.channel = self._app_channel.currentText()
                self._app_button.setToolTip(self.model.conan_ref)
                self._app_button.set_icon(self.model.get_icon())
                # self.model.trigger_conan_update()
                self._app_button.setToolTip(self.model.conan_ref)
        self.update_icon()
        self.model.save()
        self.model.lock_changes = False
        self._lock_cboxes = False

    def update_conan_info(self):
        """ Update with new conan data """
        self.update_icon()

        if not self._combo_boxes_enabled:  # set text instead
            self._app_version.setText(self.model.version)
            self._app_user.setText(self.model.user)
            self._app_channel.setText(self.model.channel)
            return
        if self._lock_cboxes == True:
            return

        if self._app_channel.itemText(0) != self.model.INVALID_DESCR and \
                len(self.model.versions) > 1 and self._app_version.count() < len(self.model.versions) or \
                len(self.model.channels) > 1 and self._app_channel.count() < len(self.model.channels):
            # signals the cbox callback that we do not set new user values
            self._lock_cboxes = True
            self._app_version.clear()
            self._app_user.clear()
            self._app_channel.clear()

            self._app_version.addItems(self.model.versions)
            self._app_user.addItems(self.model.users)
            self._app_channel.addItems(self.model.channels)
            try:  # try to set updated values
                self._app_version.setCurrentIndex(
                    self.model.versions.index(self.model.version))
                self._app_user.setCurrentIndex(
                    self.model.users.index(self.model.user))
                self._app_channel.setCurrentIndex(
                    self.model.channels.index(self.model.channel))
            except Exception:
                pass
            # on first show
            self._app_version.setEnabled(True)
            self._app_user.setEnabled(True)
            self._app_channel.setEnabled(True)

            self._lock_cboxes = False

        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.model.channels)):
            self._app_channel.setItemData(i, self.model.channels[i], Qt.ToolTipRole)
