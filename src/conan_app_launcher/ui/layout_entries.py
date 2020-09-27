import os

from conan_app_launcher.config_file import AppEntry
from conan_app_launcher.logger import Logger
from PyQt5 import QtCore, QtGui, QtWidgets

from .qt.app_button import AppButton

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt

# TODO Clean up


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
        """ Calback for opening the executable on click """
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
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_scroll_area.sizePolicy().hasHeightForWidth())
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
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
