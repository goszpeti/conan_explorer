from typing import List
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel, UiTabModel

from .common.app_edit_dialog import EditAppDialog
from .app_link import AppLink
from PyQt5 import QtCore, QtWidgets

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabGrid(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QTabWidget, max_rows: int, max_columns: int, model: UiTabModel):
        super().__init__(parent)
        self.model = model
        self.max_rows = max_rows  # TODO currently not handled correctly
        self.max_columns = max_columns
        self.app_links: List[AppLink] = []  # list of refs to app links

    def init_app_grid(self):
        self.setObjectName("tab_" + self.model.name)

        # this is a dummy, because tab_scroll_area needs a layout
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self._v_spacer = QtWidgets.QSpacerItem(
            20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # makes it possible to have a scroll bar
        self.tab_scroll_area = QtWidgets.QScrollArea(self)
        # this holds all the app links, which are layouts
        self.tab_scroll_area_widgets = QtWidgets.QWidget(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.model.name)
        # grid layout for tab_scroll_area_widgets
        self.tab_grid_layout = QtWidgets.QGridLayout(self.tab_scroll_area_widgets)

        # set minimum on vertical is needed, so the app links very shrink,
        # when a dropdown is hidden
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.tab_layout.setContentsMargins(2, 0, 2, 0)
        self.tab_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.tab_scroll_area.setSizePolicy(size_policy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setAlignment(Qt.AlignTop)
        self.tab_scroll_area.setUpdatesEnabled(True)
        self.tab_scroll_area.setWidgetResizable(False)
        self.tab_scroll_area_widgets.setSizePolicy(size_policy)
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)
        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)  # SetMinimumSize needed!
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

    def load(self):
        self.init_app_grid()
        row = 0
        column = 0
        for app_model in self.model.apps:
            # add in order of occurence
            app_link = AppLink(self, app_model)
            app_link.load()
            self.app_links.append(app_link)
            self.tab_grid_layout.addLayout(app_link, row, column)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1
        # spacer for compressing app links, when hiding cboxes
        self.tab_grid_layout.addItem(self._v_spacer, row+1, 0)

    def open_app_link_add_dialog(self, new_model: UiAppLinkModel = None):
        if not new_model:
            new_model = UiAppLinkModel()
            new_model.parent = self.model
        # save for testing
        self._edit_app_dialog = EditAppDialog(new_model, parent=self.parentWidget())
        reply = self._edit_app_dialog.exec_()
        if reply == EditAppDialog.Accepted:
            self._edit_app_dialog.save_data()
            app_link = AppLink(self, new_model)
            app_link.load()
            app_link.model.update_from_cache()
            self.add_app_link_to_tab(app_link)
            self.model.save()  # TODO this should happen on apps.append
            return app_link  # for testing
        return None

    def add_app_link_to_tab(self, app_link: AppLink):
        """ To be called from a child AppLink """
        current_row = int(len(self.model.apps) / self.max_columns)  # count from 0
        current_column = len(self.model.apps) % self.max_columns  # count from 0 to 3

        self.app_links.append(app_link)
        self.model.apps.append(app_link.model)
        self.tab_grid_layout.addLayout(app_link, current_row, current_column, 1, 1)

    def reset_grid(self):
        for app_link in self.app_links:
            self.tab_grid_layout.removeItem(app_link)
        row = 0
        column = 0
        for app_link in self.app_links:
            self.tab_grid_layout.addLayout(app_link, row, column)
            column += 1
            if column == self.max_columns:
                column = 0
                row += 1

    def remove_app_link_from_tab(self, app_link: AppLink):
        """ To be called from a child AppLink """
        self.model.apps.remove(app_link.model)
        self.app_links.remove(app_link)
        self.reset_grid()
