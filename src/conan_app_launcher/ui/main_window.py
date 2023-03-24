import datetime
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher import APP_NAME, MAX_FONT_SIZE, MIN_FONT_SIZE, PathLike, conan_version
                                
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.core.conan_cleanup import ConanCleanup
from conan_app_launcher.settings import (CONSOLE_SPLIT_SIZES, FILE_EDITOR_EXECUTABLE, FONT_SIZE,
                                         GUI_MODE, GUI_MODE_DARK, GUI_MODE_LIGHT, GUI_STYLE, GUI_STYLE_FLUENT, 
                                         GUI_STYLE_MATERIAL, LAST_CONFIG_FILE, WINDOW_SIZE)
from conan_app_launcher.ui.common.theming import get_gui_dark_mode, get_gui_style
from conan_app_launcher.ui.dialogs.file_editor_selection.file_editor_selection import FileEditorSelDialog
from conan_app_launcher.ui.plugin.plugins import PluginHandler
from conan_app_launcher.ui.widgets import AnimatedToggle, WideMessageBox
from PySide6.QtCore import QRect, SignalInstance, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget, QFrame, QVBoxLayout, QRadioButton, QSizePolicy, QSpacerItem

from .common import (AsyncLoader, activate_theme, init_qt_logger,
                     remove_qt_logger)
from .fluent_window import FluentWindow, SideSubMenu
from .plugin import PluginInterfaceV1
from .model import UiApplicationModel
from .views import AboutPage, AppGridView, PluginsPage


# Signal names
@dataclass
class BaseSignals():
    """ Dict of base signals, wich is passed down to the Views """
    conan_pkg_installed: SignalInstance  # conan_ref, pkg_id
    conan_pkg_removed: SignalInstance  # conan_ref, pkg_ids
    conan_remotes_updated: SignalInstance
    page_size_changed: SignalInstance

class MainWindow(FluentWindow):
    """ Instantiates MainWindow and holds all UI objects """

    # signals for inter page communication
    conan_pkg_installed: SignalInstance = Signal(str, str)  # type: ignore - conan_ref, pkg_id
    conan_pkg_removed: SignalInstance = Signal(str, str)  # type: ignore - conan_ref, pkg_ids
    conan_remotes_updated: SignalInstance = Signal()  # type: ignore
    page_size_changed: SignalInstance = Signal(QWidget) # type: ignore

    log_console_message: SignalInstance = Signal(str)  # type: ignore - message

    qt_logger_name = "qt_logger"

    def __init__(self, qt_app: QApplication):
        super().__init__(title_text=APP_NAME)
        self._qt_app = qt_app
        self.loaded = False
        self.base_signals = BaseSignals(self.conan_pkg_installed, self.conan_pkg_removed, self.conan_remotes_updated, self.page_size_changed)
        self.model = UiApplicationModel(self.conan_pkg_installed, self.conan_pkg_removed)
        self._plugin_handler = PluginHandler(self)
        self.setWindowTitle(APP_NAME)
        # connect logger to console widget to log possible errors at init
        init_qt_logger(Logger(), self.qt_logger_name, self.log_console_message)
        self.log_console_message.connect(self.write_log)
        self.page_size_changed.connect(self.resize_page)
        # Default pages
        self.about_page = AboutPage(self, self.base_signals)
        self.plugins_page = PluginsPage(self, self._plugin_handler)
        self.app_grid = AppGridView(self, self.model.app_grid, self.base_signals, self.page_widgets)
        self._init_left_menu()
        self._init_right_menu()

        self._plugin_handler.load_plugin.connect(self._load_plugin)
        # size needs to be set as early as possible to correctly position loading windows
        self.restore_window_state()


    def resize_page(self, widget: QWidget):
        pass
        # widget.setMaximumWidth(self.ui.center_frame.width() - 4)

    def _init_left_menu(self):
        self.add_left_menu_entry("Conan Quicklaunch", "icons/global/grid.svg", is_upper_menu=True, page_widget=self.app_grid,
                                 create_page_menu=True)
        # set default page
        self.page_widgets.get_button_by_name("Conan Quicklaunch").click()

    def _init_style_chooser(self):
        self._style_chooser_frame = QFrame(self)
        self._style_chooser_layout = QVBoxLayout(self._style_chooser_frame)
        self._style_chooser_radio_material = QRadioButton("Material", self._style_chooser_frame)
        self._style_chooser_layout.addWidget(self._style_chooser_radio_material)
        self._style_chooser_radio_fluent = QRadioButton("Fluent", self._style_chooser_frame)
        self._style_chooser_layout.addWidget(self._style_chooser_radio_fluent)
        # set initial state
        if get_gui_style() == GUI_STYLE_MATERIAL:
            self._style_chooser_radio_material.setChecked(True)
        elif get_gui_style() == GUI_STYLE_FLUENT:
            self._style_chooser_radio_fluent.setChecked(True)

        self._style_chooser_radio_material.clicked.connect(self.on_style_changed)
        self._style_chooser_radio_fluent.clicked.connect(self.on_style_changed)


    def _init_right_menu(self):
        self.main_general_settings_menu.add_button_menu_entry("Select file editor",
                                                              self.open_file_editor_selection_dialog, "icons/edit_file.svg")
        view_settings_submenu = SideSubMenu(self.ui.right_menu_bottom_content_sw, "View")

        self.main_general_settings_menu.add_sub_menu(view_settings_submenu, "icons/view.svg")

        view_settings_submenu.add_button_menu_entry(
            "Font Size +", self.on_font_size_increased, "icons/increase_font.svg", QKeySequence("CTRL++"), self)
        view_settings_submenu.add_button_menu_entry(
            "Font Size - ", self.on_font_size_decreased, "icons/decrease_font.svg", QKeySequence("CTRL+-"), self)
        view_settings_submenu.add_menu_line()

        view_settings_submenu.add_toggle_menu_entry(
            "Dark Mode", self.on_dark_mode_changed, get_gui_dark_mode(), "icons/dark_mode.svg")
        self._init_style_chooser()
        view_settings_submenu.add_named_custom_entry(
            "Icon Style", self._style_chooser_frame, "icons/global/conan_settings.svg", force_v_layout=True)
        view_settings_submenu.add_menu_line()

        self.main_general_settings_menu.add_menu_line()
        
        if conan_version.startswith("1"):
            self.main_general_settings_menu.add_button_menu_entry("Remove Locks",
                                                                app.conan_api.remove_locks, "icons/remove-lock.svg")
            self.main_general_settings_menu.add_button_menu_entry("Clean Conan Cache",
                                                                self.open_cleanup_cache_dialog, "icons/cleanup.svg")
            self.main_general_settings_menu.add_menu_line()
        self.add_right_bottom_menu_main_page_entry("Manage Plugins", self.plugins_page, "icons/plugin.svg")
        self.add_right_bottom_menu_main_page_entry("About", self.about_page, "icons/about.svg")

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        self.app_grid.setEnabled(False)  # disable app_grid to signal shutdown
        try:
            self.log_console_message.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        remove_qt_logger(Logger(), self.qt_logger_name)
        super().closeEvent(event)

    def resizeEvent(self, a0) -> None:  # QtGui.QResizeEvent
        super().resizeEvent(a0)
        if self.loaded:
            self.ui.page_stacked_widget.currentWidget().setMaximumWidth(self.ui.center_frame.width() - 4)
            self.ui.page_stacked_widget.currentWidget().adjustSize()

    def load(self, config_source: Optional[PathLike] = None):
        """ Load all application gui elements specified in the GUI config (file) """
        config_source_str = str(config_source)
        if not config_source:
            config_source_str = app.active_settings.get_string(LAST_CONFIG_FILE)
        self._load_plugins()

        # model loads incrementally
        loader = AsyncLoader(self)
        loader.async_loading(self, self._load_job, (config_source_str,), cancel_button=False)
        loader.wait_for_finished()
        self.loaded = True

    def _load_plugins(self):
        self._plugin_handler.load_all_plugins()

    def _load_plugin(self, plugin):
        try:
            import_path = Path(plugin.import_path)
            sys.path.append(str(import_path.parent))
            module_ = importlib.import_module(import_path.stem)
            class_ = getattr(module_, plugin.plugin_class)
            plugin_object: PluginInterfaceV1 = class_(self, self.base_signals, self.page_widgets)
            self.add_left_menu_entry(plugin.name, plugin.icon, True, plugin_object, plugin.side_menu)
        except Exception as e:
            Logger().error(f"Can't load plugin {plugin.name}: {str(e)}")

    def _load_job(self, config_source_str):
        # load ui file definitions
        self.model.loadf(config_source_str)
        # now actually load the views - this need signals, to execute in the gui thread
        self.app_grid.model = self.model.app_grid
        for page in self.page_widgets.get_all_pages():
            try:
                page.load_signal.emit()
            except Exception as e:
                Logger().error(f"Can't load page {type(page)}: {str(e)}")
        # loads the remotes in the search dialog
        self.conan_remotes_updated.emit()

    def on_font_size_increased(self):
        """ Increase font size by 2. Ignore if font gets too large. """
        new_size = app.active_settings.get_int(FONT_SIZE) + 1
        if new_size > MAX_FONT_SIZE:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    def on_font_size_decreased(self):
        """ Decrease font size by 2. Ignore if font gets too small. """
        new_size = app.active_settings.get_int(FONT_SIZE) - 1
        if new_size < MIN_FONT_SIZE:
            return
        app.active_settings.set(FONT_SIZE, new_size)
        activate_theme(self._qt_app)

    def on_style_changed(self):
        # wait 0,5 seconds, so all animations can finish
        start = datetime.datetime.now()
        while datetime.datetime.now() - start <= datetime.timedelta(milliseconds=600):
            QApplication.processEvents()
        if self._style_chooser_radio_material.isChecked():
            app.active_settings.set(GUI_STYLE, GUI_STYLE_MATERIAL)
        elif self._style_chooser_radio_fluent.isChecked():
            app.active_settings.set(GUI_STYLE, GUI_STYLE_FLUENT)
        self.reload_theme()
    

    def on_dark_mode_changed(self):
        sender_toggle: AnimatedToggle = self.sender()  # type: ignore
        sender_toggle.wait_for_anim_finish()
        enable_dark_mode = sender_toggle.isChecked()
        if enable_dark_mode:
            app.active_settings.set(GUI_MODE, GUI_MODE_DARK)
        else:
            app.active_settings.set(GUI_MODE, GUI_MODE_LIGHT)
        self.reload_theme()

    def reload_theme(self):
        activate_theme(self._qt_app)

        # all icons must be reloaded
        self.apply_theme()
        for page in self.page_widgets.get_all_pages():
            page.reload_themed_icons()

    def open_cleanup_cache_dialog(self):
        """ Open the message box to confirm deletion of invalid cache folders """
        cleaner = ConanCleanup(app.conan_api)
        loader = AsyncLoader(self)
        loader.async_loading(self, cleaner.get_cleanup_cache_paths, )
        loader.wait_for_finished()
        paths = cleaner.orphaned_packages.union(cleaner.orphaned_references)
        if not paths:
            self.write_log("INFO: Nothing found in cache to clean up.")
            return
        if len(paths) > 1:
            path_list = "\n".join(paths)
        else:
            path_list = str(paths)

        msg = WideMessageBox(parent=self)
        msg.setWindowTitle("Delete folders")
        msg.setText("Are you sure, you want to delete the found folders?\t")
        msg.setDetailedText(path_list)
        msg.setStandardButtons(WideMessageBox.StandardButton.Yes | WideMessageBox.StandardButton.Cancel) # type: ignore
        msg.setIcon(WideMessageBox.Icon.Question)
        msg.setWidth(800)
        msg.setMaximumHeight(600)
        reply = msg.exec()
        if reply == WideMessageBox.StandardButton.Yes:
            for path in paths:
                rmtree(str(path), ignore_errors=True)

    def open_file_editor_selection_dialog(self):
        dialog = FileEditorSelDialog(self)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            app.active_settings.set(FILE_EDITOR_EXECUTABLE, "")

    def write_log(self, text):
        """ Write the text signaled by the logger """
        self.ui.console.append(text)

    def restore_window_state(self):
        # restore window size
        sizes_str = app.active_settings.get_string(WINDOW_SIZE)
        if sizes_str.lower() == "maximized":
            self.showMaximized()
        else:
            split_sizes_int = [0, 0, 800, 600]
            try:
                split_sizes = sizes_str.strip().split(",")
                split_sizes_int = [int(size) for size in split_sizes]
            except Exception as e:
                Logger().warning(f"Can't read window size: {str(e)}")
            try:
                assert len(split_sizes_int) == 4, "Invalid setting window size length."
                geometry = QRect(*split_sizes_int)
                self.setGeometry(geometry)
            except Exception as e:
                Logger().warning(f"Can't restore window size: {str(e)}")

        # restore console size
        try:
            sizes_str = app.active_settings.get_string(CONSOLE_SPLIT_SIZES)
            split_sizes = sizes_str.strip().split(",")
            split_sizes_int = [int(size) for size in split_sizes]
            self.ui.content_footer_splitter.setSizes(split_sizes_int)
        except Exception as e:
            Logger().warning(f"Can't restore console size: {str(e)}")

    def save_window_state(self):
        # save window size
        if self.isMaximized():
            app.active_settings.set(WINDOW_SIZE, "maximized")
        else:
            geometry = self.geometry()
            geo_str = f"{geometry.left()},{geometry.top()},{geometry.width()},{geometry.height()}"
            app.active_settings.set(WINDOW_SIZE, geo_str)
        # save console size
        sizes = self.ui.content_footer_splitter.sizes()
        if len(sizes) < 2:
            Logger().warning(f"Can't save splitter size")
        sizes_str = f"{int(sizes[0])},{int(sizes[1])}"
        app.active_settings.set(CONSOLE_SPLIT_SIZES, sizes_str)
