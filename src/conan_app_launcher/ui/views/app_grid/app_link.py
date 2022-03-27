
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import ICON_SIZE, asset_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core import open_in_file_manager, run_file
from conan_app_launcher.settings import (APPLIST_ENABLED, DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS,
                                         ENABLE_APP_COMBO_BOXES)
from conan_app_launcher.ui.common import get_themed_asset_image
from conan_app_launcher.ui.views.app_grid.model import UiAppLinkModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QComboBox, QDialog, QFrame, QHBoxLayout,
                             QLabel, QLayout, QMenu, QMessageBox, QSizePolicy, QPushButton,
                             QSpacerItem, QVBoxLayout)

from .dialogs import AppEditDialog, AppsMoveDialog, ClickableIcon

if TYPE_CHECKING:  # pragma: no cover
    from.tab import TabGrid

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"

current_dir = Path(__file__).parent


class AppLink(QFrame):
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
    - Rearrange App Links
    """
    icon_size: int

    def __init__(self, parent: "QWidget", parent_tab: "TabGrid", model: UiAppLinkModel, icon_size=ICON_SIZE):
        super().__init__(parent)
        self._app_list_enabled = app.active_settings.get_bool(APPLIST_ENABLED)
        self.setLayout(QHBoxLayout(self) if self._app_list_enabled else QVBoxLayout(self))
        self.setObjectName(repr(self))
        self.icon_size = icon_size
        self.model = model
        self._parent_tab = parent_tab  # save parent - don't use qt signals ands slots
        self._lock_cboxes = False  # lock combo boxes to ignore changes of conanref
        self._combo_boxes_enabled = app.active_settings.get_bool(ENABLE_APP_COMBO_BOXES)
        self._init_app_link()

    @staticmethod
    def max_width() -> int:
        """ Max width depending on cbox (needed for tab to precalculate full width) """
        enable_combo_boxes = app.active_settings.get_bool(ENABLE_APP_COMBO_BOXES)
        max_width = 150
        if enable_combo_boxes:
            max_width = 190
        return max_width

    def _init_app_link(self):
        """ Initialize all subwidgets with default values. """
        max_width = self.max_width()
        self.layout().setSpacing(3)

        if self._app_list_enabled:
            max_width = 150
            self.setMinimumHeight(100)
            self.setMaximumHeight(100)

            size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                      QSizePolicy.Fixed)
            self._left_frame = QFrame(self)
            self._center_frame = QFrame(self)
            self._center_right_frame = QFrame(self)
            self._right_frame = QFrame(self)


            self._left_frame.setLayout(QVBoxLayout(self))
            self._center_frame.setLayout(QVBoxLayout(self))
            self._center_right_frame.setLayout(QVBoxLayout(self))
            self._right_frame.setLayout(QVBoxLayout(self))

            self._left_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
            self._center_frame.layout().setSizeConstraint(QLayout.SetMinimumSize)
            self._center_right_frame.layout().setSizeConstraint(QLayout.SetMinimumSize)
            self._right_frame.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
    
            self._left_frame.setMaximumWidth(max_width)
            self._left_frame.setMinimumWidth(max_width)
            #self._left_frame.layout().setAlignment(Qt.AlignCenter)
            self._left_frame.layout().setContentsMargins(0,0,0,5)
            self._right_frame.setMinimumWidth(200)
            self._right_frame.setMaximumWidth(150)
            self._center_frame.setMinimumWidth(200)

            self._app_button = ClickableIcon(self._left_frame, asset_path / "icons" / "app.png")
            self._app_name_label = QLabel(self)
            self._left_frame.layout().addWidget(self._app_button)
            self._app_button.setMinimumWidth(max_width)
            self._app_button.setMaximumWidth(max_width)
            self._app_name_label.setMinimumWidth(200)
            self._app_name_label.setWordWrap(True)
            self._app_name_label.setAlignment(Qt.AlignLeft)

            self._app_version_cbox = QLabel(self._center_frame)
            self._app_user_cbox = QLabel(self._center_frame)
            self._app_channel_cbox = QLabel(self._center_frame)
            self._center_frame.layout().addWidget(self._app_name_label)

            self._center_right_frame.layout().addWidget(self._app_version_cbox)
            self._center_right_frame.layout().addWidget(self._app_user_cbox)
            self._center_right_frame.layout().addWidget(self._app_channel_cbox)
            self._app_version_cbox.setSizePolicy(size_policy)
            self._app_user_cbox.setSizePolicy(size_policy)
            self._app_channel_cbox.setSizePolicy(size_policy)

            self._edit_button = QPushButton("Edit", self)
            self._remove_button = QPushButton("Remove", self)
            self._edit_button.setIcon(QIcon(get_themed_asset_image("icons/edit.png")))
            self._remove_button.setIcon(QIcon(get_themed_asset_image("icons/delete.png")))
            self._edit_button.setMinimumWidth(150)
            self._edit_button.setMaximumWidth(150)
            self._remove_button.setMinimumWidth(150)
            self._remove_button.setMaximumWidth(150)

            self._right_frame.layout().addWidget(self._edit_button)
            self._right_frame.layout().addWidget(self._remove_button)
            self.layout().addWidget(self._left_frame)
            self.layout().addWidget(self._center_frame)
            self.layout().addWidget(self._center_right_frame)
            self.layout().addWidget(self._right_frame)

        else:
            self.setMaximumWidth(max_width)
            size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.Expanding)
            self._app_button = ClickableIcon(self, asset_path / "icons" / "app.png")
            self._app_name_label = QLabel(self)

            if self._combo_boxes_enabled:
                self._app_version_cbox = QComboBox(self)
                self._app_user_cbox = QComboBox(self)
                self._app_channel_cbox = QComboBox(self)
            else:
                self._app_version_cbox = QLabel(self)
                self._app_user_cbox = QLabel(self)
                self._app_channel_cbox = QLabel(self)
                self._app_version_cbox.setAlignment(Qt.AlignHCenter)
                self._app_user_cbox.setAlignment(Qt.AlignHCenter)
                self._app_channel_cbox.setAlignment(Qt.AlignHCenter)
            self.layout().addWidget(self._app_button)
            self.layout().addWidget(self._app_name_label)
            self.layout().addWidget(self._app_version_cbox)
            self.layout().addWidget(self._app_user_cbox)
            self.layout().addWidget(self._app_channel_cbox)
            self._app_name_label.setMaximumWidth(max_width)

            self._app_version_cbox.setMaximumWidth(max_width
            )

            self._app_user_cbox.setMaximumWidth(max_width)

        self.setSizePolicy(size_policy)

        # add sub widgets

        self._app_button.setSizePolicy(size_policy)
        self._app_button.setMinimumHeight(self.icon_size + 10)
        self._app_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self._app_button.customContextMenuRequested.connect(self.on_context_menu_requested)

        self._app_name_label.setAlignment(Qt.AlignCenter)
        self._app_name_label.setSizePolicy(size_policy)
        self._app_name_label.setWordWrap(True)

        if self._combo_boxes_enabled:
            self._app_version_cbox.setDisabled(True)
            self._app_version_cbox.setDuplicatesEnabled(False)
        self._app_version_cbox.setSizePolicy(size_policy)
        self._app_version_cbox.setAlignment(Qt.AlignCenter)


        if self._combo_boxes_enabled:
            self._app_user_cbox.setDisabled(True)
            self._app_user_cbox.setDuplicatesEnabled(False)
        self._app_user_cbox.setAlignment(Qt.AlignCenter)

        self._app_user_cbox.setSizePolicy(size_policy)

        if self._combo_boxes_enabled:
            self._app_channel_cbox.setDisabled(True)
            self._app_channel_cbox.setDuplicatesEnabled(False)
        self._app_channel_cbox.setSizePolicy(size_policy)
        self._app_channel_cbox.setAlignment(Qt.AlignCenter)

        # connect signals
        self._app_button.clicked.connect(self.on_click)
        if self._combo_boxes_enabled:
            self._app_version_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)
            self._app_user_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)
            self._app_channel_cbox.currentIndexChanged.connect(self.on_ref_cbox_selected)

        if self._app_list_enabled:
            self._edit_button.clicked.connect(self.open_edit_dialog)
            self._remove_button.clicked.connect(self.remove)

        self._init_context_menu()

    def _init_context_menu(self):
        """ Setup context menu. """
        self.menu = QMenu()

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

        self.rearrange_action = QAction("Rearrange App Links", self)
        self.rearrange_action.setIcon(QIcon(get_themed_asset_image("icons/rearrange.png")))
        self.rearrange_action.triggered.connect(self.on_move)

        self.menu.addAction(self.rearrange_action)

    def load(self):
        self.model.register_update_callback(self.update_with_conan_info)
        self._apply_new_config()

    def on_move(self):
        move_dialog = AppsMoveDialog(parent=self, tab_ui_model=self.model.parent)
        ret = move_dialog.exec()
        if ret == QDialog.Accepted:
            self._parent_tab.remove_all_app_links()
            self._parent_tab.load_apps_from_model()

    def delete(self):
        self._app_name_label.close()
        self._app_version_cbox.close()
        self._app_user_cbox.close()
        self._app_channel_cbox.close()
        self._app_button.close()

    def on_context_menu_requested(self, position):
        self.menu.exec_(self._app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        split_name = self.model.name.split(" ")
        name = ""
        for word in split_name:
            if len(word) > 24:
                word = word[:24] + " " + word[24:-1]

            name += " " + word if name else word
        self._app_name_label.setWordWrap(True)
        self._app_name_label.setText(name)
        self._app_name_label.setText(name)
        self._app_button.setToolTip(self.model.conan_ref)
        self._app_button.set_icon(self.model.get_icon())

        if self._combo_boxes_enabled:
            self._lock_cboxes = True
            self._app_channel_cbox.clear()
            self._app_channel_cbox.addItem(self.model.channel)
            self._app_version_cbox.clear()
            self._app_version_cbox.addItem(self.model.version)
            self._app_user_cbox.clear()
            self._app_user_cbox.addItem(self.model.user)
            self._lock_cboxes = False
        else:
            self._app_channel_cbox.setText(self.model.channel)
            self._app_version_cbox.setText(self.model.version)
            self._app_user_cbox.setText(self.model.user)

        self.update_versions_info_visible()
        self.update_users_info_visible()
        self.update_channels_info_visible()

        self.update_with_conan_info()  # initial update with offline information


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
        message_box.setText(f"Are you sure, you want to delete the link \"{self.model.name}?\"")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setIcon(QMessageBox.Question)
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            self.hide() # TODO call extra function
            self.model.parent.apps.remove(self.model)
            self._parent_tab.app_links.remove(self)

            self.model.save()
            self._parent_tab.redraw_grid(force=True)


    def update_with_conan_info(self):
        """ Update combo boxes with new conan data """
        self.update_icon()

        if not self._combo_boxes_enabled:  # set text instead
            self._app_version_cbox.setText(self.model.version)
            self._app_user_cbox.setText(self.model.user)
            self._app_channel_cbox.setText(self.model.channel)
            return
        if self._lock_cboxes == True:
            return

        if self._app_channel_cbox.itemText(0) != self.model.INVALID_DESCR and \
                len(self.model.versions) > 1 and self._app_version_cbox.count() < len(self.model.versions) or \
                len(self.model.channels) > 1 and self._app_channel_cbox.count() < len(self.model.channels):
            # signals the cbox callback that we do not set new user values
            self._lock_cboxes = True
            self._app_version_cbox.clear()
            self._app_user_cbox.clear()
            self._app_channel_cbox.clear()

            self._app_version_cbox.addItems(self.model.versions)
            self._app_user_cbox.addItems(self.model.users)
            self._app_channel_cbox.addItems(self.model.channels)
            try:  # try to set updated values
                self._app_version_cbox.setCurrentIndex(
                    self.model.versions.index(self.model.version))
                self._app_user_cbox.setCurrentIndex(
                    self.model.users.index(self.model.user))
                self._app_channel_cbox.setCurrentIndex(
                    self.model.channels.index(self.model.channel))
            except Exception:
                pass
            # on first show
            self._app_version_cbox.setEnabled(True)
            self._app_user_cbox.setEnabled(True)
            self._app_channel_cbox.setEnabled(True)

            self._lock_cboxes = False

        # add tooltip for channels, in case it is too long
        for i in range(0, len(self.model.channels)):
            self._app_channel_cbox.setItemData(i, self.model.channels[i], Qt.ToolTipRole)

    def update_icon(self):
        if self.model.get_executable_path().is_file():
            self._app_button.set_icon(self.model.get_icon())
            self._app_button.ungrey_icon()

    def update_versions_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_VERSIONS):
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.setHidden(True)

    def update_users_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_USERS):
            self._app_user_cbox.show()
        else:
            self._app_user_cbox.setHidden(True)

    def update_channels_info_visible(self):
        if app.active_settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.setHidden(True)

    def on_click(self):
        """ Callback for opening the executable on click """
        if not self.model.get_executable_path().is_file():
            Logger().error(
                f"Can't find file in package {self.model.conan_ref}:\n    {str(self.model.get_executable_path())}")
        run_file(self.model.get_executable_path(), self.model.is_console_application, self.model.args)

    def on_ref_cbox_selected(self, index: int):
        """ Update combo boxes """
        if self._lock_cboxes:
            return
        if index == -1:  # on clear
            return
        self._lock_cboxes = True
        re_eval_channel = False
        self._app_button.grey_icon()
        if self.model.version != self._app_version_cbox.currentText():
            self.model.lock_changes = True
            self.model.version = self._app_version_cbox.currentText()
            self.model.user = self.model.INVALID_DESCR  # invalidate, must be evaluated again for new version
        if self.model.user != self._app_user_cbox.currentText():
            self.model.lock_changes = True
            if self.model.user == self.model.INVALID_DESCR:
                self.model.update_from_cache()
                # update user to match version
                self._app_user_cbox.clear()  # reset cbox
                users = self.model.users
                if not users:
                    users = self.model.INVALID_DESCR
                self._app_user_cbox.addItems(users)
            re_eval_channel = True  # re-eval channel. can't use INVALID_DESCR, since it is also a valid user choice
            self.model.user = self._app_user_cbox.currentText()
        if self.model.channel != self._app_channel_cbox.currentText() or re_eval_channel:
            self.model.lock_changes = True
            if re_eval_channel:
                self.model.channel = self.model.INVALID_DESCR  # eval for channels
                # update channels to match version
                self._app_channel_cbox.clear()  # reset cbox
                self._app_channel_cbox.addItems(self.model.channels)
                # add tooltip for channels, in case it is too long
                for i in range(0, len(self.model.channels)):
                    self._app_channel_cbox.setItemData(i+1, self.model.channels[i], Qt.ToolTipRole)
                self._app_channel_cbox.setCurrentIndex(0)
            else:
                # remove entry NA after setting something other - NA should always have index 0
                if self._app_channel_cbox.itemText(0) == self.model.INVALID_DESCR:
                    self._app_channel_cbox.removeItem(0)
                # normal switch
                self.model.lock_changes = False
                self.model.channel = self._app_channel_cbox.currentText()
                self._app_button.setToolTip(self.model.conan_ref)
                self._app_button.set_icon(self.model.get_icon())
                # self.model.trigger_conan_update()
                self._app_button.setToolTip(self.model.conan_ref)
        self.update_icon()
        self.model.save()
        self.model.lock_changes = False
        self._lock_cboxes = False
