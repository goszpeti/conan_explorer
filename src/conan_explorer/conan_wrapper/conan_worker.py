
from queue import Queue
from threading import Thread
# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from conan_explorer.settings import SettingsInterface

if TYPE_CHECKING:
    from typing import TypedDict, Protocol
    from ..conan_wrapper import ConanApi
else:
    try:
        from typing import TypedDict, Protocol
    except ImportError:
        from typing_extensions import TypedDict, Protocol

from conan_explorer import USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL
from conan_explorer.app.logger import Logger
from .types import ConanOptions, ConanRef, ConanPkgRef, ConanSettings


class ConanWorkerElement(TypedDict):
    ref_pkg_id: str  # format in <ref>:<id>. Id is optional. If id is used options, settings and auto_isntall is ignored
    options: ConanOptions  # conan options with key-value pairs
    settings: ConanSettings  # conan settings with key-value pairs
    profile: str  # alternative to settings
    update: bool  # use -u flag for install
    auto_install: bool  # automatically determine best matching package.


class ConanWorkerResultCallback(Protocol):
    def __call__(self, conan_ref: str, pkg_id: str) -> Any: ...


class ConanWorker():
    """ Sequential worker with a queue to execute conan install/version alternatives commands """

    def __init__(self, conan_api: "ConanApi", settings: SettingsInterface):
        self._conan_api = conan_api
        self._conan_install_queue: Queue[Tuple[ConanWorkerElement,
                                         Optional[ConanWorkerResultCallback]]] = Queue(maxsize=0)
        self._install_worker: Optional[Thread] = None
        self._shutdown_requested = False  # internal flag to cancel worker on shutdown
        self._settings = settings

    def update_all_info(self, conan_elements: List[ConanWorkerElement],
                        info_callback: Optional[ConanWorkerResultCallback]):
        """ 
        Starts the worker for all given elements. Should be called at start. 
        info_signal is used to notify the caller that the worker has finished 
        for a given element. To be able to identify, which package has been finished
        the signal will send this info: tuple(conan_ref, pkg_id)
        """
        # fill up queue
        for worker_element in conan_elements:
            if USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL:
                self._conan_install_queue.put((worker_element, info_callback))

        # start getting versions info in a separate thread in a bundled way to get better performance
        self._start_install_worker()

    def put_ref_in_install_queue(self, conan_element: ConanWorkerElement, 
                                 info_callback: Optional[ConanWorkerResultCallback]):
        """ Add a new entry to work on """
        self._conan_install_queue.put((conan_element, info_callback))
        self._start_install_worker()

    def _start_install_worker(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._install_worker or not self._install_worker.is_alive():
            self._install_worker = Thread(target=self._work_on_conan_install_queue,
                                          name="ConanInstallWorker", daemon=True)
            self._install_worker.start()

    def _work_on_conan_install_queue(self):
        """ Call conan install from queue """
        info_callback = None
        pkg_id = ""
        while not self._shutdown_requested and not self._conan_install_queue.empty():
            worker_element, info_callback = self._conan_install_queue.get()
            ref_pkg_id = worker_element.get("ref_pkg_id", "")
            conan_options = worker_element.get("options", {})
            conan_settings = worker_element.get("settings", {})
            conan_profile = worker_element.get("profile", "")
            pkg_id = ""
            update = worker_element.get("update", False)
            auto_install = worker_element.get("auto_install", True)
            # package path will be updated in conan cache
            try:
                conan_ref: ConanRef
                if ":" in ref_pkg_id:  # pkg ref
                    pkg_ref: ConanPkgRef = ConanPkgRef.loads(
                        ref_pkg_id)  # type: ignore
                    conan_ref = pkg_ref.ref  # type: ignore
                    package = self._conan_api.get_remote_pkg_from_id(pkg_ref)
                    pkg_id, _ = self._conan_api.install_package(
                        pkg_ref.ref, package, update)
                else:
                    conan_ref = ConanRef.loads(ref_pkg_id)  # type: ignore

                    if auto_install:
                        pkg_id, _ = self._conan_api.get_path_or_auto_install(
                            conan_ref, conan_options, update)
                    else:
                        pkg_id, _ = self._conan_api.install_reference(conan_ref,
                            conan_settings, conan_options, conan_profile, update)
            except Exception as e:
                try:
                    self._conan_install_queue.task_done()
                except ValueError:
                    pass  # don't care about calling too many times
                continue
            Logger().debug("Finish working on " + ref_pkg_id)
            try:
                self._conan_install_queue.task_done()
            except ValueError:
                pass  # don't care about calling too many times
            if USE_CONAN_WORKER_FOR_LOCAL_PKG_PATH_AND_INSTALL:
                if info_callback and not self._shutdown_requested:
                    try:
                        info_callback(
                            self._conan_api.generate_canonical_ref(conan_ref), pkg_id)
                    except Exception as e:
                        Logger().error(str(e))

    def finish_working(self, timeout_s: Optional[float] = None):
        """ Cancel, if worker is still not finished """
        self._shutdown_requested = True
        try:
            if self._install_worker and self._install_worker.is_alive():
                self._install_worker.join(timeout_s)
        except Exception:
            return  # Conan threads can crash on join
        self._conan_install_queue = Queue(maxsize=0)
        self._install_worker = None  # reset thread for later instantiation
        self._shutdown_requested = False
