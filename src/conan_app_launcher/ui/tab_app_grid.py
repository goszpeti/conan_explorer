from typing import List


from PyQt5 import QtCore, QtWidgets
import conan_app_launcher as this
from conan_app_launcher.components import AppConfigEntry
from conan_app_launcher.ui.app_link import AppLink

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabAppGrid(QtWidgets.QWidget):

    def __init__(self, tab_info, parent: QtWidgets.QTabWidget, rows: int, coloumns: int, update_signal):
        super().__init__(parent)
        self.tab_info = tab_info
        self.apps: List[AppLink] = []
        self.rows = rows
        self.coloumns = coloumns
        self.update_signal = update_signal
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        self.tab_grid_layout = QtWidgets.QGridLayout()  # self.tab_scroll_area
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.tab_info.name)
        self.tab_scroll_area_layout = QtWidgets.QVBoxLayout(self.tab_scroll_area_widgets)
        self.setObjectName("tab_" + self.tab_info.name)

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
        self.add_app_links()

    def add_app_links(self):
        row = 0
        column = 0
        for app_info in self.tab_info.get_app_entries():
            # add in order of occurence
            app = AppLink(app_info, self.update_signal, parent=self.tab_scroll_area_widgets)
            self.apps.append(app)
            self.tab_grid_layout.addLayout(app, row, column, 1, 1)
            column += 1
            if column == self.coloumns + 1:
                column = 0
                row += 1
        if row < self.rows:  # only add + button, if max rows is not reached
            self.add_new_app_link(self, row, column)

    def add_new_app_link(self, tab, row, column):
        app_info = AppConfigEntry()
        app_info.name = "Add new Link"
        app_info.icon = str(this.base_path / "assets" / "new_app_icon.png")
        app_link = AppLink(app_info, self.update_signal,
                           parent=tab.tab_scroll_area_widgets, is_new_link=True)
        app_link._app_button.ungrey_icon()

        tab.tab_grid_layout.addLayout(app_link, row, column, 1, 1)
