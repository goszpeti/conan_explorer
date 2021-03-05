from PyQt5 import QtCore, QtWidgets

import conan_app_launcher as this
from conan_app_launcher.components import AppConfigEntry, TabConfigEntry
from conan_app_launcher.ui.app_grid.app_link import AppLink


# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabAppGrid(QtWidgets.QWidget):
    app_link_added = QtCore.pyqtSignal(AppLink)
    app_link_removed = QtCore.pyqtSignal(AppLink)

    def __init__(self, parent: QtWidgets.QTabWidget, config_data: TabConfigEntry,
                 max_rows: int, max_columns: int):
        super().__init__(parent)
        self.config_data = config_data
        self.app_links = []  # list of refs to app links
        self.max_rows = max_rows
        self.max_columns = max_columns
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.config_data.name)
        self.tab_grid_layout = QtWidgets.QGridLayout(self.tab_scroll_area_widgets)  # self.tab_scroll_area
        self.setObjectName("tab_" + self.config_data.name)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setGeometry(QtCore.QRect(0, 0, 830, 462))
        self.tab_layout.setContentsMargins(2, 0, 2, 0)
        self.tab_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setWidgetResizable(True)
        self.tab_scroll_area.setAlignment(Qt.AlignCenter)
        self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        self.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)

        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.tab_grid_layout.setColumnMinimumWidth(0, 193)
        self.tab_grid_layout.setColumnMinimumWidth(1, 193)
        self.tab_grid_layout.setColumnMinimumWidth(2, 193)
        self.tab_grid_layout.setColumnMinimumWidth(3, 193)

        self.tab_grid_layout.setRowMinimumHeight(0, 100)
        self.tab_grid_layout.setRowMinimumHeight(1, 100)
        self.tab_grid_layout.setRowMinimumHeight(2, 100)
        self.tab_grid_layout.setContentsMargins(8, 8, 8, 8)
        self.tab_grid_layout.setSpacing(4)

        self.app_link_added.connect(self.on_app_link_add)
        self.app_link_removed.connect(self.on_app_link_remove)

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.tab_layout.addWidget(self.tab_scroll_area)
        self.add_all_app_links()

    def add_all_app_links(self):
        row = 0
        column = 0
        for app_info in self.config_data.get_app_entries():
            # add in order of occurence
            app_link = AppLink(self, app_info, self.app_link_added, self.app_link_removed)
            self.app_links.append(app_link)
            self.tab_grid_layout.addLayout(app_link, row, column, 1, 1)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1

    def open_app_link_add_dialog(self):
        app_info = AppConfigEntry()
        app_link = AppLink(self, app_info, self.app_link_added, self.app_link_removed)
        app_link.open_edit_dialog()

    def on_app_link_add(self, app_link):
        current_row = int(len(self.config_data.get_app_entries()) / self.max_columns)  # count from 0
        current_column = len(self.config_data.get_app_entries()) % self.max_columns  # count from 0 to 3

        self.app_links.append(app_link)
        self.config_data.add_app_entry(app_link.config_data)
        self.tab_grid_layout.addLayout(app_link, current_row, current_column, 1, 1)

    def on_app_link_remove(self, app_link: AppLink):
        self.config_data.remove_app_entry(app_link.config_data)
        self.app_links.remove(app_link)

        # for child in self.tab_scroll_area_widgets.children():
        #     if isinstance(child, QtWidgets.QWidget):
        #         print("deleting" + str(child))
        #         child.deleteLater()
        for child in self.tab_grid_layout.children():
            self.tab_grid_layout.removeItem(child)
        # self.tab_grid_layout.removeItem(app_link)
        del app_link
        row = 0
        column = 0
        for app in self.app_links:
            # add in order of occurence
            self.tab_grid_layout.addLayout(app, row, column, 1, 1)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1
