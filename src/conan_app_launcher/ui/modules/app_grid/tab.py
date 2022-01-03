from typing import List
from conan_app_launcher.ui.modules.app_grid.model import UiAppLinkModel, UiTabModel

from .common.app_edit_dialog import EditAppDialog
from .app_link import AppLink
from PyQt5 import QtCore, QtWidgets, QtGui

# define Qt so we can use it like the namespace in C++
Qt = QtCore.Qt


class TabGrid(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QTabWidget, model: UiTabModel):
        super().__init__(parent)
        self.model = model
        self.app_links: List[AppLink] = []  # list of refs to app links
        self.tab_scroll_area = None

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
        self.tab_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.tab_scroll_area.setAlignment(Qt.AlignTop)
        self.tab_scroll_area.setUpdatesEnabled(True)
        self.tab_scroll_area.setWidgetResizable(False)
        self.tab_scroll_area_widgets.setSizePolicy(size_policy)
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)
        self.tab_grid_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)  # SetMinimumSize needed!

        self.tab_grid_layout.setContentsMargins(8, 8, 8, 8)
        self.tab_grid_layout.setSpacing(4)

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.tab_layout.addWidget(self.tab_scroll_area)

    def get_max_columns(self):
        if self.tab_scroll_area:
            width = self.tab_scroll_area.geometry().width()
            max_columns = int(width / (AppLink.MAX_WIDTH))
            if max_columns == 0:
                max_columns = 1
            return max_columns
        return 1  # always enable one row

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        self.redraw_grid()

    def load(self):
        self.init_app_grid()
        # no need to call load_apps_from_model - will be called by resize event on drawing the window

    def load_apps_from_model(self):
        row = 0
        column = 0
        max_columns = self.get_max_columns()

        for app_model in self.model.apps:
            # add in order of occurence
            app_link = AppLink(self, app_model)
            app_link.load()
            self.app_links.append(app_link)
            self.tab_grid_layout.addLayout(app_link, row, column)
            self.tab_grid_layout.setColumnMinimumWidth(column, AppLink.MAX_WIDTH - 8)
            column += 1
            if column == max_columns:
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
        current_row = int(len(self.model.apps) / self.get_max_columns())  # count from 0
        current_column = int(len(self.model.apps) % self.get_max_columns())  # count from 0 to count

        self.app_links.append(app_link)
        self.model.apps.append(app_link.model)
        self.tab_grid_layout.addLayout(app_link, current_row, current_column, 1, 1)
        self.tab_grid_layout.setColumnMinimumWidth(current_column, AppLink.MAX_WIDTH - 8)
        self.tab_grid_layout.update()

    def remove_all_app_links(self):
        """ 
        Clears all AppLink by actually deleting them. Manipulating self.tab_grid_layout does not work!
        Can then be reloaded with load_apps_from_model.
        """
        # remove spacer - needed so, the layout can be resized correctly, if layout shifts
        self.tab_grid_layout.removeItem(self._v_spacer)
        reverse_app_links = self.app_links
        reverse_app_links.reverse()
        for app_link in self.app_links:
            app_link.delete()
        self.app_links = []

    def redraw_grid(self):
        """ Works only as long as the order does not change. Used for resizing the window. """
        if self.tab_scroll_area:  # don't call on init
            self.remove_all_app_links()
            self.load_apps_from_model()

