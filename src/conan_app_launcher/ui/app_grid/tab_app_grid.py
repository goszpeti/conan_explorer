import conan_app_launcher as this
from conan_app_launcher.components import TabConfigEntry
from conan_app_launcher.components.config_file import AppConfigEntry
from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog
from conan_app_launcher.ui.app_grid.app_link import AppLink
from PyQt5 import QtCore, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabAppGrid(QtWidgets.QWidget):
    

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

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.tab_layout.addWidget(self.tab_scroll_area)
        self.add_all_app_links()

    def add_all_app_links(self):
        row = 0
        column = 0
        for app_info in self.config_data.get_app_entries():
            # add in order of occurence
            app_link = AppLink(self, app_info)
            self.app_links.append(app_link)
            self.tab_grid_layout.addLayout(app_link, row, column, 1, 1)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1

    def open_app_link_add_dialog(self, config_data = AppConfigEntry()):
        # TODO save for testing
        self._edit_app_dialog = EditAppDialog(config_data, self)
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            config_data.update_from_cache()  # instantly use local paths and pkgs
            app_link = AppLink(self, config_data)
            self.add_app_link_to_tab(app_link)
            this.main_window.save_config()
            return app_link  # for testing
        return None

    def add_app_link_to_tab(self, app_link):
        """ To be called from a child AppLink """
        current_row = int(len(self.config_data.get_app_entries()) / self.max_columns)  # count from 0
        current_column = len(self.config_data.get_app_entries()) % self.max_columns  # count from 0 to 3

        self.app_links.append(app_link)
        self.config_data.add_app_entry(app_link.config_data)
        self.tab_grid_layout.addLayout(app_link, current_row, current_column, 1, 1)

    def remove_app_link_from_tab(self, app_link: AppLink):
        """ To be called from a child AppLink """
        self.config_data.remove_app_entry(app_link.config_data)
        self.app_links.remove(app_link)
        self.tab_grid_layout.removeItem(app_link)
        app_link.setParent(None)
        del app_link
