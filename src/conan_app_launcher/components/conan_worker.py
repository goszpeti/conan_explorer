
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, List

from PyQt5 import QtCore
from conans.model.ref import ConanFileReference

from conan_app_launcher.base import Logger
from conan_app_launcher.components.conan import ConanApi

if TYPE_CHECKING:
    from conan_app_launcher.components import TabEntry


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self, tabs: List["TabEntry"], gui_update_signal: QtCore.pyqtSignal):
        self._conan = ConanApi()
        self._conan_queue: "Queue[Tuple[str, Dict[str, str]]]" = Queue(maxsize=0)
        self._version_getter = None
        self._worker = None
        self._closing = False
        self._gui_update_signal = gui_update_signal
        self._tabs = tabs

        # get all conan refs and  make them unique # TODO separate this from worker
        conan_refs = []
        for tab in tabs:
            for app in tab.get_app_entries():
                ref_dict = {"name": str(app.conan_ref), "options": app.conan_options}
                if not ref_dict in conan_refs:
                    conan_refs.append(ref_dict)

        # fill up queue
        for ref in conan_refs:
            self._conan_queue.put([ref["name"], ref["options"]])
            # start getting versions info in a separate thread
            self._version_getter = Thread(target=self._get_packages_versions, args=[ref["name"], ])
            self._version_getter.start()
        self.start_working()

    def put_ref_in_queue(self, conan_ref: str, conan_options: {}):
        self._conan_queue.put([conan_ref, conan_options])
        self.start_working()

    def start_working(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._worker or not self._worker.is_alive():
            self._worker = Thread(target=self._work_on_conan_queue, name="ConanWorker")
            self._worker.start()

    def finish_working(self, timeout_s: int = None):
        """ Cancel, if worker is still not finished """
        self._closing = True
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout_s)
        if self._version_getter and self._version_getter.is_alive():
            self._version_getter.join(timeout_s)
        self._conan_queue = Queue(maxsize=0)
        self._worker = None  # reset thread for later instantiation

    def _work_on_conan_queue(self):
        """ Call conan operations from queue """
        while not self._closing and not self._conan_queue.empty():
            conan_ref, conan_options = self._conan_queue.get()
            package_folder = self._conan.get_path_or_install(
                ConanFileReference.loads(conan_ref), conan_options)
            # call update on every entry which has this ref
            for tab in self._tabs:
                for app in tab.get_app_entries():
                    if str(app.conan_ref) == conan_ref:
                        app.set_package_info(package_folder)
            Logger().debug("Finish working on " + conan_ref)
            if self._gui_update_signal:
                self._gui_update_signal.emit()
            self._conan_queue.task_done()

    def _get_packages_versions(self, conan_ref):
        available_refs = self._conan.search_for_all_recipes(ConanFileReference.loads(conan_ref))
        if not available_refs:
            return
        for tab in self._tabs:
            for app in tab.get_app_entries():
                if not self._closing and str(app.conan_ref) == conan_ref:
                    app.set_available_packages(available_refs)
        if not self._closing and self._gui_update_signal:
            self._gui_update_signal.emit()
