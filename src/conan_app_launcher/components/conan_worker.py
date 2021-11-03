
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict
    from .conan import ConanApi
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

from conan_app_launcher import USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH
from conan_app_launcher.logger import Logger
from conans.model.ref import ConanFileReference


class ConanWorkerElement(TypedDict):
    reference: str
    options: Dict[str, str]

class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self, conan_api: "ConanApi"):
        self._conan_api = conan_api
        self._conan_queue: Queue[Tuple[str, Dict[str, str]]] = Queue(maxsize=0)
        self._version_getter: Optional[Thread] = None
        self._worker: Optional[Thread] = None
        self._closing = False

    def update_all_info(self, conan_elements: List[ConanWorkerElement]):
        """ Starts the worker for all given elements. Should be called at start. """
        # fill up queue
        for ref in conan_elements:
            if USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH:
                self._conan_queue.put((ref["reference"], ref["options"]))
        # start getting versions info in a separate thread in a bundled way to get better performance
        self._version_getter = Thread(target=self._get_packages_versions, args=[conan_elements, ])
        self._version_getter.start()
        self._start_working()

    def put_ref_in_queue(self, conan_ref: str, conan_options: Dict[str, str]):
        """ Add a new entry to work on """
        self._conan_queue.put((conan_ref, conan_options))
        self._start_working()

    def _start_working(self):
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
                package_folder = self._conan_api.get_path_or_install(
                    ConanFileReference.loads(conan_ref), conan_options)
            except Exception:
                self._conan_queue.task_done()
                return
            # call update on every entry which has this ref
            # TODO this dependency should not be here!
            # for tab in tab_configs:
            #     for app in tab.get_app_entries():
            #         if str(app.conan_ref) == conan_ref:
            #             app.set_package_info(package_folder)
            Logger().debug("Finish working on " + conan_ref)
            self._conan_queue.task_done()

    def _get_packages_versions(self, conan_refs: List[ConanWorkerElement]):
        """ Get all version and channel combination of a package from all remotes. """
        for conan_ref in conan_refs:
            available_refs = self._conan_api.search_recipe_in_remotes(
                ConanFileReference.loads(conan_ref["reference"]))
            Logger().debug(f"Finished available package query for{str(conan_ref)}")
            if not available_refs:
                continue
            # TODO this dependency should not be here!
            # for tab in tab_configs:
            #     for app in tab.get_app_entries():
            #         if not self._closing and str(app.conan_ref) == conan_ref:
            #             app.set_available_packages(available_refs)
