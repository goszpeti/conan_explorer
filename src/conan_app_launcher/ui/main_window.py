from pathlib import Path
from shutil import rmtree
from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import PathLike, user_save_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core.conan import ConanCleanup
from conan_app_launcher.settings import (APPLIST_ENABLED, DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS, FONT_SIZE,
                                         GUI_STYLE, GUI_STYLE_DARK,
                                         GUI_STYLE_LIGHT, LAST_CONFIG_FILE)
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from .common import QLoader, activate_theme
from .views.about_page import AboutPage
from .fluent_window import FluentWindow
from .model import UiApplicationModel
from .views import AppGridView, ConanSearchDialog, LocalConanPackageExplorer

class MainWindow(FluentWindow):
    """ Instantiates MainWindow and holds all UI objects """

    # signals for inter page communication
    conan_pkg_installed = pyqtSignal(str, str)  # conan_ref, pkg_id
    conan_pkg_removed = pyqtSignal(str, str)  # conan_ref, pkg_ids

    display_versions_changed = pyqtSignal()
    display_channels_changed = pyqtSignal()
    display_users_changed = pyqtSignal()

    log_console_message = pyqtSignal(str)  # str arg is the message

    def __init__(self, qt_app: QApplication):
        super().__init__("Conan App Launcher")
        self._qt_app = qt_app
        self.model = UiApplicationModel(self.conan_pkg_installed, self.conan_pkg_removed)


        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self.log_console_message)
        self.log_console_message.connect(self.write_log)

        self.about_page = AboutPage(self)
        self.app_grid = AppGridView(self, self.model.app_grid, self.conan_pkg_installed, self.page_widgets)
        self.local_package_explorer = LocalConanPackageExplorer(self, self.conan_pkg_removed, self.page_widgets)
        self.search_dialog = ConanSearchDialog(self, self.conan_pkg_installed,
                                               self.conan_pkg_removed, self.page_widgets)

        self._init_left_menu()
        self._init_right_menu()


    def _init_left_menu(self):
        self.add_left_menu_entry("Conan Quicklaunch", "icons/grid.png", True, self.app_grid)
        self.add_left_menu_entry("Local Package Explorer", "icons/package.png", True, self.local_package_explorer)
        self.add_left_menu_entry("Conan Search", "icons/search_packages.png", True, self.search_dialog)

        # set default page
        self.page_widgets.get_button_by_name("Conan Quicklaunch").click()


    def _init_right_menu(self):

        # Right Settings menu
        quicklaunch_submenu = self.RightSubMenu("Quicklaunch")
        quicklaunch_submenu.add_button_menu_entry(
            "Open Layout File", self.open_config_file_dialog, "icons/opened_folder.png")
        quicklaunch_submenu.add_toggle_menu_entry(
            "Use Grid for AppLinks", self.quicklaunch_grid_mode_toggled, app.active_settings.get_bool(APPLIST_ENABLED))

        quicklaunch_submenu.add_toggle_menu_entry(
            "Display versions for AppLinks", self.display_versions_setting_toggled, app.active_settings.get_bool(DISPLAY_APP_VERSIONS))
        quicklaunch_submenu.add_toggle_menu_entry(
            "Display users for AppLinks", self.apply_display_users_setting_toggled, app.active_settings.get_bool(DISPLAY_APP_USERS))
        quicklaunch_submenu.add_toggle_menu_entry(
            "Display channels for AppLinks", self.display_channels_setting_toggled, app.active_settings.get_bool(DISPLAY_APP_CHANNELS))

        self.add_right_menu_sub_menu(quicklaunch_submenu, "icons/grid.png")
        self.add_right_menu_line()

        view_settings_submenu = self.RightSubMenu("View")
        self.add_right_menu_sub_menu(view_settings_submenu, "icons/package_settings.png")

        view_settings_submenu.add_button_menu_entry(
            "Font Size +", self.on_font_size_increased, "icons/increase_font.png", QKeySequence(Qt.CTRL + Qt.Key_Plus))
        view_settings_submenu.add_button_menu_entry(
            "Font Size - ", self.on_font_size_decreased, "icons/decrease_font.png", QKeySequence(Qt.CTRL + Qt.Key_Minus))

        dark_mode_enabled = True if app.active_settings.get_string(GUI_STYLE) == GUI_STYLE_DARK else False
        view_settings_submenu.add_toggle_menu_entry("Dark Mode", self.on_theme_changed, dark_mode_enabled)

        conan_settings_submenu = self.RightSubMenu("Conan")
        conan_button = self.add_right_menu_sub_menu(conan_settings_submenu)
        conan_button.setIcon(QIcon(str(app.asset_path / "icons/conan.png")))

        self.add_right_menu_line()
        self.add_right_menu_entry("Remove Locks", "icons/remove-lock.png").clicked.connect(app.conan_api.remove_locks)
        self.add_right_menu_entry("Clean Conan Cache", "icons/cleanup").clicked.connect(self.open_cleanup_cache_dialog)
        self.add_right_menu_line()
        self.add_right_bottom_menu_main_page_entry("About", self.about_page, "icons/about.png")

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        try:
            self.log_console_message.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()
        super().closeEvent(event)

    def resizeEvent(self, a0) -> None:  # QtGui.QResizeEvent
        super().resizeEvent(a0)

        if APPLIST_ENABLED:  # no redraw necessary
            return
        if a0.oldSize().width() == -1:  # initial resize - can be skipped
            return
        self.app_grid.re_init_all_app_links()

    def load(self, config_source: Optional[PathLike] = None):
        """ Load all application gui elements specified in the GUI config (file) """
        config_source_str = str(config_source)
        if not config_source:
            config_source_str = app.active_settings.get_string(LAST_CONFIG_FILE)

        # model loads incrementally
        loader = QLoader(self)
        loader.async_loading(self, self.model.loadf, (config_source_str,))
        loader.wait_for_finished()

        # model loaded, now load the gui elements, which have a static model
        self.app_grid.re_init(self.model.app_grid)

        # TODO: Other modules are currently loaded on demand. A window and view restoration would be nice and
        # should be called from here

    @pyqtSlot()
    def on_font_size_increased(self):
        """ Increase font size by 2. Ignore if font gets too large. """
        new_size = app.active_settings.get_int(FONT_SIZE) + 1
        if new_size > 14:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    @pyqtSlot()
    def on_font_size_decreased(self):
        """ Decrease font size by 2. Ignore if font gets too small. """
        new_size = app.active_settings.get_int(FONT_SIZE) - 1
        if new_size < 8:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    @pyqtSlot()
    def on_theme_changed(self):
        # wait 0,5 seconds, so all animations can finish
        import datetime
        start = datetime.datetime.now()
        while not datetime.datetime.now() - start > datetime.timedelta(milliseconds=600):
            QApplication.processEvents()

        dark_mode_enabled = True if app.active_settings.get_string(GUI_STYLE) == GUI_STYLE_DARK else False
        if not dark_mode_enabled:
            app.active_settings.set(GUI_STYLE, GUI_STYLE_DARK)
        else:
            app.active_settings.set(GUI_STYLE, GUI_STYLE_LIGHT)

        activate_theme(self._qt_app)

        # all icons must be reloaded
        self.apply_theme()
        self.local_package_explorer.apply_theme()
        self.app_grid.re_init(self.model.app_grid)  # needs a whole reload because models need to be reinitialized
        if self.search_dialog:
            self.search_dialog.apply_theme()

    @ pyqtSlot()
    def open_cleanup_cache_dialog(self):
        """ Open the message box to confirm deletion of invalid cache folders """
        paths = ConanCleanup(app.conan_api).get_cleanup_cache_paths()
        if not paths:
            self.write_log("INFO: Nothing found in cache to clean up.")
            return
        if len(paths) > 1:
            path_list = "\n".join(paths)
        else:
            path_list = paths[0]

        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Delete folders")
        msg.setText("Are you sure, you want to delete the found folders?\t")
        msg.setDetailedText(path_list)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setIcon(QMessageBox.Question)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            for path in paths:
                rmtree(str(path), ignore_errors=True)

    @pyqtSlot()
    def open_config_file_dialog(self):
        """" Open File Dialog and load config file """
        dialog_path = user_save_path
        config_file_path = Path(app.active_settings.get_string(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QFileDialog(parent=self, caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QFileDialog.Accepted:
            new_file = dialog.selectedFiles()[0]
            app.active_settings.set(LAST_CONFIG_FILE, new_file)
            # model loads incrementally
            self.model.loadf(new_file)

            # conan works, model can be loaded
            self.app_grid.re_init(self.model.app_grid)  # loads tabs

    @pyqtSlot()
    def display_versions_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        # status is changed only after this is done, so the state must be negated
        sender_toggle = self.sender()
        status = sender_toggle.isChecked()
        app.active_settings.set(DISPLAY_APP_VERSIONS, status)
        self.app_grid.re_init_all_app_links(force=True)

    @pyqtSlot()
    def apply_display_users_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        sender_toggle = self.sender()
        status = sender_toggle.isChecked()
        app.active_settings.set(DISPLAY_APP_USERS, status)
        self.app_grid.re_init_all_app_links(force=True)

    @pyqtSlot()
    def display_channels_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        sender_toggle = self.sender()
        status = sender_toggle.isChecked()
        app.active_settings.set(DISPLAY_APP_CHANNELS, status)
        self.app_grid.re_init_all_app_links(force=True)

    @pyqtSlot()
    def quicklaunch_grid_mode_toggled(self):
        sender_toggle = self.sender()
        status = not sender_toggle.isChecked()
        app.active_settings.set(APPLIST_ENABLED, status)
        self.app_grid.re_init(self.model.app_grid)

    @pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)


