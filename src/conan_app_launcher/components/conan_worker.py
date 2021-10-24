
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import Tuple, Dict, Optional

from conans.model.ref import ConanFileReference

import conan_app_launcher as this
from conan_app_launcher.base import Logger
from conan_app_launcher.components.conan import ConanApi


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self):
        self._conan = ConanApi()
        self._conan_queue: Queue[Tuple[str, Dict[str, str]]] = Queue(maxsize=0)
        self._version_getter: Optional[Thread] = None
        self._worker: Optional[Thread] = None
        self._closing = False

        self.update_all_info()

    def update_all_info(self):
        """ Starts the worker on using the current tabs info global var """
        # get all conan refs and  make them unique # TODO separate this from worker
        conan_refs = []
        for tab in this.tab_configs:
            for app in tab.get_app_entries():
                ref_dict = {"name": str(app.conan_ref), "options": app.conan_options}
                if ref_dict not in conan_refs:
                    conan_refs.append(ref_dict)

        # fill up queue
        for ref in conan_refs:
            if this.USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH:
                self._conan_queue.put([ref["name"], ref["options"]])
            # start getting versions info in a separate thread in a bundled way to get better performance
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
            try:
                package_folder = self._conan.get_path_or_install(
                    ConanFileReference.loads(conan_ref), conan_options)
            except:
                self._conan_queue.task_done()
                return
            # call update on every entry which has this ref
            for tab in this.tab_configs:
                for app in tab.get_app_entries():
                    if str(app.conan_ref) == conan_ref:
                        app.set_package_info(package_folder)
            Logger().debug("Finish working on " + conan_ref)
            self._conan_queue.task_done()

    def _get_packages_versions(self, conan_ref: str):
        """ Get all version and channel combination of a package from all remotes. """
        available_refs = self._conan.search_recipe_in_remotes(ConanFileReference.loads(conan_ref))
        if not available_refs:
            return
        for tab in this.tab_configs:
            for app in tab.get_app_entries():
                if not self._closing and str(app.conan_ref) == conan_ref:
                    app.set_available_packages(available_refs)
