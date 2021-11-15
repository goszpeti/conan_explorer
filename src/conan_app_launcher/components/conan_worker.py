
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple
from PyQt5.QtCore import pyqtBoundSignal

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict
    from .conan import ConanApi
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

from conan_app_launcher import USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL
from conan_app_launcher.logger import Logger
from conans.model.ref import ConanFileReference


class ConanWorkerElement(TypedDict):
    reference: str
    options: Dict[str, str]


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self, conan_api: "ConanApi"):
        self._conan_api = conan_api
        self._conan_install_queue: Queue[Tuple[str, Dict[str, str],
                                               Optional[pyqtBoundSignal]]] = Queue(maxsize=0)
        self._conan_versions_queue: Queue[Tuple[str, Optional[pyqtBoundSignal]]] = Queue(maxsize=0)
        self._version_worker: Optional[Thread] = None
        self._install_worker: Optional[Thread] = None
        self._shutdown_requested = False

    def update_all_info(self, conan_elements: List[ConanWorkerElement],
                        info_signal: Optional[pyqtBoundSignal]):
        """ Starts the worker for all given elements. Should be called at start. """
        # fill up queue
        for ref in conan_elements:
            if USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL:
                self._conan_install_queue.put((ref["reference"], ref["options"], info_signal))
            self._conan_versions_queue.put((ref["reference"], info_signal))

        # start getting versions info in a separate thread in a bundled way to get better performance
        self._start_install_worker()
        self._start_version_worker()

    def put_ref_in_version_queue(self, conan_ref: str, info_signal: Optional[pyqtBoundSignal]):
        self._conan_versions_queue.put((conan_ref, info_signal))
        self._start_version_worker()

    def put_ref_in_install_queue(self, conan_ref: str, conan_options: Dict[str, str], install_signal):
        """ Add a new entry to work on """
        self._conan_install_queue.put((conan_ref, conan_options, install_signal))
        self._start_install_worker()

    def _start_install_worker(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._install_worker or not self._install_worker.is_alive():
            self._install_worker = Thread(target=self._work_on_conan_install_queue,
                                          name="ConanInstallWorker", daemon=True)
            self._install_worker.start()

    def _start_version_worker(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._version_worker or not self._version_worker.is_alive():
            self._version_worker = Thread(target=self._work_on_conan_versions_queue,
                                          name="ConanVersionWorker", daemon=True)
            self._version_worker.start()

    def finish_working(self, timeout_s: int = None):
        """ Cancel, if worker is still not finished """
        self._shutdown_requested = True
        try:
            if self._install_worker and self._install_worker.is_alive():
                self._install_worker.join(timeout_s)
        except Exception:
            return  # Conan threads can crash on join
        try:
            if self._version_worker and self._version_worker.is_alive():
                self._version_worker.join(timeout_s)
        except Exception:
            return  # Conan threads can crash on join
        self._conan_install_queue = Queue(maxsize=0)
        self._install_worker = None  # reset thread for later instantiation
        self._shutdown_requested = False

    def _work_on_conan_install_queue(self):
        """ Call conan operations from queue """
        signal = None
        conan_ref = ""
        while not self._shutdown_requested and not self._conan_install_queue.empty():
            conan_ref, conan_options, signal = self._conan_install_queue.get()
            # package path wwill be updated in conan cache
            try:
                self._conan_api.get_path_or_install(ConanFileReference.loads(conan_ref), conan_options)
            except Exception:
                self._conan_install_queue.task_done()
                continue
            Logger().debug("Finish working on " + conan_ref)
            self._conan_install_queue.task_done()
        # batch emitting signal
        if signal:
            signal.emit(conan_ref)

    def _work_on_conan_versions_queue(self):
        """ Get all version and channel combination of a package from all remotes. """
        signal = None
        conan_ref = ""
        while not self._shutdown_requested and not self._conan_versions_queue.empty():
            conan_ref, signal = self._conan_versions_queue.get()
            # available versions will be in cache and retrievable for every item from there
            try:
                available_refs = self._conan_api.search_recipe_in_remotes(
                    ConanFileReference.loads(conan_ref))
            except Exception as e:
                Logger().debug(f"ERROR in searching for {conan_ref}: {str(e)}")
                continue
            Logger().debug(f"Finished available package query for {str(conan_ref)}")
            if not available_refs:
                continue
        if signal:
            signal.emit(conan_ref)
