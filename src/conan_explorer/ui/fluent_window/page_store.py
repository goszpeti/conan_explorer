from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, TypeVar

from PySide6.QtWidgets import QPushButton, QWidget

from . import gen_obj_name
from .side_menu import SideSubMenu

if TYPE_CHECKING:
    from ..plugin.handler import PluginInterfaceV1


class WidgetNotFoundException(Exception):
    """Raised, when a widget searched for, ist in the parent container."""

    pass


class PageStore:
    """Saves all relevant information for pages accessible from the left menu
    and provides easy retrieval methods for all members."""

    def __init__(self) -> None:
        self._page_widgets: Dict[
            str, Tuple[QPushButton, QWidget, Optional[SideSubMenu], str]
        ] = {}

    def get_button_by_name(self, name: str) -> QPushButton:
        return self._page_widgets[gen_obj_name(name)][0]

    def get_page_by_name(self, name: str) -> QWidget:
        return self._page_widgets[gen_obj_name(name)][1]

    def get_side_menu_by_name(self, name: str) -> "Optional[SideSubMenu]":
        return self._page_widgets[gen_obj_name(name)][2]

    def get_display_name_by_name(self, name: str) -> str:
        return self._page_widgets[gen_obj_name(name)][3]

    def get_side_menu_by_type(self, type_name: Type) -> "Optional[SideSubMenu]":
        for _, (_, page, menu, _) in self._page_widgets.items():
            if page.__class__.__name__ == type_name.__name__:
                return menu
        raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

    def get_button_by_type(self, type_name: Type) -> QPushButton:
        for _, (button, page, _, _) in self._page_widgets.items():
            if page.__class__.__name__ == type_name.__name__:
                return button
        raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

    T = TypeVar("T")

    def get_page_by_type(self, type_name: Type[T]) -> T:
        for (
            _,
            (_, page, _, _),
        ) in self._page_widgets.items():
            if page.__class__.__name__ == type_name.__name__:
                return page  # type: ignore
        raise WidgetNotFoundException(f"{type_name} not in page_widgets!")

    def get_all_buttons(self):
        buttons = []
        for button, _, _, _ in self._page_widgets.values():
            buttons.append(button)
        return buttons

    def get_all_pages(self) -> List["PluginInterfaceV1"]:
        pages = []
        for (
            _,
            (_, page, _, _),
        ) in self._page_widgets.items():
            pages.append(page)
        return pages

    def add_new_page(self, name: str, button, page, right_sub_menu):
        self._page_widgets[gen_obj_name(name)] = (button, page, right_sub_menu, name)

    def remove_page_by_name(self, name: str):
        button, widget, menu, _ = self._page_widgets.pop(gen_obj_name(name))
        button.hide()
        widget.hide()
        button.deleteLater()
        if menu:
            menu.deleteLater()
        widget.deleteLater()

    def remove_page_extras_by_name(self, name: str):
        """Remove page but not the widget itself, in case it is managed
        by another mechanism like plugins"""
        try:
            button, _, menu, _ = self._page_widgets.pop(gen_obj_name(name))
            button.hide()
            button.deleteLater()
            if menu:
                menu.deleteLater()
        except Exception:  # fail silently - nothing to remove
            pass
