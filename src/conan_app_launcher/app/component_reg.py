import threading
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Dict, List, Optional, Type, TypeVar, Union

from conan_app_launcher.app.component import Component
from conan_app_launcher.app.logger import Logger


from conan_app_launcher.core import ConanApi, ConanWorker



class ComponentRegistry():
    """
    Abstraction to hold all components, create, stop and get access to them.
    An instance is passed automatically to all components.
    """
    # Constants for Component names to an alternitave method to access components

    comp_init_lock = threading.Lock()  # lock to only instantiate one component at a time

    def __init__(self, settings: "Settings"):
        self._logger = Logger()
        self._settings = settings
        self._unload_in_progress = False  # don't generate new objects
        self._components: Dict[str, Component] = {}  # holds all the instances
        self._stop_thread: threading.Thread

    def set_unload_in_progress(self):
        """ Signals the components, that they are unloading and should not instantiate new objects. """
        self._unload_in_progress = True

    def set_unload_finished(self):
        """ Signals the components, that unload finished and business is back as usual. """
        # reset sensors
        self._sensors = {}
        self._unload_in_progress = False

    def get_names(self) -> List[str]:
        """ Get a list of names of all components"""
        return list(self._components)

    def get(self, name) -> Optional[Component]:
        """ Get a specific component instance """
        return self._components.get(name)

    def stop_component_instance(self, instance):
        """
        Stops a component based on an instance. 
        This is meant for a component to commit sudoku, e.g. when for restarting itself.
        """
        for comp in self._components:
            if instance is self._components[comp]:
                # cant stop from own instance
                self._stop_thread = threading.Thread(name="Stop" + comp,
                                                     target=self.stop_component,
                                                     args=[comp, ],
                                                     daemon=True)
                self._stop_thread.start()
                break

    def stop_component(self, name):
        """ Stops a component. """
        with self.comp_init_lock:
            component = self._components.get(name)
            if not component:
                return
            self._components.pop(name)
            self._logger.info("ComponentRegistry: Stopping %s", name)
            component.stop()
            # call destructors
            del component

    @property
    def conan_api(self) -> ConanApi:
        """ Access for Display singleton """
        from waqd.components import Display
        return self._create_component_instance(Display, [self._settings.get_string(DISPLAY_TYPE),
                                                         self._settings.get_int(BRIGHTNESS),
    
    
    T = TypeVar('T', bound=Component)

    def _create_component_instance(self, class_ref: Type[T], args: List = [], name_ref=None) -> T:
        """ Generic method for component creation and access. """
        name = class_ref.__name__
        if name_ref:
            name = name_ref
        with self.comp_init_lock:
            component = self._components.get(name)
            if component:
                if not isinstance(component, class_ref):
                    raise TypeError(f"FATAL: Component {str(component)}has unexpected type.")
                return component

            if self._unload_in_progress:
                pass
            self._logger.info("ComponentRegistry: Starting %s", name)
            if issubclass(class_ref, Component):
                component = class_ref(*args)
                self._components.update({name: component})
            else:
                raise TypeError("The component " + str(class_ref) +
                                " to be created must be subclass of 'Component', but is instead a " +
                                class_ref.__class__.__name__ + " .")
            return component
