
from pathlib import Path
from typing import List, Tuple, Dict

from conans import __version__ as conan_version
from conans.client.conan_api import ClientCache, ConanAPIV1, UserIO
from conans.client.conan_command_output import CommandOutputer
from conans.model.ref import ConanFileReference
from packaging.version import Version

from conan_app_launcher.base import Logger


def get_conan_package_folder(conan_ref: ConanFileReference, input_options={}) -> Path:
    """ Return the package folder of a conan reference, and install it, if it is not available """
    conan, cache, user_io = _getConanAPI()
    package_folder = Path("Inconclusive")
    [is_installed, package_folder] = get_conan_path(
        "package_folder", conan, cache, user_io, conan_ref, input_options)

    if not is_installed:
        Logger().info(f"Installing '{str(conan_ref)}'...")
        res = install_conan_package(conan, cache, conan_ref, input_options)
        if not res:  # Logger gave error msg
            return package_folder
        # needed: call info again for path, install info does not have it
        [is_installed, package_folder] = get_conan_path(
            "package_folder", conan, cache, user_io, conan_ref, input_options)
    else:
        Logger().debug(f"Found '{str(conan_ref)}' in {str(package_folder)}.")
    return package_folder


def get_conan_path(path: str, conan: ConanAPIV1, cache: ClientCache, user_io: UserIO,
                   conan_ref: ConanFileReference, input_options: Dict[str, str]) -> Tuple[bool, Path]:
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
        options: List[dict] = []
        [deps_graph, _] = ConanAPIV1.info(conan, str(
            conan_ref), options=_create_key_value_pair_list(input_options))
        # I don't know another way to do this
        output = CommandOutputer(user_io.out, cache)._grab_info_data(deps_graph, True)
        return get_install_status_and_path_from_output(output, conan_ref, path)
    except BaseException as error:
        Logger().error(str(error))
    return False, Path()


def install_conan_package(conan: ConanAPIV1, cache: ClientCache,
                          conan_ref: ConanFileReference, input_options: Dict[str, str]) -> bool:
    """
    Try to install a conan package while guessing the mnost suitable package
    for the current platform.
    """
    remotes = cache.registry.load_remotes()
    found_pkgs = []
    default_settings = cache.default_profile.settings
    for remote in remotes.items():
        if not isinstance(remote, str) and len(remote) > 0:  # only check for len, can be an object or a list
            remote = remote[0]  # for old apis
        try:
            query = f"(arch=None OR arch={default_settings.get('arch')})" \
                    f" AND (arch_build=None OR arch_build={default_settings.get('arch_build')})" \
                    f" AND (os=None OR os={default_settings.get('os')})"\
                    f" AND (os_build=None OR os_build={default_settings.get('os_build')})"

            search_results = ConanAPIV1.search_packages(conan, str(conan_ref), query=query,
                                                        remote_name=remote).get("results", None)
        except:  # next
            continue
        # get options and settings
        found_pkgs = []
        # # try to find a suitable package with matching settings
        # # the internal conan model API is explicitly mot used, becasue its volatility
        for result in search_results:
            for item in result.get("items"):
                for package in item.get("packages"):
                    found_pkgs.append(package)

        # Check for settings, like there is a debug and release package
        # -> release is preferred
        if len(found_pkgs) > 1:
            filtered_pkgs = []
            for pkg in found_pkgs:
                if pkg.get("settings").get("build_type", "").lower() == "debug":
                    continue
                filtered_pkgs.append(pkg)
        else:
            filtered_pkgs = found_pkgs

        # the only difference must be in settings.compiler - take the first one (not elegant)
        # TODO take highest compiler version
        found_pkg = filtered_pkgs[0]
        settings_list = _create_key_value_pair_list(found_pkg.get("settings"))
        options_list = []
        if found_pkg.get("options"):
            if input_options:
                options_list = _create_key_value_pair_list(found_pkg.get("options"))
            else:
                default_options = conan.inspect(str(conan_ref), attributes=[
                                                "default_options"]).get("default_options")
                options_list = []  # default options are used automatically and corrected with config options
                Logger().info("Multiple packages found. Using default options:\n" +
                              (str(_create_key_value_pair_list(default_options))))

        try:
            info = ConanAPIV1.install_reference(conan, conan_ref, update=True,
                                                settings=settings_list, options=options_list)
            return True
        except BaseException as error:
            Logger().error(f"Cannot install package '{conan_ref}': {str(error)}")
            return False
    # check after all remotes are checked
    if not found_pkgs:
        Logger().warning(f"Can't find a matching package '{str(conan_ref)}' for this platform.")
        return False
    return True


def _getConanAPI():
    """ Helper function to get conan API objects"""
    conan, cache, user_io = ConanAPIV1.factory()
    if Version(conan_version) > Version("1.18"):
        conan.create_app()
        user_io = conan.user_io
        cache = conan.app.cache
    return conan, cache, user_io


def _create_key_value_pair_list(input_dict: dict) -> List[str]:
    """ helper to create name=value string list from dict"""
    res_list = []
    for name, value in input_dict.items():
        value = str(value)
        if value.lower() == "any":
            continue
        res_list.append(name + "=" + value)
    return res_list


def get_install_status_and_path_from_output(output: List[dict], conan_ref: str, path: str) -> Tuple[bool, Path]:
    """ Helper for getting the own ref from the conan output parser"""
    for package_info in output:
        if package_info.get("reference") == str(conan_ref):
            is_installed = (package_info.get("binary") == "Cache")
            return is_installed, Path(package_info.get(path))
    return False, Path("Wrong")
