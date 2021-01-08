from typing import List

from conan_app_launcher.components import AppEntry, run_file
from conan_app_launcher.settings import (DISPLAY_APP_CHANNELS,
                                         DISPLAY_APP_VERSIONS, Settings)
from conan_app_launcher.ui.qt.app_button import AppButton
from PyQt5 import QtCore, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class AppUiEntry(QtWidgets.QVBoxLayout):
    def __init__(self, parent: QtWidgets.QTabWidget, app: AppEntry, gui_update_signal: QtCore.pyqtSignal):
        super().__init__(parent)
        self._app_info = app
        self._app_button = AppButton(parent, app.icon)
        self._app_name_label = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self._app_channel_cbox = QtWidgets.QComboBox(parent)
        self._gui_update_signal = gui_update_signal

        self.setObjectName(parent.objectName() + app.name)  # to find it for tests
        self.setSpacing(5)

        # size policies
        self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self._app_button.setSizePolicy(size_policy)

        self._app_button.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._app_button.setToolTip(str(app.conan_ref))

        self.addWidget(self._app_button)
        # self._app_name_label.setSizePolicy(size_policy)
        self._app_name_label.setAlignment(Qt.AlignCenter)
        self._app_name_label.setText(app.name)
        self.addWidget(self._app_name_label)

        self._app_version_cbox.addItem(app.conan_ref.version)
        self._app_version_cbox.setDisabled(True)
        self._app_version_cbox.setDuplicatesEnabled(False)
        self.addWidget(self._app_version_cbox)

        self._app_channel_cbox.addItem(app.conan_ref.channel)
        self._app_channel_cbox.setDisabled(True)
        self._app_channel_cbox.setDuplicatesEnabled(False)
        self.addWidget(self._app_channel_cbox)

        self._app_button.clicked.connect(self.app_clicked)
        self._app_version_cbox.currentIndexChanged.connect(self.version_selected)
        self._app_channel_cbox.currentIndexChanged.connect(self.channel_selected)

    def update_entry(self, settings: Settings):
        # set icon and ungrey if package is available
        if self._app_info.executable.is_file():
            self._app_button.set_icon(self._app_info.icon)
            self._app_button.ungrey_icon()

        if len(self._app_info.versions) > 0 and self._app_version_cbox.count() != len(self._app_info.versions):  # on nums changed
            self._app_version_cbox.clear()
            self._app_channel_cbox.clear()
            self._app_version_cbox.addItems(self._app_info.versions)
            self._app_channel_cbox.addItems(self._app_info.channels)
            try:  # TODO
                self._app_version_cbox.setCurrentIndex(self._app_info.versions.index(self._app_info.version))
                self._app_channel_cbox.setCurrentIndex(self._app_info.channels.index(self._app_info.channel))
            except Exception:
                pass
            self._app_version_cbox.setDisabled(False)
            self._app_channel_cbox.setDisabled(False)

        if settings.get(DISPLAY_APP_VERSIONS):
            self._app_version_cbox.show()
        else:
            self._app_version_cbox.hide()
        if settings.get(DISPLAY_APP_CHANNELS):
            self._app_channel_cbox.show()
        else:
            self._app_channel_cbox.hide()

    def app_clicked(self):
        """ Callback for opening the executable on click """
        run_file(self._app_info.executable, self._app_info.is_console_application, self._app_info.args)

    def version_selected(self, index):
        if not self._app_version_cbox.isEnabled():
            return
        if index == -1:  # on clear
            return
        if self._app_info.version == self._app_version_cbox.currentText():  # no change
            return
        self._app_button.grey_icon()
        # update channels to match version
        self._app_channel_cbox.clear()  # reset cbox
        self._app_channel_cbox.addItems([self._app_info.INVALID_DESCR] + self._app_info.channels)
        self._app_channel_cbox.setCurrentIndex(0)

        self._app_info.channel = self._app_info.INVALID_DESCR
        self._app_info.version = self._app_version_cbox.currentText()

    def channel_selected(self, index):
        if not self._app_channel_cbox.isEnabled():
            return
        if index == -1:
            return
        if self._app_info.channel == self._app_channel_cbox.currentText():
            return
        self._app_button.grey_icon()
        self._app_info.channel = self._app_channel_cbox.currentText()


class TabUiGrid(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QTabWidget, name):
        super().__init__(parent)
        self.apps: List[AppUiEntry] = []
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        self.tab_grid_layout = QtWidgets.QGridLayout()  # self.tab_scroll_area
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + name)
        self.tab_scroll_area_layout = QtWidgets.QVBoxLayout(self.tab_scroll_area_widgets)
        self.setObjectName("tab_" + name)

        self.tab_scroll_area_layout.setContentsMargins(0, 0, 0, 0)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setGeometry(QtCore.QRect(0, 0, 830, 462))
        self.tab_layout.setContentsMargins(2, 0, 2, 0)
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(Qt.AlignCenter)
        self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        self.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)

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
        self.tab_grid_layout.setContentsMargins(8, 8, 8, 8)
        self.tab_grid_layout.setSpacing(5)

        self.tab_scroll_area_layout.addLayout(self.tab_grid_layout)
        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.tab_layout.addWidget(self.tab_scroll_area)
