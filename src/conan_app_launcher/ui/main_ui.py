from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtWidgets, uic

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components import ConanWorker, parse_config_file, write_config_file
from conan_app_launcher.settings import LAST_CONFIG_FILE, DISPLAY_APP_VERSIONS, DISPLAY_APP_CHANNELS, Settings
from conan_app_launcher.ui.layout_entries import AppUiEntry, TabUiGrid


class CustomProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        # self.setDynamicSortFilter(True)

    def rowCount(self, index):
        model_index = self.mapToSource(index)
        if not model_index.isValid():
            return 0
        new_rc = self.sourceModel().rowCount(model_index) + 1
        # self.insertRows(0)
        return new_rc

    def insertRows(self, position, rows=1, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            self.insertRows(position, row, parent)
            self.setData(parent, "AWESOME")
            print('AWESOME VIRTUAL ROW')
        self.endInsertRows()
        return True


class TodoModel(QtWidgets.QFileSystemModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRootPath(r"C:\Users\goszp\.conan\data")

    # def data(self, index, role):
    #     if role == Qt.DisplayRole:
    #         _, text = self.todos[index.row()]
    #         return text

    #     if role == Qt.DecorationRole:
    #         status, _ = self.todos[index.row()]
    #         if status:
    #             return tick


class MainUi(QtWidgets.QMainWindow):
    """ Instantiates MainWindow and holds all UI objects """
    conan_info_updated = QtCore.pyqtSignal()
    new_message_logged = QtCore.pyqtSignal(str)  # str arg is the message

    def __init__(self, settings: Settings):
        super().__init__()
        self._ui = uic.loadUi(this.base_path / "ui" / "qt" / "app_grid.ui", baseinstance=self)
        self._settings = settings
        self._tab_info: List[TabUiGrid] = []
        self._about_dialog = AboutDialog(self)
        self._tab = None

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self)
        self._ui.console.setFontPointSize(10)

        self._ui.menu_about_action.triggered.connect(self._about_dialog.show)
        self._ui.menu_open_config_file_action.triggered.connect(self.open_config_file_dialog)
        self._ui.menu_set_display_versions.triggered.connect(self.toggle_display_versions)
        self._ui.menu_set_display_channels.triggered.connect(self.toogle_display_channels)

        self.conan_info_updated.connect(self.update_layout)
        self.new_message_logged.connect(self.write_log)

        self.init_gui()

    # @QtCore.pyqtSlot()
#    def on_click(self, index):
        # path = self.model.fileInfo(index).absoluteFilePath()
        # self._ui.listView.setRootIndex(self.fileModel.setRootPath(path))
        # self.todos = todos or []

    def save_all_configs(self):
        write_config_file(self._settings.get(LAST_CONFIG_FILE), self._tab_info)

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
        self.update_layout()

    def toogle_display_channels(self):
        """ Reads the current menu setting, sevaes it and updates the gui """
        self._settings.set(DISPLAY_APP_CHANNELS, self._ui.menu_set_display_channels.isChecked())
        self.update_layout()

    def create_layout(self):
        """ Creates the tabs and app icons """
        for tab_info in self._tab_info:
            # need to save object locally, otherwise it can be destroyed in the underlying C++ layer
            self._tab = TabUiGrid(self, tab_info.name)
            row = 0  # 3
            column = 0  # 4
            for app_info in tab_info.get_app_entries():
                # add in order of occurence
                app = AppUiEntry(self._tab.tab_scroll_area_widgets, app_info, self.conan_info_updated)
                self._tab.apps.append(app)
                self._tab.tab_grid_layout.addLayout(app, row, column, 1, 1)
                column += 1
                if column == 4:
                    column = 0
                    row += 1
            self._ui.tabs.addTab(self._tab, tab_info.name)

    def update_layout(self):
        """ Update without cleaning up. Ungrey entries and set correct icon and add hover text """
        for tab in self._ui.tabs.findChildren(TabUiGrid):
            for app in tab.apps:
                app.update_entry(self._settings)
        self.save_all_configs()

    def init_gui(self):
        """ Cleans up ui, reads config file and creates new layout """
        # while self._ui.tabs.count() > 0:
        #    self._ui.tabs.removeTab(0)
        config_file_path = Path(self._settings.get(LAST_CONFIG_FILE))
        if config_file_path.is_file():  # escape error log on first opening
            self._tab_info = parse_config_file(config_file_path)
        this.conan_worker = ConanWorker(self._tab_info, self.conan_info_updated)
        self.model = TodoModel()
        # dirModel -> setFilter(QDir: : NoDotAndDotDot |
        #                       QDir:: AllDirs);
        self.proxy = CustomProxyModel()
        self.proxy.setSourceModel(self.model)
        self.model_index = self.model.index(self.model.rootDirectory().absolutePath())
        print(self.model.rootDirectory().absolutePath())
        self.proxy_index = self.proxy.mapFromSource(self.model_index)
        self._ui.treeView.setModel(self.proxy)

        self._ui.treeView.setRootIndex(self.proxy_index)
        self.fileModel = QtWidgets.QFileSystemModel(self)
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |
                                 QtCore.QDir.Files)
        self.fileModel.setRootPath(self.model.rootDirectory().absolutePath())
        self._ui.listView.setModel(self.fileModel)

        # self._ui.treeView.clicked.connect(self.on_click)
        self._ui.treeView.setColumnHidden(1, True)
        self._ui.treeView.setColumnHidden(2, True)
        self._ui.treeView.setColumnWidth(0, 310)
        # self._ui.treeView.setRootIsDecorated(False)
        # self._ui.treeView.setItemsExpandable(False)
        self._ui.treeView.selectionModel().selectionChanged.connect(
            self.on_selection_change)

        self.create_layout()

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

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        ok_button = QtWidgets.QDialogButtonBox.Ok
        self._text = QtWidgets.QLabel(self)
        self._text.setText("Conan App Launcher\n" + this.__version__ + "\n" +
                           "Copyright (C), 2020, Péter Gosztolya")

        self._button_box = QtWidgets.QDialogButtonBox(ok_button)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self._text)
        self.layout.addWidget(self._button_box)
        self.setLayout(self.layout)
