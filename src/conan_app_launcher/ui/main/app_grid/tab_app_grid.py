from typing import List
import conan_app_launcher as this

from conan_app_launcher.ui.app_grid.app_edit_dialog import EditAppDialog
from conan_app_launcher.ui.app_grid.app_link import AppLink
from PyQt5 import QtCore, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabAppGrid(QtWidgets.QWidget):
    

    def __init__(self, parent: QtWidgets.QTabWidget, config_data,
                 max_rows: int, max_columns: int):
        super().__init__(parent)
        self.config_data = config_data
        self.setObjectName("tab_" + self.config_data.name)

        self.app_links: List[AppLink] = []  # list of refs to app links
        self.max_rows = max_rows # TODO currently not handled correctly
        self.max_columns = max_columns
        # this is a dummy, because tab_scroll_area needs a layout
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self._v_spacer = QtWidgets.QSpacerItem(
            20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # makes it possible to have a scroll bar
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        # this holds all the app links, which are layouts
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.config_data.name)
        # grid layout for tab_scroll_area_widgets
        self.tab_grid_layout = QtWidgets.QGridLayout(self.tab_scroll_area_widgets)

        # set maximum on vertical is needed, so the app links very shrink, when a dropdown is hidden
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)  # Maximum
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        # own_size_poicy = sizePolicy
        # own_size_poicy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        #self.setSizePolicy(sizePolicy)

        self.tab_layout.setContentsMargins(2, 0, 2, 0)
        self.tab_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.tab_scroll_area.setSizePolicy(sizePolicy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setAlignment(Qt.AlignTop)
        self.tab_scroll_area.setUpdatesEnabled(True)
        self.tab_scroll_area.setWidgetResizable(False)
        #self.tab_scroll_area_widgets.setGeometry(QtCore.QRect(0, 0, 811, 439))
        self.tab_scroll_area_widgets.setSizePolicy(sizePolicy)
        #elf.tab_scroll_area_widgets.setMinimumSize(QtCore.QSize(752, 359))
        #self.tab_scroll_area_widgets.setBaseSize(QtCore.QSize(752, 359))
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)
        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)  # SetMinimumSize needed!
        self.tab_grid_layout.setColumnMinimumWidth(0, 193)
        self.tab_grid_layout.setColumnMinimumWidth(1, 193)
        self.tab_grid_layout.setColumnMinimumWidth(2, 193)
        self.tab_grid_layout.setColumnMinimumWidth(3, 193)

        self.tab_grid_layout.setRowMinimumHeight(0, 100)
        self.tab_grid_layout.setRowMinimumHeight(1, 100)
        self.tab_grid_layout.setRowMinimumHeight(2, 100)
        #self.tab_grid_layout.setRowMinimumHeight(3, 100)

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
            self.tab_grid_layout.addLayout(app_link, row, column)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1
        # spacer for compressing app links, when hiding cboxes
        self.tab_grid_layout.addItem(self._v_spacer, row+1,0)

    def open_app_link_add_dialog(self, config_data):  # = AppLinkModel()
        # save for testing
        self._edit_app_dialog = EditAppDialog(config_data, self)
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            config_data.update_from_cache()  # instantly use local paths and pkgs
            app_link = AppLink(self, config_data)
            self.add_app_link_to_tab(app_link)
            main_window.save_config()
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
