import threading
import time
import os
import platform
from pathlib import Path

from PyQt5 import QtCore, QtWidgets, QtGui

from conan_app_launcher import config
from conan_app_launcher.logger import Logger
from conan_app_launcher.ui import common
from conan_app_launcher.ui.qt import app_grid
from .qt.clickable_label import AppButton
from conan_app_launcher.layout_file import parse_layout_file, AppEntry
from conan_app_launcher import __version__ as version
from conans.client import conan_api
from conans.client.conan_command_output import CommandOutputer


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
        self.app = app
        self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        # TODO add icon
        self.app_button = AppButton(parent, app.icon)
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
        self.app_button.clicked.connect(self.app_clicked)

    def app_clicked(self):
        # get conan info TODO: cache later
        [conan, cache, user_io] = conan_api.ConanAPIV1.factory()
        [deps_graph, conanfile] = conan_api.ConanAPIV1.info(conan, self.app.package_id.full_repr())
        output = CommandOutputer(user_io.out, cache)._grab_info_data(deps_graph, True)
        output = output[0] # can have only one element
        package_folder = ""
        if output.get("binary") == "Download":
            remotes = cache.registry.load_remotes()
            for [remote, _] in remotes.items():
                if remote == "conan-center":
                    continue # no third party packages
                try:
                    search_results = conan_api.ConanAPIV1.search_packages(
                        conan, self.app.package_id.full_repr(), remote_name=remote)
                except: # next
                    continue
                # get options and settings
                sets = None
                default_settings = cache.default_profile.settings

                for result in search_results.get("results"):
                    for item in result.get("items"):
                        for package in item.get("packages"):
                            sets = package.get("settings")
                            if (sets.get("os") == default_settings.get("os") or
                                default_settings.get("os_build") == sets.get("os_build")
                                and 
                                sets.get("arch") == default_settings.get("arch") or
                                    sets.get("arch_build") == default_settings.get("arch_build")):
                                    break
                settings_list = []
                for name,value in sets.items():
                    settings_list.append(name + "=" + value)
                Logger().info("Installing %s", str(self.app.package_id))
                res = conan_api.ConanAPIV1.install_reference(
                    conan, self.app.package_id, update=True, settings=settings_list)
                [deps_graph, conanfile] = conan_api.ConanAPIV1.info(conan, self.app.package_id.full_repr())
                output = CommandOutputer(user_io.out, cache)._grab_info_data(deps_graph, True)
                output = output[0]  # can have only one element
        package_folder = output.get("package_folder")
        # get os specififc extension
        if platform.system == "Windows":
            self.app.executable = self.app.executable + ".exe"
        full_path=Path(package_folder / self.app.executable)
        if not full_path.is_file():
            pass
            # TODO log
        else:
            os.system(full_path)



class TabUiGrid(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.apps = []  # AppUiEntry
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        self.tab_scroll_area.setGeometry(QtCore.QRect(0, 0, 771, 441))
        self.tab_scroll_area.setGeometry(QtCore.QRect(0, 0, 771, 441))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_scroll_area.sizePolicy().hasHeightForWidth())
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        #self.tab_scroll_area.setObjectName("tab_scroll_area")
        self.tab_scroll_area_widgets = QtWidgets.QWidget()
        self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 755, 439))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_scroll_area_widgets.sizePolicy().hasHeightForWidth())
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        self.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(QtCore.Qt.LeftToRight)
        #self.tab_scroll_area_widgets.setObjectName("tab_scroll_area_widgets")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab_scroll_area_widgets)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 761, 445))
        #self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.tab_grid_layout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.tab_grid_layout.setContentsMargins(0, 0, 0, 0)
        #self.tab_grid_layout.setObjectName("tab_grid_layout")
        self.tab_grid_layout.setColumnStretch(0, 1)
        self.tab_grid_layout.setColumnStretch(1, 1)
        self.tab_grid_layout.setColumnStretch(2, 1)
        self.tab_grid_layout.setColumnStretch(3, 1)
        self.tab_grid_layout.setRowStretch(0, 1)
        self.tab_grid_layout.setRowStretch(1, 1)
        self.tab_grid_layout.setRowStretch(2, 1)
        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)



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
        self._tab_info = parse_layout_file(config.config_path)
        # TODO unclean
        self._ui.tabs.removeTab(0)
        self.tabs = []
        if self._tab_info:
            tab = None
            for tab_info in self._tab_info:
                tab = TabUiGrid()
                row = 0 # 3
                column = 0 # 4
                for app_info in tab_info.get_app_entries():

                    # add in order of occurence
                    app = AppUiEntry(tab.gridLayoutWidget, app_info)
                    tab.apps.append(app)
                    tab.tab_grid_layout.addLayout(app, row, column, 1, 1)
                    #self._ui.tab1_grid_layout.addLayout(AppUiEntry(
                    #    self._ui.gridLayoutWidget, app_info), row, column)
                    column += 1
                    if column == 4:
                        column = 0
                        row += 1
                self.tabs.append(tab)
                self._ui.tabs.addTab(tab, tab_info.name)
        a = self.ui.tabs.widget(1)

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
