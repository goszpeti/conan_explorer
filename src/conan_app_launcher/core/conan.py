import platform
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from conans.client.cache.remote_registry import Remote
from conans.client.output import ConanOutput

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict
from conans.errors import ConanException
from conans.client.conan_api import ClientCache, ConanAPIV1, UserIO, client_version
from conans.model.ref import ConanFileReference, PackageReference
from conans.paths.package_layouts.package_editable_layout import \
    PackageEditableLayout
from conans.util.windows import path_shortener

try:
    from conans.util.windows import CONAN_REAL_PATH, path_shortener
except Exception:
    pass

from conan_app_launcher import (CONAN_LOG_PREFIX, INVALID_CONAN_REF,
                                SEARCH_APP_VERSIONS_IN_LOCAL_CACHE, base_path)
from conan_app_launcher.app.logger import Logger

from .conan_cache import ConanInfoCache


class ConanPkg(TypedDict, total=False):
    """ Dummy class to type conan returned package dicts """

    id: str
    options: Dict[str, str]
    settings: Dict[str, str]
    requires: List
    outdated: bool


class LoggerWriter:
    """
    Dummy stream to log directly to a logger object, when writing in the stream.
    Used to redirect custom stream from Conan. Adds a prefix to do some custom formatting in the Logger.
    """

    def __init__(self, level, prefix: str):
        self.level = level
        self._prefix = prefix

    def write(self, message: str):
        if message != '\n':
            self.level(self._prefix + message.strip("\n"))

    def flush(self):
        """ For interface compatiblity """
        pass


class ConanApi():
    """ Wrapper around ConanAPIV1 """

    def __init__(self):
        self.conan: ConanAPIV1
        self.client_cache: ClientCache
        self.info_cache: ConanInfoCache
        self._short_path_root = Path("NULL")
        self.init_api()
        self.client_version = client_version

    def init_api(self):
        """ Instantiate the internal Conan api. In some cases it needs to be instatiated anew. """
        self.conan, _, _ = ConanAPIV1.factory()
        self.conan.user_io = UserIO(out=ConanOutput(LoggerWriter(
            Logger().info, CONAN_LOG_PREFIX), LoggerWriter(Logger().error, CONAN_LOG_PREFIX)))
        self.conan.create_app()
        self.conan.user_io.disable_input()  # error on inputs - nowhere to enter
        if self.conan.app:
            self.client_cache = self.conan.app.cache
        else:
            raise NotImplementedError
        # Experimental fast search - Conan search_packages is VERY slow
        # HACK: Removed the  @api_method decorator by getting the original function from the closure attribute
        self.search_packages = self.conan.search_packages.__closure__[0].cell_contents
        # don't hang on startup
        try:  # use try-except because of Conan 1.24 envvar errors in tests
            self.remove_locks()
        except Exception as error:
            Logger().debug(str(error))
        self.info_cache = ConanInfoCache(base_path, self.get_all_local_refs())

    ### General commands ###

    def remove_locks(self):
        self.conan.remove_locks()
        Logger().info("Removed Conan cache locks.")

    def get_remotes(self, include_disabled=False) -> List[Remote]:
        remotes = []
        try:
            if include_disabled:
                remotes = self.conan.remote_list()
            else:
                remotes = self.client_cache.registry.load_remotes().values()
        except Exception as e:
            Logger().error(f"Error while reading remotes file: {str(e)}")
        return remotes
    
    def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]: # user_name, autheticated
        user_info = self.conan.users_list(remote_name).get("remotes", {})
        if len(user_info) < 1:
            return ("", False)
        try:
            return (str(user_info[0].get("user_name", "")), user_info[0].get("authenticated", False))
        except Exception:
            Logger().warning(f"Can't get user info for {remote_name}")
            return ("", False)

    def get_short_path_root(self) -> Path:
        """ Return short path root for Windows. Sadly there is no built-in way to do  """
        # only need to get once
        if self._short_path_root.exists() or platform.system() != "Windows":
            return self._short_path_root
        temp_dir: str = path_shortener(tempfile.mkdtemp(), True)
        gen_short_path = Path(temp_dir)
        short_path_root = gen_short_path.parents[1]
        shutil.rmtree(gen_short_path.parent, ignore_errors=True)
        return short_path_root

    def get_package_folder(self, conan_ref: ConanFileReference, package_id: str) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        try:
            layout = self.client_cache.package_layout(conan_ref)
            return Path(layout.package(PackageReference(conan_ref, package_id)))
        except Exception:  # gotta catch 'em all!
            return Path("NULL")

    def get_export_folder(self, conan_ref: ConanFileReference) -> Path:
        """ Get the export folder form a reference """
        layout = self.client_cache.package_layout(conan_ref)
        if layout:
            return Path(layout.export())
        return Path("NULL")

    def get_conanfile_path(self, conan_ref: ConanFileReference) -> Path:
        if conan_ref not in self.get_all_local_refs():
            self.conan.info(self.generate_canonical_ref(conan_ref))
        layout = self.client_cache.package_layout(conan_ref)
        if layout:
            return Path(layout.conanfile())
        return Path("NULL")

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanFileReference, conan_settings:  Dict[str, str] = {},
                          conan_options: Dict[str, str] = {}, update=True) -> Tuple[str, Path]:
        """
        Try to install a conan reference (without id) with the provided extra information.
        Uses plain conan install (No auto determination of best matching package)
        Returns the actual pkg_id and the package path.
        """
        pkg_id = ""
        try:
            infos = self.conan.install_reference(
                conan_ref, settings=conan_settings, options=conan_options, update=update)
            if not infos.get("error", True):
                pkg_id = infos.get("installed", [{}])[0].get("packages", [{}])[0].get("id", "")
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        except ConanException as error:
            Logger().error(f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return (pkg_id, Path("NULL"))

    def install_package(self, conan_ref: ConanFileReference, package: ConanPkg, update=True) -> bool:
        """
        Try to install a conan package (id) with the provided extra information.
        Returns True, if installation was succesfull.
        """
        package_id = package.get("id", "")
        options_list = _create_key_value_pair_list(package.get("options", {}))
        settings_list = _create_key_value_pair_list(package.get("settings", {}))
        Logger().info(
            f"Installing '<b>{str(conan_ref)}</b>':{package_id} with settings: {str(settings_list)}, options: {str(options_list)}")
        try:
            self.conan.install_reference(conan_ref, update=update,
                                         settings=settings_list, options=options_list)
            # Update cache with this package
            self.info_cache.update_local_package_path(
                conan_ref, self.get_package_folder(conan_ref, package.get("id", "")))
            return True
        except ConanException as error:
            Logger().error(f"Can't install package '<b>{str(conan_ref)}</b>': {str(error)}")
            return False

    def get_path_or_auto_install(self, conan_ref: ConanFileReference, conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
        """ Return the pkg_id and package folder of a conan reference 
        and auto-install it with the best matching package, if it is not available """

        pkg_id, path = self.get_best_matching_package_path(conan_ref, conan_options)
        if pkg_id:
            return pkg_id, path

        Logger().info(f"'<b>{conan_ref}</b>' with options {repr(conan_options)} is not installed.")

        pkg_id, path = self.install_best_matching_package(conan_ref, conan_options, update=update)
        return pkg_id, path

    def install_best_matching_package(self, conan_ref: ConanFileReference,
                                      conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
        packages: List[ConanPkg] = self.get_matching_package_in_remotes(conan_ref, conan_options)
        if not packages:
            self.info_cache.invalidate_remote_package(conan_ref)
            return ("", Path("NULL"))

        if self.install_package(conan_ref, packages[0], update):
            package = self.find_best_local_package(conan_ref, conan_options)
            pkg_id = package.get("id", "")
            if not pkg_id:
                return (pkg_id, Path("NULL"))
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        return ("", Path("NULL"))

    # Local References and Packages

    def get_best_matching_package_path(self, conan_ref: ConanFileReference, conan_options: Dict[str, str] = {}) -> Tuple[str, Path]:
        package = self.find_best_local_package(conan_ref, conan_options)
        if package.get("id", ""):
            return package.get("id", ""), self.get_package_folder(conan_ref, package.get("id", ""))
        return "", Path("NULL")

    def get_all_local_refs(self) -> List[ConanFileReference]:
        """ Returns all locally installed conan references """
        return self.client_cache.all_refs()

    def get_local_pkgs_from_ref(self, conan_ref: ConanFileReference) -> List[ConanPkg]:
        """ Returns all installed pkg ids for a reference. """
        result: List[ConanPkg] = []
        response = {}
        try:
            response = self.search_packages(self.conan, self.generate_canonical_ref(conan_ref))
        except Exception as error:
            Logger().debug(f"{str(error)}")
            return result
        if not response.get("error", True):
            try:
                result = response.get("results", [{}])[0].get("items", [{}])[0].get("packages", [{}])
            except Exception:
                Logger().error(f"Received invalid package response format for {str(conan_ref)}")
        return result

    def get_local_pkg_from_id(self, pkg_ref: PackageReference) -> ConanPkg:
        """ Returns an installed pkg from reference and id """

        package = None
        for package in self.get_local_pkgs_from_ref(pkg_ref.ref):
            if package.get("id", "") == pkg_ref.id:
                return package
        return {"id": ""}

    def find_best_local_package(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {}) -> ConanPkg:
        """ Find a package in the local cache """
        packages = self.find_best_matching_packages(conan_ref, input_options)
        # What to if multiple ones exits? - for now simply take the first entry
        if packages:
            if len(packages) > 1:
                settings = packages[0].get("settings", {})
                id = packages[0].get("id", "")
                Logger().warning(f"Multiple matching packages found for '<b>{str(conan_ref)}</b>'!\n"
                                 f"Choosing this: {id} ({self.build_conan_profile_name_alias(settings)})")
            # Update cache with this package
            self.info_cache.update_local_package_path(
                conan_ref, self.get_package_folder(conan_ref, packages[0].get("id", "")))
            return packages[0]
        Logger().debug(f"No matching packages found for <b>{str(conan_ref)}</b>")
        return {"id": ""}

    # Remote References and Packages

    def search_query_in_remotes(self, query: str, remote="all") -> List[ConanFileReference]:
        """ Search in all remotes for a specific query. """
        res_list = []
        search_results = []
        try:
            # no query possible with pattern
            search_results = self.conan.search_recipes(
                query, remote_name=remote, case_sensitive=False).get("results", None)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []
        if not search_results:
            return res_list

        for res in search_results:
            for item in res.get("items", []):
                res_list.append(ConanFileReference.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        return res_list

    def search_recipe_alternatives_in_remotes(self, conan_ref: ConanFileReference) -> List[ConanFileReference]:
        """ Search in all remotes for all versions of a conan ref """
        search_results = []
        local_results = []
        try:
            # no query possible with pattern
            search_results: List = self.conan.search_recipes(f"{conan_ref.name}/*@*/*",
                                                             remote_name="all").get("results", None)
        except Exception as e:
            Logger().warning(str(e))
        try:
            if SEARCH_APP_VERSIONS_IN_LOCAL_CACHE:
                local_results: List = self.conan.search_recipes(f"{conan_ref.name}/*@*/*",
                                                                remote_name=None).get("results", None)
        except Exception as e:
            Logger().warning(str(e))
            return []

        res_list: List[ConanFileReference] = []
        for res in search_results + local_results:
            for item in res.get("items", []):
                res_list.append(ConanFileReference.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        # update cache
        self.info_cache.update_remote_package_list(res_list)
        return res_list

    def get_packages_in_remote(self, conan_ref: ConanFileReference, remote: Optional[str], query=None) -> List[ConanPkg]:
        found_pkgs: List[ConanPkg] = []
        try:
            search_results = self.conan.search_packages(conan_ref.full_str(), query=query,
                                                        remote_name=remote).get("results", None)
            if search_results:
                found_pkgs = search_results[0].get("items")[0].get("packages")
            Logger().debug(str(found_pkgs))
        except ConanException:  # no problem, next
            return []
        return found_pkgs

    def get_remote_pkg_from_id(self, pkg_ref: PackageReference) -> ConanPkg:
        """ Returns a remote pkg from reference and id """
        package = None
        for remote in self.get_remotes():
            packages = self.get_packages_in_remote(pkg_ref.ref, remote.name)
            for package in packages:
                if package.get("id", "") == pkg_ref.id:
                    return package
        return {"id": ""}

    def get_matching_package_in_remotes(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {}) -> List[ConanPkg]:
        """ Find a package with options in the remotes """
        for remote in self.get_remotes():
            packages = self.find_best_matching_packages(conan_ref, input_options, remote.name)
            if packages:
                return packages
        Logger().info(f"Can't find a matching package '<b>{str(conan_ref)}</b>' in the remotes")
        return []

    def find_best_matching_packages(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {},
                                    remote: Optional[str] = None) -> List[ConanPkg]:
        """
        This method tries to find the best matching packages either locally or in a remote,
        based on the users machine and the supplied options.
        """
        # skip search on default invalid recipe
        if str(conan_ref) == INVALID_CONAN_REF:
            return []

        found_pkgs: List[ConanPkg] = []
        default_settings: Dict[str, str] = {}
        try:
            default_settings = dict(self.client_cache.default_profile.settings)
            query = f"(arch=None OR arch={default_settings.get('arch')})" \
                    f" AND (arch_build=None OR arch_build={default_settings.get('arch_build')})" \
                    f" AND (os=None OR os={default_settings.get('os')})"\
                    f" AND (os_build=None OR os_build={default_settings.get('os_build')})"
            found_pkgs = self.get_packages_in_remote(conan_ref, remote, query)
        except Exception:  # no problem, next
            return []

        # remove debug releases
        no_debug_pkgs = list(filter(lambda pkg: pkg.get("settings", {}).get(
            "build_type", "").lower() != "debug", found_pkgs))
        # check, if a package remained and only then take the result
        if no_debug_pkgs:
            found_pkgs = no_debug_pkgs

        # filter the found packages by the user options
        if input_options:
            found_pkgs = list(filter(lambda pkg: input_options.items() <=
                                     pkg.get("options", {}).items(), found_pkgs))
            if not found_pkgs:
                Logger().warning(
                    f"Can't find a matching package '{str(conan_ref)}' for options {str(input_options)}")
                return found_pkgs
        # get a set of existing options and reduce default options with them
        min_opts_set = set(map(lambda pkg: frozenset(tuple(pkg.get("options", {}).keys())), found_pkgs))
        min_opts_list = frozenset()
        if min_opts_set:
            min_opts_list = min_opts_set.pop()

        # this calls external code of the recipe
        try:
            default_options = self._resolve_default_options(
                self.conan.inspect(str(conan_ref), attributes=["default_options"]).get("default_options", {}))
        except Exception:
            default_options = {}

        if default_options:
            default_options = dict(filter(lambda opt: opt[0] in min_opts_list, default_options.items()))
            # patch user input into default options to combine the two
            default_options.update(input_options)
            # convert vals to string
            default_str_options: Dict[str, str] = dict([key, str(value)]
                                                       for key, value in default_options.items())
            if len(found_pkgs) > 1:
                comb_opts_pkgs = list(filter(lambda pkg: default_str_options.items() <=
                                             pkg.get("options", {}).items(), found_pkgs))
                if comb_opts_pkgs:
                    found_pkgs = comb_opts_pkgs

        # now we have all matching packages, but with potentially different compilers
        # reduce with default settings
        if len(found_pkgs) > 1:
            same_comp_pkgs = list(filter(lambda pkg: default_settings.get("compiler", "") ==
                                         pkg.get("settings", {}).get("compiler", ""), found_pkgs))
            if same_comp_pkgs:
                found_pkgs = same_comp_pkgs

            same_comp_version_pkgs = list(filter(lambda pkg: default_settings.get("compiler.version", "") ==
                                                 pkg.get("settings", {}).get("compiler.version", ""), found_pkgs))
            if same_comp_version_pkgs:
                found_pkgs = same_comp_version_pkgs
        return found_pkgs

    @staticmethod
    def _resolve_default_options(default_options_ret: Any) -> Dict[str, Any]:
        """ Default options can be a a dict or name=value as string, or a tuple of it """
        default_options: Dict[str, Any] = {}
        if default_options_ret and isinstance(default_options_ret, str):
            default_option_str = default_options_ret.split("=")
            default_options.update({default_option_str[0]: default_option_str[1]})
        elif default_options_ret and isinstance(default_options_ret, (list, tuple)):
            for default_option in default_options_ret:
                default_option_str = default_option.split("=")
                default_options.update({default_option_str[0]: default_option_str[1]})
        else:
            default_options = default_options_ret
        return default_options

    @staticmethod
    def generate_canonical_ref(conan_ref: ConanFileReference) -> str:
        if conan_ref.user is None and conan_ref.channel is None:
            return str(conan_ref) + "@_/_"
        return str(conan_ref)

    @staticmethod
    def build_conan_profile_name_alias(settings: Dict[str, str]) -> str:
        """ Build a  human readable pseduo profile name, like Windows_x64_vs16_v142_release """
        if not settings:
            return "No Settings"

        os = settings.get("os", "")
        if not os:
            os = settings.get("os_target", "")
            if not os:
                os = settings.get("os_build", "")

        arch = settings.get("arch", "")
        if not arch:
            arch = settings.get("arch_target", "")
            if not arch:
                arch = settings.get("arch_build", "")
        if arch == "x86_64":  # shorten x64
            arch = "x64"

        comp = settings.get("compiler", "")
        if comp == "Visual Studio":
            comp = "vs"
        comp_ver = settings.get("compiler.version", "")
        comp_text = comp.lower() + comp_ver.lower()

        comp_toolset = settings.get("compiler.toolset", "")

        bt = settings.get("build_type", "")

        alias = os
        for item in [arch.lower(), comp_text, comp_toolset.lower(), bt.lower()]:
            if item:
                alias += "_" + item

        return alias


class ConanCleanup():

    def __init__(self, conan_api: ConanApi) -> None:
        self._conan_api = conan_api

    def get_cleanup_cache_paths(self) -> List[str]:
        """ Get a list of orphaned short path and cache folders """
        # Blessed are the users Microsoft products!
        if platform.system() != "Windows":
            return []
        return self.get_orphaned_references() + self.get_orphaned_packages()

    def get_orphaned_references(self):
        del_list = []
        for ref in self._conan_api.client_cache.all_refs():
            ref_cache = self._conan_api.client_cache.package_layout(ref)
            try:
                package_ids = ref_cache.package_ids()
            except Exception:
                package_ids = ref_cache.packages_ids()  # old API of Conan
            for pkg_id in package_ids:
                short_path_dir = self._conan_api.get_package_folder(ref, pkg_id)
                pkg_id_dir = None
                if not isinstance(ref_cache, PackageEditableLayout):
                    pkg_id_dir = Path(ref_cache.packages()) / pkg_id
                if not short_path_dir.exists():
                    Logger().debug(f"Can't find {str(short_path_dir)} for {str(ref)}")
                    if pkg_id_dir:
                        del_list.append(str(pkg_id_dir))
        return del_list

    def get_orphaned_packages(self):
        """ Reverse search for orphaned packages on windows short paths """
        del_list = []
        short_path_folders = [f for f in self._conan_api.get_short_path_root().iterdir() if f.is_dir()]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if rp_file.is_file():
                with open(str(rp_file)) as fp:
                    real_path = fp.read()
                try:
                    if not Path(real_path).is_dir():
                        Logger().debug(f"Can't find {real_path} for {str(short_path)}")
                        del_list.append(str(short_path))
                except Exception:
                    Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
        return del_list


def _create_key_value_pair_list(input_dict: Dict[str, str]) -> List[str]:
    """
    Helper to create name=value string list from dict
    Filters "ANY" options.
    """
    res_list: List[str] = []
    if not input_dict:
        return res_list
    for name, value in input_dict.items():
        value = str(value)
        # this is not really safe, but there can be wild values...
        if "any" in value.lower() or "none" in value.lower():
            continue
        res_list.append(name + "=" + value)
    return res_list
