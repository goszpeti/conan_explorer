import ctypes
from ctypes.wintypes import MSG
from pathlib import Path
from shutil import rmtree
from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import (ADD_APP_LINK_BUTTON, ADD_TAB_BUTTON, APPLIST_ENABLED, PathLike,
                                user_save_path)
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core.conan import ConanCleanup
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_USERS,
                                         DISPLAY_APP_VERSIONS, FONT_SIZE,
                                         GUI_STYLE, GUI_STYLE_DARK,
                                         GUI_STYLE_LIGHT, LAST_CONFIG_FILE)
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QFrame, QHBoxLayout, QLabel

from .common import QLoader, activate_theme, get_themed_asset_image
from .views.about_page import AboutPage
from .fluent_window import FluentWindow
from .model import UiApplicationModel
from .views import AppGridView, ConanSearchDialog, LocalConanPackageExplorer
from .widgets.toggle import AnimatedToggle

class MainWindow(FluentWindow):
    """ Instantiates MainWindow and holds all UI objects """
    conan_pkg_installed = pyqtSignal(str, str)  # conan_ref, pkg_id
    conan_pkg_removed = pyqtSignal(str, str)  # conan_ref, pkg_id

    display_versions_changed = pyqtSignal()
    display_channels_changed = pyqtSignal()
    display_users_changed = pyqtSignal()

    log_console_message = pyqtSignal(str)  # str arg is the message

    def __init__(self, qt_app: QApplication):
        super().__init__("Conan App Launcher")
        self._qt_app = qt_app
        self.model = UiApplicationModel(self.conan_pkg_installed, self.conan_pkg_removed)

        self._about_dialog = AboutPage(self)
        self.load_icons()
        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self.log_console_message)
        self.log_console_message.connect(self.write_log)

        self.app_grid = AppGridView(self, self.model.app_grid)
        self.local_package_explorer = LocalConanPackageExplorer(self)
        self.search_dialog: Optional[ConanSearchDialog] = ConanSearchDialog(self, self)

        # initialize view user settings
        # self.ui.menu_toggle_display_versions.setChecked(app.active_settings.get_bool(DISPLAY_APP_VERSIONS))
        # self.ui.menu_toggle_display_users.setChecked(app.active_settings.get_bool(DISPLAY_APP_USERS))
        # self.ui.menu_toggle_display_channels.setChecked(app.active_settings.get_bool(DISPLAY_APP_CHANNELS))
        # self.ui.menu_enable_dark_mode.setChecked(dark_mode_enabled)

        # self.ui.menu_about_action.triggered.connect(self._about_dialog.show)
        # self.ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        # self.ui.menu_search_in_remotes.triggered.connect(self.open_conan_search_dialog)
        # self.ui.menu_search_in_remotes.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F))
        # self.ui.menu_toggle_display_versions.triggered.connect(self.display_versions_setting_toggled)
        # self.ui.menu_toggle_display_users.triggered.connect(self.apply_display_users_setting_toggled)
        # self.ui.menu_toggle_display_channels.triggered.connect(self.display_channels_setting_toggled)
        # self.ui.menu_enable_dark_mode.triggered.connect(self.on_theme_changed)
        # self.ui.menu_increase_font_size.triggered.connect(self.on_font_size_increased)
        # self.ui.menu_increase_font_size.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus))
        # self.ui.menu_decrease_font_size.triggered.connect(self.on_font_size_decreased)
        # self.ui.menu_decrease_font_size.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus))

        # self.ui.menu_cleanup_cache.triggered.connect(self.open_cleanup_cache_dialog)
        # self.ui.menu_remove_locks.triggered.connect(app.conan_api.remove_locks)
        
        # self.ui.main_toolbox.currentChanged.connect(self.on_main_view_changed)
        icon = QIcon()
        icon.addPixmap(QPixmap(get_themed_asset_image("icons/grid.png")),
                        QIcon.Normal, QIcon.Off)
        self.add_left_menu_entry("Conan Quicklaunch", icon, True, self.app_grid)
        icon = QIcon()
        icon.addPixmap(QPixmap(get_themed_asset_image("icons/opened_folder.png")),
                               QIcon.Normal, QIcon.Off)
        self.add_left_menu_entry("Local Package Explorer", icon, True, self.local_package_explorer)
        icon.addPixmap(QPixmap(get_themed_asset_image("icons/search_packages.png")),
                       QIcon.Normal, QIcon.Off)
        self.add_left_menu_entry("Conan Search", icon, True, self.search_dialog)

        # set default page
        self.page_entries["Conan Quicklaunch"][0].click()

        view_settings_submenu = self.RightSubMenu("View Settings")
        self.add_right_bottom_menu_sub_menu("View", view_settings_submenu, QIcon(
            get_themed_asset_image("icons/package_Settings.png")))

        view_settings_submenu.add_button_menu_entry(
            "Font Size +", self.on_font_size_increased, QIcon(
                get_themed_asset_image("icons/increase_font.png")), QKeySequence(Qt.CTRL + Qt.Key_Plus))
        view_settings_submenu.add_button_menu_entry(
            "Font Size - ", self.on_font_size_decreased, QIcon(
                get_themed_asset_image("icons/decrease_font.png")), QKeySequence(Qt.CTRL + Qt.Key_Minus))

        s_frame = QFrame(self)
        s_frame.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        dark_mode_toggle = AnimatedToggle(self)
        dark_mode_toggle.setMinimumSize(70, 40)
        dark_mode_toggle.setMaximumSize(70, 40)
        s_frame.layout().addWidget(QLabel("Dark mode"))
        s_frame.layout().addWidget(dark_mode_toggle)

        #self.on_theme_changed
        view_settings_submenu.add_custom_menu_entry(s_frame)
        # dark_mode_enabled = True if app.active_settings.get_string(GUI_STYLE) == GUI_STYLE_DARK else False

        self.add_right_bottom_menu_main_page_entry(
            "About", self._about_dialog, QIcon(get_themed_asset_image("icons/about.png")))

        # menu
        # self.ui.menu_cleanup_cache.setIcon(QIcon(get_themed_asset_image("icons/cleanup.png")))
        # self.ui.menu_remove_locks.setIcon(QIcon(get_themed_asset_image("icons/remove-lock.png")))
        # self.ui.menu_increase_font_size.setIcon(QIcon(get_themed_asset_image("icons/increase_font.png")))
        # self.ui.menu_decrease_font_size.setIcon(QIcon(get_themed_asset_image("icons/decrease_font.png")))


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
        if self.ui.menu_enable_dark_mode.isChecked():
            app.active_settings.set(GUI_STYLE, GUI_STYLE_DARK)
        else:
            app.active_settings.set(GUI_STYLE, GUI_STYLE_LIGHT)

        activate_theme(self._qt_app)

        # all icons must be reloaded
        self.load_icons()
        self.local_package_explorer.apply_theme()
        self.app_grid.re_init(self.model.app_grid)  # needs a whole reload because models need to be reinitialized
        if self.search_dialog:
            self.search_dialog.apply_theme()

    @pyqtSlot()
    def on_main_view_changed(self):
        """ Change between main views (grid and package explorer) """
        if self.ui.main_toolbox.currentIndex() == 1:  # package view
            # hide floating grid buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.hide()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.hide()
        elif self.ui.main_toolbox.currentIndex() == 0:  # grid view
            # show floating buttons
            if ADD_APP_LINK_BUTTON:
                self.ui.add_app_link_button.show()
            if ADD_TAB_BUTTON:
                self.ui.add_tab_button.show()

    @ pyqtSlot()
    def open_conan_search_dialog(self):
        """ Opens a Conan Search dialog. Only one allowed. """
        if self.search_dialog:
            self.search_dialog.show()
            self.search_dialog.activateWindow()
            return

        # parent=None enables to hide the dialog behind the application window
        self.search_dialog = ConanSearchDialog(None, self)
        self.search_dialog.show()

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
            # self.apply_view_settings()  # now view settings can be applied

    @pyqtSlot()
    def display_versions_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_versions.isChecked()
        app.active_settings.set(DISPLAY_APP_VERSIONS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def apply_display_users_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_users.isChecked()
        app.active_settings.set(DISPLAY_APP_USERS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot()
    def display_channels_setting_toggled(self):
        """ Reads the current menu setting, saves it and updates the gui """
        status = self.ui.menu_toggle_display_channels.isChecked()
        app.active_settings.set(DISPLAY_APP_CHANNELS, status)
        self.app_grid.re_init_all_app_links()

    @pyqtSlot(str)
    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)

    def load_icons(self):
        """ Load icons for main toolbox and menu """

