
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, List

from conan_app_launcher.base import Logger
from conan_app_launcher.components.conan import get_conan_package_folder
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore

if TYPE_CHECKING:
    from conan_app_launcher.components import TabEntry


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self, tabs: List["TabEntry"], gui_update_signal: QtCore.pyqtSignal):
        self._conan_queue: "Queue[str]" = Queue(maxsize=0)
        self._worker = None
        self._closing = False
        self._gui_update_signal = gui_update_signal
        self._tabs = tabs

        # get all conan refs
        conan_refs = []
        for tab in tabs:
            for app in tab.get_app_entries():
                conan_refs.append(str(app.conan_ref))
        # make them unique
        self._conan_refs = set(conan_refs)
        # fill up queue
        for ref in self._conan_refs:
            self._conan_queue.put(ref)
            self.start_working()

    def start_working(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._worker:
            self._worker = Thread(target=self._work_on_conan_queue, name="ConanWorker")
            self._worker.start()

    def finish_working(self, timeout_s: int = None):
        """ Cancel, if worker is still not finished """
        if self._worker and self._worker.is_alive():
            self._closing = True
            self._worker.join(timeout_s)
        self._conan_queue = Queue(maxsize=0)
        self._worker = None  # reset thread for later instantiation

    def _work_on_conan_queue(self):
        """ Call conan operations from queue """
        while not self._closing and not self._conan_queue.empty():
            conan_ref = self._conan_queue.get()
            package_folder = get_conan_package_folder(ConanFileReference.loads(conan_ref))
            # call update on every entry which has this ref
            for tab in self._tabs:
                for app in tab.get_app_entries():
                    if str(app.conan_ref) == conan_ref:
                        app.validate_with_conan_info(package_folder)
            Logger().debug("Finish working on " + conan_ref)
            if self._gui_update_signal:
                self._gui_update_signal.emit()
            self._conan_queue.task_done()
