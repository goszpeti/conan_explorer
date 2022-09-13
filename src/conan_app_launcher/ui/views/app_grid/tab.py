from typing import List, Optional

import conan_app_launcher.app as app  # using global module pattern
from conan_app_launcher.settings import APPLIST_ENABLED
from conan_app_launcher.ui.fluent_window import RIGHT_MENU_MAX_WIDTH
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QLayout, QScrollArea, QSizePolicy, QFrame,
                             QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

from .app_link import AppLinkBase, GridAppLink, ListAppLink
from .dialogs import AppEditDialog
from .model import UiAppLinkModel, UiTabModel


class TabScrollAreaWidgets(QWidget):
    def __init__(self, parent: Optional['QWidget'] = None):
        super().__init__(parent)


class TabBase(QWidget):
    SPACING = 10

    def __init__(self, parent: QTabWidget, model: UiTabModel):
        super().__init__(parent)
        self.model = model
        self._app_link_type = AppLinkBase
        self.app_links: List[AppLinkBase] = []  # list of refs to app links
        self._initialized = False
        self._columns_count = 0
        self._v_spacer = QSpacerItem(
            20, 2000, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def init_app_grid(self):
        self.setObjectName("tab_" + self.model.name)
        self.setContentsMargins(0, 0, 0, 0)
        # this is a dummy, because tab_scroll_area needs a layout
        self.tab_layout = QVBoxLayout(self)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.tab_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.tab_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.setLayout(self.tab_layout)

        # makes it possible to have a scroll bar
        self.tab_scroll_area = QScrollArea(self)
        self.tab_scroll_area.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area.setFrameStyle(QFrame.NoFrame)

        #self.tab_scroll_area.setSizePolicy(size_policy)
        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tab_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tab_scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        #self.tab_scroll_area.setUpdatesEnabled(True)
        self.tab_scroll_area.setWidgetResizable(True)
        # this holds all the app links, which are layouts
        self.tab_scroll_area_widgets = TabScrollAreaWidgets(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.model.name)
        self._initialized = True
    
    def get_max_columns(self, offset=0) -> int:
        return 1

    def load(self, offset=0):
        self.init_app_grid()
        self.load_apps_from_model(offset=offset)

    def load_apps_from_model(self, force_reload=False, offset=0):
        if not self.app_links or force_reload:
            for app_model in self.model.apps:
                app_link = self._app_link_type(self, self, app_model)
                app_link.load()
                self.app_links.append(app_link)

    def open_app_link_add_dialog(self, new_model: Optional[UiAppLinkModel] =None):
        if not new_model:
            new_model = UiAppLinkModel()
            new_model.parent = self.model
        # save for testing
        self._edit_app_dialog = AppEditDialog(new_model, parent=self)
        reply = self._edit_app_dialog.exec_()
        if reply == AppEditDialog.Accepted:
            self.model.apps.append(new_model)
            self.model.save()
            self.redraw(force=True)
            return new_model # for testing
        return None

    def add_app_link_to_tab(self, app_link: AppLinkBase):
        """ To be called from a child AppLink """
        pass

    def remove_all_app_links(self, force=False):
        """ 
        Clears all AppLinks.
        Can then be reloaded with load_apps_from_model.
        """
        # remove spacer - needed so, the layout can be resized correctly, if layout shifts
        self.tab_layout.removeItem(self._v_spacer)
        # self.tab_layout.removeItem(self._h_spacer)
        for app_link in self.app_links:
            self.tab_layout.removeWidget(app_link)
            if force:
                # TODO this a leak, currently it does not delete everything!
                app_link.hide()
                app_link.delete()
            else:
                app_link.hide()
        if force:
            self.app_links = []

    def redraw(self, force=False):
        """ Works only as long as the order does not change. Used for resizing the window. """
        # only if column size changes
        max_columns = self.get_max_columns()
        if max_columns in [self._columns_count, 1] and not force:  # already correct -> 1 means this is still not real width
            return
        if self._initialized:  # don't call on init
            self.remove_all_app_links(force)
            self.load_apps_from_model(force)


class TabGrid(TabBase):
    def __init__(self, parent: QTabWidget, model: UiTabModel):
        super().__init__(parent, model)
        self._app_link_type = GridAppLink

    def init_app_grid(self):
        super().init_app_grid()

        self.tab_layout = QGridLayout(self.tab_scroll_area_widgets)
        # set minimum on vertical is needed, so the app links shrink,
        # when a dropdown is hidden
        size_policy = QSizePolicy(QSizePolicy.Minimum,
                                    QSizePolicy.Minimum)
        self.tab_layout.setSizeConstraint(QLayout.SetMinimumSize)  # SetMinimumSize needed!

        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.tab_scroll_area_widgets.setSizePolicy(size_policy)
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)
        self.tab_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.tab_layout.setSpacing(self.SPACING)
        self.tab_layout.setContentsMargins(0, 0, 5, 0)

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.layout().addWidget(self.tab_scroll_area)

    def add_app_link_to_tab(self, app_link: AppLinkBase):
        """ To be called from a child AppLink """
        current_row = int(len(self.model.apps) / self.get_max_columns())  # count from 0
        current_column = int(len(self.model.apps) % self.get_max_columns())  # count from 0 to count

        self.app_links.append(app_link)
        self.model.apps.append(app_link.model)
        self.tab_layout.addWidget(app_link, current_row, current_column)
        self.tab_layout.setColumnMinimumWidth(current_column, self._app_link_type.max_width() - 8)
        self.tab_layout.update()

    def get_max_columns(self, offset=0):
        if self._initialized:
            width = self.parent().width()
            max_columns = int((width + offset) / (GridAppLink.max_width()))
            if max_columns == 0:
                max_columns = 1
            return max_columns
        return 1  # always enable one row

    def load_apps_from_model(self, force_reload=False, offset=0):
        super().load_apps_from_model()
        row = 0
        column = 0
        max_columns = self.get_max_columns(offset)
        self._columns_count = max_columns
        for app_link in self.app_links:
            # add in order of occurence
            self.tab_layout.addWidget(app_link, row, column, 1, 1)
            self.tab_layout.setColumnMinimumWidth(column, app_link.max_width() - (2 * self.SPACING))
            column += 1
            if column == max_columns:
                column = 0
                row += 1
            app_link.show()
        # spacer for compressing app links, when hiding cboxes
        self.tab_layout.addItem(self._v_spacer, row + 1, 0)
        self.tab_layout.addItem(QSpacerItem(
            2000, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), max_columns+1, 0, 0, 0)
        self.tab_layout.setColumnStretch(max_columns+1, 1)


class TabList(TabBase):
    def __init__(self, parent: QTabWidget, model: UiTabModel):
        super().__init__(parent, model)
        self._app_link_type = ListAppLink


    def init_app_grid(self):
        super().init_app_grid()
        self.tab_layout = QVBoxLayout(self.tab_scroll_area_widgets)
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                    QSizePolicy.MinimumExpanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.tab_scroll_area_widgets.setSizePolicy(size_policy)
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LeftToRight)
        self.tab_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.tab_layout.setSpacing(self.SPACING)
        self.tab_layout.setContentsMargins(0, 0, 5, 0)

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.layout().addWidget(self.tab_scroll_area)

    def get_max_columns(self, offset=0):
        if self._initialized:
            width = self.parent().width()
            max_columns = int((width + offset) / (self._app_link_type.max_width()))
            if max_columns == 0:
                max_columns = 1
            return max_columns
        return 1  # always enable one row

    def add_app_link_to_tab(self, app_link: AppLinkBase):
        """ To be called from a child AppLink """
        self.app_links.append(app_link)
        self.model.apps.append(app_link.model)
        self.tab_layout.insertWidget(-1, app_link) # -1 is end
        self.tab_layout.update()

    def load_apps_from_model(self, force_reload=False, offset=0):
        super().load_apps_from_model()
        for app_link in self.app_links:
            # add in order of occurence
            self.tab_layout.addWidget(app_link)
            app_link.show()
        # spacer for compressing app links, when hiding cboxes
        self.tab_layout.addItem(self._v_spacer)

