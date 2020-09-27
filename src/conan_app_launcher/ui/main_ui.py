import os
import threading
from pathlib import Path

import conan_app_launcher as this
from conan_app_launcher.config_file import AppEntry, parse_config_file
from conan_app_launcher.logger import Logger

from PyQt5 import QtCore, QtGui, QtWidgets

from .qt.app_button import AppButton
from .qt.app_grid import Ui_MainWindow
# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


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


class AppUiEntry(QtWidgets.QVBoxLayout):

    def __init__(self, parent: QtWidgets.QTabWidget, app: AppEntry):
        super().__init__()
        self.app_info = app
        self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        # TODO add icon
        self.app_button = AppButton(parent, app.icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_button.sizePolicy().hasHeightForWidth())
        self.app_button.setSizePolicy(sizePolicy)
        # self.app_button.setMaximumSize(QtCore.QSize(64, 64))
        self.app_button.setTextFormat(QtCore.Qt.AutoText)
        self.app_button.setPixmap(QtGui.QPixmap(str(app.icon)).scaled(
            64, 64, transformMode=Qt.SmoothTransformation))
        self.app_button.setScaledContents(False)
        self.app_button.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.app_button.setToolTip(app.package_id.full_repr())
        self.addWidget(self.app_button)
        self.app_name = QtWidgets.QLabel(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_name.sizePolicy().hasHeightForWidth())
        self.app_name.setSizePolicy(sizePolicy)
        self.app_name.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.app_name)
        self.app_name.setText(app.name)
        self.app_version_cbox = QtWidgets.QComboBox(parent)
        self.app_version_cbox.addItem(app.package_id.version)
        # TODO unlock when version feature is implemented
        self.app_version_cbox.setDisabled(True)
        self.addWidget(self.app_version_cbox)
        self.app_button.clicked.connect(self.app_clicked)

    def app_clicked(self):
        # get conan info TODO: cache later
        if self.app_info.executable.is_file():
            os.system(str(self.app_info.executable))


class TabUiGrid(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.apps = []  # AppUiEntry

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setGeometry(QtCore.QRect(0, 0, 811, 439))
        # self.setObjectName("tab_1")

        # self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        # self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_scroll_area.sizePolicy().hasHeightForWidth())
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        # self.tab_scroll_area.setObjectName("tab_scroll_area")
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.tab_scroll_area_widgets)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_scroll_area_widgets.sizePolicy().hasHeightForWidth())
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        self.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(QtCore.Qt.LeftToRight)

        self.tab_grid_layout = QtWidgets.QGridLayout(self)
        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.tab_grid_layout.setColumnMinimumWidth(0, 202)
        self.tab_grid_layout.setColumnMinimumWidth(1, 202)
        self.tab_grid_layout.setColumnMinimumWidth(2, 202)
        self.tab_grid_layout.setColumnMinimumWidth(3, 202)
        self.tab_grid_layout.setRowMinimumHeight(0, 146)
        self.tab_grid_layout.setRowMinimumHeight(1, 146)
        self.tab_grid_layout.setRowMinimumHeight(2, 146)
        self.tab_grid_layout.setColumnStretch(0, 1)
        self.tab_grid_layout.setColumnStretch(1, 1)
        self.tab_grid_layout.setColumnStretch(2, 1)
        self.tab_grid_layout.setColumnStretch(3, 1)
        self.tab_grid_layout.setRowStretch(0, 1)
        self.tab_grid_layout.setRowStretch(1, 1)
        self.tab_grid_layout.setRowStretch(2, 1)

        self.verticalLayout_9.addLayout(self.tab_grid_layout)
        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.verticalLayout_8.addWidget(self.tab_scroll_area)
        # self.tabs.addTab(self, "")


class MainUi(QtCore.QObject):
    """ Instantiates MainWindow and holds all UI objects """

    def __init__(self):
        super().__init__()
        self._tab_info = []
        self._qt_root_obj = QtWidgets.QMainWindow()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self._qt_root_obj)
        self._init_thread = threading.Thread(
            name="InitMainUI", target=self._init_gui(), daemon=True)

        # connect logger to console widget
        Logger.init_qt_logger(self._ui.console)
        self._ui.console.setFontPointSize(10)
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
        if this.config_path.exists():
            dialog_path = this.config_path.parent
        dialog = QtWidgets.QFileDialog(caption="Select JSON Config File",
                                       directory=str(dialog_path), filter="JSON files (*.json)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            this.config_path = Path(dialog.selectedFiles()[0])
            self._re_init()

    def create_layout(self):
        tab = None
        for tab_info in self._tab_info:
            tab = TabUiGrid()
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
        self._tab_info = parse_config_file(this.config_path)
        self.create_layout()

    def _re_init(self):
        # reset gui and objects
        for i in range(self._ui.tabs.count()):
            self._ui.tabs.removeTab(i)
        this.conan_worker.finish_working(2)
        # self._init_gui()
