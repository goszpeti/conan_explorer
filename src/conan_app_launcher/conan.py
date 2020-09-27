
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Tuple

from conans.client import conan_api
from conans.client.conan_command_output import CommandOutputer
from conans.model.ref import ConanFileReference
from conan_app_launcher.config_file import AppEntry

from .logger import Logger


class ConanWorker():
    """ Sequential worker with a queue to execute conan commands """

    def __init__(self):
        # TODO add setter
        self.app_queue = Queue(maxsize=0)
        self._worker = None

    def start_working(self):
        """ Start worker, if it is not already started (can be called multiple times)"""
        if not self._worker:
            self._worker = Thread(target=self._work_on_conan_queue, name="ConanWorker")
            self._worker.setDaemon(True)
            self._worker.start()

    def finish_working(self, timeout_s: int):
        """ Cancel, if worker is still not finished """
        if self._worker.is_alive():
            self._worker.join(timeout_s)
        self._worker = None  # reset thread for later instantiation

    def _work_on_conan_queue(self):
        """ Call conan operations form queue """
        while not self.app_queue.empty():
            app_entry: AppEntry = self.app_queue.get()
            # TODO use setter
            set_conan_package_folder(app_entry)
            app_entry.on_conan_info_available()
            self.app_queue.task_done()


def get_conan_paths(conan, cache, user_io, conan_ref) -> Tuple[bool, Path]:
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
        Logger().info("Getting info for '%s'...", str(conan_ref))
        [deps_graph, _] = conan_api.ConanAPIV1.info(conan, conan_ref.full_repr())
        # TODO: only for conan 1.16 - 1.18
        output = CommandOutputer(user_io.out, cache)._grab_info_data(
            deps_graph, True)[0]  # can have only one element
        is_installed = output.get("binary") == "Download"
        return is_installed, Path(output.get("package_folder"))
    except BaseException as error:
        Logger().error(str(error))
        return False, Path()


def set_conan_package_folder(app_entry: AppEntry):
    [conan, cache, user_io] = conan_api.ConanAPIV1.factory()
    package_folder = Path()
    [is_installed, package_folder] = get_conan_paths(conan, cache, user_io, app_entry.package_id)

    if not is_installed:
        Logger().info("Installing '%s'...", str(app_entry.package_id))
        install_conan_package(conan, cache, app_entry.package_id)
        # lazy: call info again for path
        [is_installed, package_folder] = get_conan_paths(conan, cache, user_io, app_entry.package_id)
    else:
        Logger().info("Found '%s' in %s.", str(app_entry.package_id), str(package_folder))
    app_entry.package_folder = package_folder


def install_conan_package(conan: conan_api.ConanAPIV1, cache: conan_api.ClientCache,
                          package_id: ConanFileReference):
    remotes = cache.registry.load_remotes()
    for [remote, _] in remotes.items():
        if remote == "conan-center":
            continue  # no third party packages
        try:
            search_results = conan_api.ConanAPIV1.search_packages(conan,
                                                                  str(package_id),
                                                                  remote_name=remote)
        except:  # next
            continue
        # get options and settings
        sets = {}
        default_settings = cache.default_profile.settings

        found_pkg = True
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
        if not found_pkg:
            Logger().warning("Cant find a matching package '%s' for this platform.", str(package_id))
        settings_list = []
        for name, value in sets.items():
            settings_list.append(name + "=" + value)
        try:
            conan_api.ConanAPIV1.install_reference(conan, package_id, update=True, settings=settings_list)
        except BaseException as error:
            Logger().error("Cannot install packge '%s': %s", package_id, str(error))
