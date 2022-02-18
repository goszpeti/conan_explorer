
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from conan_app_launcher.settings import (ENABLE_APP_COMBO_BOXES,
                                         SettingsInterface)
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
from conans.model.ref import ConanFileReference, PackageReference


class ConanWorkerElement(TypedDict):
    ref_pkg_id: str  # format in <ref>:<id>. Id is optional. If id is used options, settings and auto_isntall is ignored
    options: Dict[str, str]  # conan options with key-value pairs
    settings: Dict[str, str]  # conan settings with key-value pairs
    update: bool  # use -u flag for install
    auto_install: bool  # automatically determine best matching package.


class ConanWorker():
    """ Sequential worker with a queue to execute conan install/version alternatives commands """

    def __init__(self, conan_api: "ConanApi", settings: SettingsInterface):
        self._conan_api = conan_api
        self._conan_install_queue: Queue[Tuple[ConanWorkerElement, Optional[pyqtBoundSignal]]] = Queue(maxsize=0)
        self._conan_versions_queue: Queue[Tuple[ConanWorkerElement, Optional[pyqtBoundSignal]]] = Queue(maxsize=0)
        self._version_worker: Optional[Thread] = None
        self._install_worker: Optional[Thread] = None
        self._shutdown_requested = False  # internal flag to cancel worker on shutdown
        self._settings = settings

    def update_all_info(self, conan_elements: List[ConanWorkerElement],
                        info_signal: Optional[pyqtBoundSignal]):
        """ 
        Starts the worker for all given elements. Should be called at start. 
        info_signal is used to notify the caller, that the worker has finished for a given element.
        Install and version workers use the same signal. To be able to identify, which package has been finished
        the signal will send this info: tuple(conan_ref, pkg_id)
        """
        # fill up queue
        for worker_element in conan_elements:
            if USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL:
                self._conan_install_queue.put((worker_element, info_signal))
            self._conan_versions_queue.put((worker_element, info_signal))

        # start getting versions info in a separate thread in a bundled way to get better performance
        self._start_install_worker()
        if self._settings.get_bool(ENABLE_APP_COMBO_BOXES):
            self._start_version_worker()

    def put_ref_in_version_queue(self, conan_element: ConanWorkerElement, info_signal: Optional[pyqtBoundSignal]):
        self._conan_versions_queue.put((conan_element, info_signal))
        if self._settings.get_bool(ENABLE_APP_COMBO_BOXES):
            self._start_version_worker()

    def put_ref_in_install_queue(self, conan_element: ConanWorkerElement, install_signal: Optional[pyqtBoundSignal]):
        """ Add a new entry to work on """
        self._conan_install_queue.put((conan_element, install_signal))
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

    def _work_on_conan_install_queue(self):
        """ Call conan install from queue """
        signal = None
        conan_ref = None
        pkg_id = ""
        while not self._shutdown_requested and not self._conan_install_queue.empty():
            worker_element, signal = self._conan_install_queue.get()
            ref_pkg_id = worker_element.get("ref_pkg_id", "")
            conan_options = worker_element.get("options", {})
            conan_settings = worker_element.get("settings", {})
            pkg_id = ""
            update = worker_element.get("update", False)
            auto_install = worker_element.get("auto_install", True)
            # package path will be updated in conan cache
            try:
                if ":" in ref_pkg_id:  # pkg ref
                    pkg_ref = PackageReference.loads(ref_pkg_id)
                    conan_ref = pkg_ref.ref
                    pkg_id = pkg_ref.id
                    package = self._conan_api.get_remote_pkg_from_id(pkg_ref)
                    self._conan_api.install_package(pkg_ref.ref, package, update)
                else:
                    conan_ref = ConanFileReference.loads(ref_pkg_id)

                    if auto_install:
                        pkg_id, _ = self._conan_api.get_path_or_auto_install(conan_ref, conan_options, update)
                    else:
                        pkg_id, _ = self._conan_api.install_reference(conan_ref, conan_settings, conan_options, update=update)
            except Exception:
                self._conan_install_queue.task_done()
                continue
            Logger().debug("Finish working on " + ref_pkg_id)
            self._conan_install_queue.task_done()
        # batch emitting signal TODO ????
        if signal:
            signal.emit(str(conan_ref), pkg_id)

    def _work_on_conan_versions_queue(self):
        """ Get all version and channel combination of a package from all remotes. """
        signal = None
        conan_ref = ""
        while not self._shutdown_requested and not self._conan_versions_queue.empty():
            worker_element, signal = self._conan_versions_queue.get()
            # available versions will be in cache and retrievable for every item from there
            try:
                available_refs = self._conan_api.search_recipe_alternatives_in_remotes(
                    ConanFileReference.loads(conan_ref))
            except Exception as e:
                Logger().debug(f"ERROR in searching for {conan_ref}: {str(e)}")
                continue
            Logger().debug(f"Finished available package query for {str(conan_ref)}")
            if not available_refs:
                continue
        if signal:
            signal.emit(conan_ref, "")

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
