
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QDialog, QFrame, QMessageBox, QWidget)

from conan_explorer import ICON_SIZE, INVALID_PATH
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import open_in_file_manager, run_file
from conan_explorer.ui.common import get_themed_asset_icon, measure_font_width
from conan_explorer.ui.dialogs.reorder_dialog import ReorderDialog
from conan_explorer.ui.widgets import RoundedMenu

from .dialogs import AppEditDialog
from .model import UiAppLinkModel

if TYPE_CHECKING:
    from .tab import TabList, TabList  # TabGrid

OFFICIAL_RELEASE_DISP_NAME = "<official release>"
OFFICIAL_USER_DISP_NAME = "<official user>"

current_dir = Path(__file__).parent


class ListAppLink(QFrame):
    """ Represents a clickable button + info for an executable in a conan package.
    Rightclick context menu has the following elements:
    - Show in File Manager
    - Add new App Link
    - Edit
    - Remove App Link
    - Reorder App Links
    """
    icon_size: int

    def __init__(self, parent: Optional[QWidget], parent_tab: "TabList",
                 model: UiAppLinkModel, icon_size=ICON_SIZE):
        super().__init__(parent)
        self.setObjectName(repr(self))
        self.icon_size = icon_size
        self.model = model
        self._parent_tab = parent_tab  # save parent - don't use qt signals ands slots

        from .app_link_ui import Ui_Form
        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._ui.edit_button.setIcon(
            QIcon(get_themed_asset_icon("icons/edit.svg")))
        self._ui.remove_button.setIcon(
            QIcon(get_themed_asset_icon("icons/delete.svg")))
        self._ui.app_button.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._ui.app_button.customContextMenuRequested.connect(
            self.on_context_menu_requested)

        # connect signals
        self._ui.app_button.clicked.connect(self.on_click)
        self._ui.edit_button.clicked.connect(self.open_edit_dialog)
        self._ui.remove_button.clicked.connect(self.remove)
        self._init_context_menu()

    def _init_context_menu(self):
        """ Setup context menu. """
        self.menu = RoundedMenu()
        self.open_fm_action = QAction("Show in File Manager", self)
        self.open_fm_action.setIcon(
            QIcon(get_themed_asset_icon("icons/file_explorer.svg")))
        self.menu.addAction(self.open_fm_action)
        self.open_fm_action.triggered.connect(self.on_open_in_file_manager)

        self.menu.addSeparator()

        self.add_action = QAction("Add new App Link", self)
        self.add_action.setIcon(
            QIcon(get_themed_asset_icon("icons/add_link.svg")))
        self.menu.addAction(self.add_action)
        self.add_action.triggered.connect(self.open_app_link_add_dialog)

        self.edit_action = QAction("Edit", self)
        self.edit_action.setIcon(
            QIcon(get_themed_asset_icon("icons/edit.svg")))
        self.menu.addAction(self.edit_action)
        self.edit_action.triggered.connect(self.open_edit_dialog)

        self.remove_action = QAction("Remove App Link", self)
        self.remove_action.setIcon(
            QIcon(get_themed_asset_icon("icons/delete.svg")))
        self.menu.addAction(self.remove_action)
        self.remove_action.triggered.connect(self.remove)

        self.menu.addSeparator()

        self.reorder_action = QAction("Reorder App Links", self)
        self.reorder_action.setIcon(
            QIcon(get_themed_asset_icon("icons/rearrange.svg")))
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

    def resizeEvent(self, event):
        if not self._parent_tab:
            return
        content_frame: QWidget = self._parent_tab.parent(
        ).parent().parent().parent().parent()  # type: ignore
        max_cl_width = content_frame.width() - self._ui.left_frame.width() - \
            self._ui.right_frame.width()
        if max_cl_width < 400:  # TODO find better solution
            self._ui.central_left_frame.setMaximumWidth(0)
            self._ui.central_right_frame.setMaximumWidth(0)
            self._ui.arguments_name_label.setMaximumWidth(0)
            self._ui.arguments_value_label.setMaximumWidth(0)
            self._ui.arguments_value_label.setText("")
            return
        else:
            self._ui.central_left_frame.setMaximumWidth(10000)

        self._ui.central_left_frame.adjustSize()
        max_sum_width = content_frame.width() - self._ui.left_frame.width() - \
            self._ui.central_left_frame.width() - self._ui.right_frame.width()

        # Hide arguments, if too big
        if max_sum_width < 250:
            self._ui.central_right_frame.setMaximumWidth(0)
            self._ui.arguments_name_label.setMaximumWidth(0)
            self._ui.arguments_value_label.setMaximumWidth(0)
            self._ui.arguments_value_label.setText("")

        else:
            self._ui.central_right_frame.setMaximumWidth(max_sum_width)
            self._ui.arguments_name_label.setMaximumWidth(1000)
            self._ui.arguments_name_label.adjustSize()
            self._ui.arguments_value_label.setMaximumWidth(
                max_sum_width - self._ui.arguments_name_label.width() - 50)
            self.split_into_lines(self._ui.arguments_value_label, self.model.args,
                                  max_sum_width - self._ui.arguments_name_label.width())

        super().resizeEvent(event)

    def delete(self):  # TODO needed?
        pass

    def split_into_lines(self, widget, model_value, max_width):
        """ Calculate, how text can be split into multiple lines, based on the current width"""
        px = measure_font_width(model_value)
        if px == 0:
            return
        new_length = int(len(model_value) * (max_width-10) / px)
        if len(widget.text().split("\n")[0]) > new_length > len(model_value) or \
                new_length-1 == len(widget.text().split("\n")[0]):
            return
        args = self.word_wrap(model_value, new_length)
        widget.setText(args)

    @staticmethod
    def word_wrap(text: str, max_length: int) -> str:
        if max_length == 0:
            return text
        split_name = text.split(" ")
        name = ""  # split long titles
        for word in split_name:
            if len(word) < max_length:
                new_word = word
            else:
                n_to_short = int(len(word) / max_length) + \
                    int(len(word) % max_length > 0)
                new_word = ""
                for i in range(n_to_short):
                    new_word += word[max_length*i:max_length*(i+1)] + "\n"
                new_word = new_word[:-1]  # remove last \n
            name += " " + new_word if name else new_word
        return name

    def on_context_menu_requested(self, position):
        self.menu.exec(self._ui.app_button.mapToGlobal(position))

    def on_open_in_file_manager(self):
        open_in_file_manager(self.model.get_executable_path().parent)

    def _apply_new_config(self):
        self._ui.app_name_label.setText(self.model.name)
        self._ui.conan_ref_value_label.setText(self.model.conan_ref)
        self._ui.app_button.set_icon(self.model.get_icon())
        self._ui.executable_value_label.setText(self.model.executable)
        self._ui.arguments_value_label.setText(self.model.args)
        self._ui.open_shell_checkbox.setChecked(
            self.model.is_console_application)

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
            self._ui.app_button.grey_icon()
            self.model.load_from_cache()
            # now apply gui config with resolved paths
            self._apply_new_config()
        del edit_app_dialog  # call delete manually for faster thread cleanup

    def remove(self):
        # confirmation dialog
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Delete app link")
        message_box.setText(
            f"Are you sure, you want to delete the link \"{self.model.name}\"?")
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setIcon(QMessageBox.Icon.Question)
        reply = message_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            self.model.parent.apps.remove(self.model)
            self._parent_tab.app_links.remove(self)

            self.model.save()
            self._parent_tab.redraw(force=True)

    def update_icon(self):
        self._ui.app_button.set_icon(self.model.get_icon())
        if self.model.get_executable_path() != Path(INVALID_PATH):
            self._ui.app_button.ungrey_icon()

    def on_click(self):
        """ Callback for opening the executable on click """
        if not self.model.get_executable_path().is_file():
            Logger().error(("Can't find file in package " 
                            f"{self.model.conan_ref}:\n    {str(self.model._executable)}"))
        run_file(self.model.get_executable_path(),
                 self.model.is_console_application, self.model.args)

    def apply_conan_info(self):
        """ Update with new conan data """
        self.update_icon()
