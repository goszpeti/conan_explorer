from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtWidgets, QtGui, uic

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanWorker, parse_config_file, write_config_file, AppConfigEntry
from conan_app_launcher.settings import (
    LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS, GRID_COLOUMNS, GRID_ROWS, Settings)
from conan_app_launcher.ui.app_link import AppLink
from conan_app_launcher.ui.tab_app_grid import TabAppGrid
from conan_app_launcher.ui.add_remove_apps import AddRemoveAppsDialog
from conan_app_launcher.ui.edit_app import EditAppDialog


Qt = QtCore.Qt


class MainUi(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    conan_info_updated = QtCore.pyqtSignal()
    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message

    def __init__(self, settings: Settings):
        super().__init__()
        self._ui = uic.loadUi(this.base_path / "ui" / "qt" / "app_grid.ui")  # , baseinstance=self)
        self._settings = settings
        self._tabs_info: List[TabAppGrid] = []
        self._tabs = []
        self._about_dialog = AboutDialog(self)

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self)
        self._ui.console.setFontPointSize(10)

        self._ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self._ui.menu_open_config_file.triggered.connect(self.open_config_file_dialog)
        self._ui.menu_set_display_versions.triggered.connect(self.toggle_display_versions)
        self._ui.menu_set_display_channels.triggered.connect(self.toogle_display_channels)

        self.conan_info_updated.connect(self.update_layouts)
        self.new_message_logged.connect(self.write_log)

        self.init_gui()

    def save_all_configs(self):
        write_config_file(self._settings.get(LAST_CONFIG_FILE), self._tabs_info)

    def closeEvent(self, event):  # override QMainWindow
        """ Remove qt logger, so it doesn't log into a non existant object """
        super().closeEvent(event)
        try:
            self.new_message_logged.disconnect(self.write_log)
        except Exception:
            # Sometimes the closeEvent is called twice and disconnect errors.
            pass
        Logger.remove_qt_logger()

    def open_config_file_dialog(self):
        """" Open File Dialog and load config file """
        dialog_path = Path.home()
        config_file_path = Path(self._settings.get(LAST_CONFIG_FILE))
        if config_file_path.exists():
            dialog_path = config_file_path.parent
        dialog = QtWidgets.QFileDialog(caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self._settings.set(LAST_CONFIG_FILE, dialog.selectedFiles()[0])
            self._re_init()

    def toggle_display_versions(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        self._settings.set(DISPLAY_APP_VERSIONS, self._ui.menu_set_display_versions.isChecked())
        self.update_layouts()

    def toogle_display_channels(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        self._settings.set(DISPLAY_APP_CHANNELS, self._ui.menu_set_display_channels.isChecked())
        self.update_layouts()

    def create_layout(self):
        """ Creates the tabs and app icons """
        for tab_info in self._tabs_info:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            tab = TabAppGrid(tab_info, parent=self, update_signal=self.conan_info_updated, coloumns=self._settings.get(
                GRID_COLOUMNS), rows=self._settings.get(GRID_ROWS))
            self._tabs.append(tab)
            self._ui.tabs.addTab(tab, tab_info.name)

    def update_layouts(self):
        """ Update without cleaning up. Ungrey entries and set correct icon and add hover text """
        for tab in self._tabs:
            for app in tab.apps:
                app.update_entry(self._settings)
        self.save_all_configs()

    def init_gui(self):
        """ Cleans up ui, reads config file and creates new layout """
        if self._ui.tabs.count() > 1:  # remove the default tab
            self._ui.tabs.removeTab(1)
        config_file_path = Path(self._settings.get(LAST_CONFIG_FILE))
        if config_file_path.is_file():  # escape error log on first opening
            self._tabs_info = parse_config_file(config_file_path)

        this.conan_worker = ConanWorker(self._tabs_info, self.conan_info_updated)
        self.create_layout()

        if self._ui.tabs.count() > 1:  # set the default tab to the first user defined tab
            self._ui.tabs.setCurrentIndex(1)

    def on_selection_change(self, index):
        view_index = self._ui.treeView.selectionModel().selectedIndexes()[0]
        proxy_index = self.proxy.mapToSource(view_index)
        item_name = self.model.fileName(proxy_index)
        path = self.model.fileInfo(view_index).dir().absolutePath()
        self._ui.listView.setRootIndex(self.fileModel.setRootPath(path))
        print(item_name)

    def _re_init(self):
        """ To be called, when a new config file is loaded """
        this.conan_worker.finish_working(3)
        self.init_gui()

    def write_log(self, text):
        """ Write the text signaled by the logger """
        self._ui.console.append(text)


class AboutDialog(QtWidgets.QDialog):
    """ Defines Help->About Dialog """
    html_content = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; }
    </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;">
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt;">Conan App Launcher ${version}</span></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt;">Copyright (C), 2021, Péter Gosztolya and contributors.</span></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="https://github.com/goszpeti/conan_app_launcher"><span style=" font-size:11pt; text-decoration: underline; color:#0000ff;">https://github.com/goszpeti/conan_app_launcher</span></a></p></body></html>
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        self.resize(450, 300)
        ok_button = QtWidgets.QDialogButtonBox.Ok

        icon = QtGui.QIcon(str(this.base_path / "assets" / "icon.ico"))
        self._logo_label = QtWidgets.QLabel(self)
        self._logo_label.setPixmap(icon.pixmap(100, 100))
        self._text = QtWidgets.QTextBrowser(self)
        self._text.setStyleSheet("background-color: #F0F0F0;")
        self._text.setHtml(self.html_content.replace("${version}", this.__version__))
        self._text.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._button_box = QtWidgets.QDialogButtonBox(ok_button)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self._logo_label)
        self.layout.addWidget(self._text)
        self.layout.addWidget(self._button_box)
        self.setLayout(self.layout)
