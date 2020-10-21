import subprocess

from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.logger import Logger
from PyQt5 import QtCore, QtGui, QtWidgets

from conan_app_launcher.ui.qt.app_button import AppButton

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

# TODO Clean up


class AppUiEntry(QtWidgets.QVBoxLayout):

    def __init__(self, parent: QtWidgets.QTabWidget, app: AppEntry):
        super().__init__()
        self._app_info = app
        self._app_button = AppButton(parent, app.icon)
        self._app_name = QtWidgets.QLabel(parent)
        self._app_version_cbox = QtWidgets.QComboBox(parent)
        self.setObjectName(parent.objectName() + app.name)

        # size policies
        self.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self._app_button.sizePolicy().hasHeightForWidth())
        self._app_button.setSizePolicy(size_policy)
        self._app_button.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self._app_button.setToolTip(str(app.package_id))
        self.addWidget(self._app_button)
        self._app_name.setSizePolicy(size_policy)
        self._app_name.setAlignment(QtCore.Qt.AlignCenter)
        self._app_name.setText(app.name)
        self.addWidget(self._app_name)

        self._app_version_cbox.addItem(app.package_id.version)
        # TODO unlock when version feature is implemented
        self._app_version_cbox.setDisabled(True)

        self.addWidget(self._app_version_cbox)

        self._app_button.clicked.connect(self.app_clicked)

    def update_entry(self):
        # set icon and ungrey
        self._app_button.set_icon(self._app_info.icon, greyed_out=False)

    def app_clicked(self):
        """ Callback for opening the executable on click """
        if self._app_info.executable.is_file():
            subprocess.Popen(str(self._app_info.executable))


class TabUiGrid(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        self.apps = []  # AppUiEntry
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        self.tab_grid_layout = QtWidgets.QGridLayout(self)
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + name)
        self.tab_scroll_area_layout = QtWidgets.QVBoxLayout(self.tab_scroll_area_widgets)
        self.setObjectName("tab_" + name)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.tab_scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        self.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(QtCore.Qt.LeftToRight)

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

        self.tab_scroll_area_layout.addLayout(self.tab_grid_layout)
        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.tab_layout.addWidget(self.tab_scroll_area)
