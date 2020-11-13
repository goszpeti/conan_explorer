
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import List, Tuple

from conans import __version__ as conan_version
from conans.client.conan_api import ClientCache, ConanAPIV1, UserIO
from conans.client.conan_command_output import CommandOutputer
from conans.model.ref import ConanFileReference
from packaging.version import Version
from PyQt5 import QtCore

from conan_app_launcher.base import Logger

# this allows to use forward declarations to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from conan_app_launcher.components import TabEntry


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands and get info on packages """

    def __init__(self, tabs: List["TabEntry"], gui_update_signal: QtCore.pyqtSignal):
        # TODO add setter
        self._conan_queue: "Queue[str]" = Queue(maxsize=0)
        self._worker = None
        self._closing = False
        self._gui_update_signal = gui_update_signal
        self._tabs = tabs

        # get all conan refs
        conan_refs = []
        for tab in tabs:
            for app in tab.get_app_entries():
                conan_refs.append(str(app.package_id))
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
                    if str(app.package_id) == conan_ref:
                        app.validate_with_conan_info(package_folder)
            Logger().debug("Finish working on " + conan_ref)
            if self._gui_update_signal:
                self._gui_update_signal.emit()
            self._conan_queue.task_done()


def get_conan_package_folder(conan_ref: ConanFileReference) -> Path:
    """ Return the package folder of a conan reference, and install it, if it is not available """
    conan, cache, user_io = ConanAPIV1.factory()
    if Version(conan_version) > Version("1.18"):
        conan.create_app()
        user_io = conan.user_io
        cache = conan.app.cache
    package_folder = Path()
    [is_installed, package_folder] = get_conan_path("package_folder", conan, cache, user_io, conan_ref)

    if not is_installed:
        Logger().info(f"Installing '{str(conan_ref)}'...")
        install_conan_package(conan, cache, conan_ref)
        # lazy: call info again for path
        [is_installed, package_folder] = get_conan_path("package_folder", conan, cache, user_io, conan_ref)
    else:
        Logger().debug(f"Found '{str(conan_ref)}' in {str(package_folder)}.")
    return package_folder


def get_conan_path(path: str, conan: ConanAPIV1, cache: ClientCache, user_io: UserIO,
                   conan_ref: ConanFileReference) -> Tuple[bool, Path]:
    """ Get a conan path and return is_installed, path """
    try:
        conan.remove_locks()
        # Workaround: remove directory, if it created a count.lock, without a conanfile
        # because conan will lock up the next time
        conan_package_path = Path(cache.store) / conan_ref.name / conan_ref.version / \
            conan_ref.user / conan_ref.channel
        if not Path(conan_package_path).is_dir():
            ref_count_file = Path(cache.store) / conan_ref.name / conan_ref.version / \
                conan_ref.user / (conan_ref.channel + ".count")
            ref_lock_file = Path(str(ref_count_file) + ".lock")
            if ref_lock_file.exists():
                ref_count_file.unlink()
                ref_lock_file.unlink()
        Logger().debug(f"Getting info for '{str(conan_ref)}'...")
        output = []
        [deps_graph, _] = ConanAPIV1.info(conan, str(conan_ref))
        output = CommandOutputer(user_io.out, cache)._grab_info_data(deps_graph, True)
        for package_info in output:
            if package_info.get("reference") == str(conan_ref):
                is_installed = (package_info.get("binary") == "Cache")
                return is_installed, Path(package_info.get(path))
    except BaseException as error:
        Logger().error(str(error))
    return False, Path()


def install_conan_package(conan: ConanAPIV1, cache: ClientCache,
                          package_id: ConanFileReference):
    """
    Try to install a conan package while guessing the mnost suitable package
    for the current platform.
    """
    remotes = cache.registry.load_remotes()
    found_pkg = False
    for remote in remotes.items():
        if not isinstance(remote, str) and len(remote) > 0:  # only check for len, can be an object or a list
            remote = remote[0]  # for old apis
        try:
            search_results = ConanAPIV1.search_packages(conan, str(package_id),
                                                        remote_name=remote)
        except:  # next
            continue
        # get options and settings
        sets = {}
        default_settings = cache.default_profile.settings

        # try to find a suitable package with matching settings
        for result in search_results.get("results"):
            for item in result.get("items"):
                for package in item.get("packages"):
                    sets = package.get("settings")
                    if ((sets.get("os") == default_settings.get("os") or
                         sets.get("os_build") == default_settings.get("os_build"))
                        and (sets.get("arch") == default_settings.get("arch") or
                             sets.get("arch_build") == default_settings.get("arch_build"))):
                        found_pkg = True
                        break
                if found_pkg:
                    break
            if found_pkg:
                break

        settings_list = []
        for name, value in sets.items():
            settings_list.append(name + "=" + value)
        try:
            ConanAPIV1.install_reference(conan, package_id, update=True, settings=settings_list)
        except BaseException as error:
            Logger().error(f"Cannot install packge '{package_id}': {str(error)}")
    if not found_pkg:
        Logger().warning(f"Cant find a matching package '{str(package_id)}' for this platform.")
