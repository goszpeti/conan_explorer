from typing import List, Optional

import conan_explorer.app as app  # using global module pattern
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLayout, QScrollArea, QSizePolicy, QFrame,
                             QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

from .app_link import ListAppLink # ,GridAppLink
from .dialogs import AppEditDialog
from .model import UiAppLinkModel, UiTabModel


class TabScrollAreaWidgets(QWidget):
    def __init__(self, parent: Optional['QWidget'] = None):
        super().__init__(parent)


class TabList(QWidget):
    SPACING = 10

    def __init__(self, parent: QTabWidget, model: UiTabModel):
        super().__init__(parent)
        self.model = model
        self._parent_tab = parent
        self.app_links: List[ListAppLink] = []  # list of refs to app links
        self._initialized = False
        self._columns_count = 0
        self._v_spacer = QSpacerItem(
            20, 2000, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    def load(self, offset=0):
        self.init_app_grid()
        self.load_apps_from_model(offset=offset)

    def load_apps_from_model(self, force_reload=False, offset=0):
        if not self.app_links or force_reload:
            for app_model in self.model.apps:
                app_link = ListAppLink(self, self, app_model)
                app_link.load()
                self.app_links.append(app_link)
        for app_link in self.app_links:
            # add in order of occurence
            self.tab_layout.addWidget(app_link)
            app_link.show()
        # spacer for compressing app links, when hiding cboxes
        self.tab_layout.addItem(self._v_spacer)

    def open_app_link_add_dialog(self, new_model: Optional[UiAppLinkModel] =None):
        if not new_model:
            new_model = UiAppLinkModel()
            new_model.parent = self.model
        # save for testing
        self._edit_app_dialog = AppEditDialog(new_model, parent=self)
        reply = self._edit_app_dialog.exec()
        if reply == AppEditDialog.DialogCode.Accepted:
            self.model.apps.append(new_model)
            self.model.save()
            self.redraw(force=True)
            return new_model # for testing
        return None

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
            # TODO this a leak, currently it does not delete everything!
            app_link.hide()
        if force:
            self.app_links = []

    def redraw(self, force=False):
        if self._initialized:  # don't call on init
            self.remove_all_app_links(force)
            self.load_apps_from_model(force)

    def init_app_grid(self):
        self.setObjectName("tab_" + self.model.name)
        self.setContentsMargins(0, 0, 0, 0)
        # this is a dummy, because tab_scroll_area needs a layout
        self.tab_layout = QVBoxLayout(self)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.setLayout(self.tab_layout)

        # makes it possible to have a scroll bar
        self.tab_scroll_area = QScrollArea(self)
        self.tab_scroll_area.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area.setFrameStyle(QFrame.Shape.NoFrame)

        self.tab_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tab_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab_scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.tab_scroll_area.setWidgetResizable(True)
        # this holds all the app links, which are layouts
        self.tab_scroll_area_widgets = TabScrollAreaWidgets(self.tab_scroll_area)
        self.tab_scroll_area_widgets.setContentsMargins(0, 0, 0, 0)
        self.tab_scroll_area_widgets.setObjectName("tab_widgets_" + self.model.name)
        self._initialized = True

        self.tab_layout = QVBoxLayout(self.tab_scroll_area_widgets)
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred,
                                    QSizePolicy.Policy.MinimumExpanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.tab_scroll_area_widgets.setSizePolicy(size_policy)
        self.tab_scroll_area_widgets.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tab_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.tab_layout.setSpacing(self.SPACING)
        self.tab_layout.setContentsMargins(0, 0, 5, 0)

        self.tab_scroll_area.setWidget(self.tab_scroll_area_widgets)
        self.layout().addWidget(self.tab_scroll_area)

    def add_app_link_to_tab(self, app_link: ListAppLink):
        """ To be called from a child AppLink """
        self.app_links.append(app_link)
        self.model.apps.append(app_link.model)
        self.tab_layout.insertWidget(-1, app_link) # -1 is end
        self.tab_layout.update()

