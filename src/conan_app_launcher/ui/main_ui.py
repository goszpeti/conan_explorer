import threading
import time

from PyQt5 import QtCore, QtWidgets, QtGui

from conan_app_launcher import config
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui import common
from conan_app_launcher.ui.qt import app_grid
from .qt.clickable_label import ClickableLabel
from conan_app_launcher.layout_file import parse_layout_file, AppEntry
from conan_app_launcher import __version__ as version

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)

        QBtn = QtWidgets.QDialogButtonBox.Ok
        self.text = QtWidgets.QLabel(self)
        self.text.setText("App Grid for Conan\n" + version + "\n" +
                          "Copyright (C), 2020, Peter Gosztolya")

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        #  config.PROG_NAME

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class AppUiEntry(QtWidgets.QVBoxLayout):

        def __init__(self, parent:QtWidgets.QTabWidget, app:AppEntry):
            super().__init__()
            self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
            self.app_button = ClickableLabel(parent)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.app_button.sizePolicy().hasHeightForWidth())
            self.app_button.setSizePolicy(sizePolicy)
            self.app_button.setTextFormat(QtCore.Qt.AutoText)
            self.app_button.setPixmap(QtGui.QPixmap(str(app.icon)).scaled(64, 64, transformMode=Qt.SmoothTransformation))
            self.app_button.setScaledContents(False)
            self.app_button.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
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
            #TODO
            self.app_version_cbox.setDisabled(True)
            self.addWidget(self.app_version_cbox)

class TabUiGrid():
    pass

class MainUi(QtCore.QObject):
    """ Base class of the main qt ui. Holds all the SubUi elements. """

    UPDATE_TIME = 1000  # microseconds

    def __init__(self):
        super().__init__()
        self._logger = Logger()
        self._qt_root_obj = QtWidgets.QMainWindow()
        self._ui = app_grid.Ui_MainWindow()
        self._ui.setupUi(self._qt_root_obj)

        Logger.init_qt_logger(self._ui.console)
        # QtLogStream().log_written.connect(self._ui.textBrowser.insertHtml)
        self._logger.info("Start")
        about_dialog = AboutDialog(self._qt_root_obj)
        self._ui.menu_about_action.triggered.connect(about_dialog.show)
        self._tabs = parse_layout_file(config.config_path)
        if self._tabs:
            for tab in self._tabs:
                self._ui.tabs.addTab()
                pass
            row = 0
            column = 0
            for app in self._tabs[0].get_app_entries():
                # add in order of occurence
                self._ui.tab1_grid_layout.addLayout(AppUiEntry(self._ui.gridLayoutWidget, app), row, column)
                row += 1
                column += 1
        # connect buttons

        # self._ui.options_button.clicked.connect(self.show_options_window)
        self.init_gui()

    @property
    def ui(self):
        """ Contains all gui objects defined in Qt .ui file. Subclasses need access to this. """
        return self._ui

    @property
    def qt_root_obj(self):
        """ The base class of this ui. Is needed to pass as parent ot call show and hide. """
        return self._qt_root_obj

    def init_gui(self):
        """ Start the thread to asynchronly load the gui. """
        self._init_thread = threading.Thread(
            name="InitMainUI", target=self._init_gui(), daemon=True)
        self._init_thread.start()

    def _init_gui(self):
        """ Retranslates, then loads all SubUi elements. """

        self.ready = True

    def unload_gui(self):
        """ Deletes all SubUi elements """

        self._init_thread.join()
