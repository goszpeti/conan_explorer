import threading
import time
import types
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Callable, Optional

from conan_app_launcher.app.logger import Logger


if TYPE_CHECKING:
    from conan_app_launcher.app.component_reg import ComponentRegistry


class Component:
    """ Base class for all components """

    def __init__(self, components: Optional["ComponentRegistry"] = None, enabled=True):
        self._comps = components
        self._logger = Logger()
        self._disabled = not enabled
        self._ready = True

    @property
    def is_ready(self) -> bool:
        """ Returns true, if component is ready to be used."""
        return self._ready

    @property
    def is_disabled(self):
        """
        The component can signal it is disabled, if it does not work correctly
        and its values are not to be used. (Component will always return an instance)
        """
        return self._disabled

    def stop(self):
        """ Stop this component. """
        pass

