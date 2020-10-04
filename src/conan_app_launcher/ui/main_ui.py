import threading
from pathlib import Path

import conan_app_launcher as this
from conan_app_launcher.config_file import parse_config_file
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui.layout_entries import AppUiEntry, TabUiGrid
from conan_app_launcher.ui.qt.app_grid import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets


class MainUi(QtCore.QObject):
    """ Instantiates MainWindow and holds all UI objects """

    def __init__(self):
        super().__init__()
        self._tab_info = []
        self._qt_root_obj = QtWidgets.QMainWindow()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self._qt_root_obj)

        # connect logger to console widget to log possible errors at init
        Logger.init_qt_logger(self._ui.console)
        self._ui.console.setFontPointSize(10)

        self._init_thread = threading.Thread(
            name="InitMainUI", target=self._init_gui(), daemon=True)

        self._about_dialog = AboutDialog(self._qt_root_obj)
        self._ui.menu_about_action.triggered.connect(self._about_dialog.show)

        # TODO set last Path on dir
        self._ui.menu_open_config_file_action.triggered.connect(self.open_config_file_dialog)

        # remove default tab TODO unclean in code, but nice preview in qt designer
        self._ui.tabs.removeTab(0)
        self.init_gui()

    @property
    def ui(self):
        """ Contains all gui objects defined in Qt .ui file. Subclasses need access to this. """
        return self._ui

    @property
    def qt_root_obj(self):
        """ The base class of this ui. Is needed to pass as parent ot call show and hide. """
        return self._qt_root_obj

    def open_config_file_dialog(self):
        dialog_path = Path.home()
        if this.config_file_path.exists():
            dialog_path = this.config_file_path.parent
        dialog = QtWidgets.QFileDialog(caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            this.config_path = Path(dialog.selectedFiles()[0])
            self._re_init()

    def create_layout(self):
        tab = None
        for tab_info in self._tab_info:
            tab = TabUiGrid(tab_info.name)
            row = 0  # 3
            column = 0  # 4
            for app_info in tab_info.get_app_entries():

                # add in order of occurence
                app = AppUiEntry(tab.tab_scroll_area_widgets, app_info)
                tab.apps.append(app)
                tab.tab_grid_layout.addLayout(app, row, column, 1, 1)
                self._ui.tab1_grid_layout.addLayout(AppUiEntry(
                    self._ui.tab_scroll_area_widgets, app_info), row, column)
                column += 1
                if column == 4:
                    column = 0
                    row += 1
            # self.tabs.append(tab)
            self._ui.tabs.addTab(tab, tab_info.name)

    def init_gui(self):
        """ Start the thread to asynchronously load gui background tasks """
        self._init_thread.start()

    def _init_gui(self):
        """ Call all conan functions """
        self._tab_info = parse_config_file(this.config_file_path)
        self.create_layout()

    def _re_init(self):
        # reset gui and objects
        for i in range(self._ui.tabs.count()):
            self._ui.tabs.removeTab(i)
        this.conan_worker.finish_working(2)
        self._init_gui()


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)

        QBtn = QtWidgets.QDialogButtonBox.Ok
        self._text = QtWidgets.QLabel(self)
        self._text.setText("Conan App Launcher\n" + this.__version__ + "\n" +
                           "Copyright (C), 2020, Péter Gosztolya")

        self._button_box = QtWidgets.QDialogButtonBox(QBtn)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self._text)
        self.layout.addWidget(self._button_box)
        self.setLayout(self.layout)
