#
# Copyright (c) 2019-2021 Péter Gosztolya & Contributors.
#
# This file is part of WAQD
# (see https://github.com/goszpeti/WeatherAirQualityDevice).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import threading
import time

from typing import Optional

from conan_app_launcher.app.component_reg import ComponentRegistry
from conan_app_launcher.app.logger import Logger

class ComponentController():
    """ Loader, unloader and watchdog for components. """
    UPDATE_TIME = 5

    def __init__(self, settings: "Settings"):
        self._components = ComponentRegistry(settings)

        # thread for watchdog
        self._stop_event = threading.Event()  # own stop event for watchdog
        # thread for waiting for comps unload
        self._unload_thread: Optional[threading.Thread] = None # re-usable thread, assignment is in unload_all

    @property
    def all_ready(self) -> bool:
        """ Signals, that all modules have been started loading """
        all_ready = False
        for comp_name in self._components.get_names():
            component = self._components.get(comp_name)
            if component:
                all_ready |= component.is_ready
        return all_ready

    @property
    def all_unloaded(self) -> bool:
        """ All managed modules are unloaded. """
        if not self._unload_thread:
            return True
        return not self._unload_thread.is_alive()

    @property
    def components(self) -> ComponentRegistry:
        """ Returns held components for higher level functions """
        return self._components

    def init_all(self):
        """
        Start every managed module, by starting the watch thread.
        """
        if self._unload_thread and self._unload_thread.is_alive():
            self._unload_thread.join()
        self._stop_event.clear()
        Logger().info("Start initializing all components")
        for comp in self.components.get:
            comp()

    def unload_all(self, reload_intended=False, updating=False):
        """
        Start unloading modules. modules_unloaded signals finish.
        """
        self._components.set_unload_in_progress()
        Logger().info("Start unloading all components")
        self._unload_thread = threading.Thread(
            name="UnloadModules", target=self._unload_all_components, args=[reload_intended, updating])
        self._unload_thread.start()

    def stop(self):
        """
        Stop this module, by sending a stop request.
        Actual stop is asyncron.
        """
        if self._watch_thread and self._watch_thread.is_alive():
            self._stop_event.set()

    def _unload_all_components(self, reload_intended, updating):
        """
        Stop own watcher and unload modules.
        :param reload_intended: singals, that objects, which forbid reload will be skipped
        """
        # watch threads needs to stop - updater runs continously
        self.stop()

        for comp_name in self._components.get_names():
            self._components.stop_component(comp_name, reload_intended)
        Logger().info("ComponentRegistry: All components unloaded.")
        self._components.set_unload_finished()
