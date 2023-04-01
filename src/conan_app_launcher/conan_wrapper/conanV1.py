import os
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from conan_app_launcher.conan_wrapper.types import ConanPkg, ConanRef, PkgRef,  ConanUnifiedApi, LoggerWriter, create_key_value_pair_list

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
    from .conan_cache import ConanInfoCache
    from conans.client.conan_api import (ClientCache, ConanAPIV1, UserIO,
                                         client_version)

    from conans.client.output import ConanOutput
    from conans.errors import ConanException

try:
    from conans.util.windows import path_shortener
except Exception:
    pass

from conan_app_launcher import (CONAN_LOG_PREFIX, INVALID_CONAN_REF, INVALID_PATH,
                                SEARCH_APP_VERSIONS_IN_LOCAL_CACHE, user_save_path)
from conan_app_launcher.app.logger import Logger


class ConanApi(ConanUnifiedApi):
    """ Wrapper around ConanAPIV1 """

    def __init__(self):
        self.conan: "ConanAPIV1"
        self.client_cache: "ClientCache"
        self.info_cache: "ConanInfoCache"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        """ Instantiate the internal Conan api. In some cases it needs to be instatiated anew. """
        from conans.client.conan_api import (ClientCache, ConanAPIV1, UserIO)
        from conans.client.output import ConanOutput
        self.conan = ConanAPIV1(output=ConanOutput(LoggerWriter(
            Logger().info, CONAN_LOG_PREFIX), LoggerWriter(Logger().error, CONAN_LOG_PREFIX)))
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
        self.search_packages = self.conan.search_packages.__closure__[0].cell_contents  # type: ignore
        # don't hang on startup
        try:  # use try-except because of Conan 1.24 envvar errors in tests
            self.remove_locks()
        except Exception as e:
            Logger().debug(str(e))
        from .conan_cache import ConanInfoCache
        self.info_cache = ConanInfoCache(user_save_path, self.get_all_local_refs())
        return self

    ### General commands ###

    def remove_locks(self):
        self.conan.remove_locks()
        Logger().info("Removed Conan cache locks.")

    def get_remotes(self, include_disabled=False) -> List["Remote"]:
        remotes = []
        try:
            if include_disabled:
                remotes = self.conan.remote_list()
            else:
                remotes = self.client_cache.registry.load_remotes().values()
        except Exception as e:
            Logger().error(f"Error while reading remotes file: {str(e)}")
        return remotes

    def get_profiles(self) -> List[str]:
        return self.conan.profile_list()

    def get_profile_settings(self, profile_name: str) -> Dict[str, str]:
        profile = self.conan.read_profile(profile_name)
        if not profile:
            return {}
        return dict(profile.settings)

    def get_profiles_with_settings(self) -> Dict[str, Dict[str, str]]:
        profiles_dict = {}
        for profile in self.get_profiles():
            profiles_dict[profile] = self.get_profile_settings(profile)
        return profiles_dict

    def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:  # user_name, autheticated
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
        short_home = os.getenv("CONAN_USER_HOME_SHORT")
        if not short_home:
            drive = os.path.splitdrive(self.client_cache.cache_folder)[0].upper()
            short_home = os.path.join(drive, os.sep, ".conan")
        os.makedirs(short_home, exist_ok=True)
        return Path(short_home)

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            layout = self.client_cache.package_layout(conan_ref)
            return Path(layout.package(PkgRef(conan_ref, package_id)))
        except Exception:  # gotta catch 'em all!
            return Path(INVALID_PATH)

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        """ Get the export folder form a reference """
        layout = self.client_cache.package_layout(conan_ref)
        if layout:
            return Path(layout.export())
        return Path(INVALID_PATH)

    def get_conanfile_path(self, conan_ref: ConanRef) -> Path:
        try:
            if conan_ref not in self.get_all_local_refs():
                self.conan.info(self.generate_canonical_ref(conan_ref))
            layout = self.client_cache.package_layout(conan_ref)
            if layout:
                return Path(layout.conanfile())
        except Exception as e:
            Logger().error(f"Can't get conanfile: {str(e)}")
        return Path(INVALID_PATH)

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, conan_settings:  Dict[str, str] = {},
                          conan_options: Dict[str, str] = {}, update=True) -> Tuple[str, Path]:
        """
        Try to install a conan reference (without id) with the provided extra information.
        Uses plain conan install (No auto determination of best matching package)
        Returns the actual pkg_id and the package path.
        """
        from conans.errors import ConanException
        pkg_id = ""
        options_list = create_key_value_pair_list(conan_options)
        settings_list = create_key_value_pair_list(conan_settings)
        Logger().info(
            f"Installing '<b>{str(conan_ref)}</b>' with settings: {str(settings_list)}, "
            f"options: {str(options_list)} and update={update}\n")
        try:
            infos = self.conan.install_reference(
                conan_ref, settings=settings_list, options=options_list, update=update)
            if not infos.get("error", True):
                pkg_id = infos.get("installed", [{}])[0].get("packages", [{}])[0].get("id", "")
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        except ConanException as error:
            Logger().error(f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return (pkg_id, Path(INVALID_PATH))

    def install_package(self, conan_ref: ConanRef, package: ConanPkg, update=True) -> bool:
        """
        Try to install a conan package (id) with the provided extra information.
        Returns True, if installation was succesfull.
        """
        from conans.errors import ConanException
        package_id = package.get("id", "")
        options_list = create_key_value_pair_list(package.get("options", {}))
        settings_list = create_key_value_pair_list(package.get("settings", {}))
        Logger().info(
            f"Installing '<b>{str(conan_ref)}</b>':{package_id} with settings: {str(settings_list)}, "
            f"options: {str(options_list)} and update={update}\n")
        try:
            self.conan.install_reference(conan_ref, update=update,
                                         settings=settings_list, options=options_list)
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            # Update cache with this package
            self.info_cache.update_local_package_path(
                conan_ref, self.get_package_folder(conan_ref, package.get("id", "")))
            return True
        except ConanException as e:
            Logger().error(f"Can't install package '<b>{str(conan_ref)}</b>': {str(e)}")
            return False

    def get_path_or_auto_install(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
        """ Return the pkg_id and package folder of a conan reference 
        and auto-install it with the best matching package, if it is not available """
        if not update:
            pkg_id, path = self.get_best_matching_package_path(conan_ref, conan_options)
            if pkg_id:
                return pkg_id, path
            Logger().info(
                f"'<b>{conan_ref}</b>' with options {repr(conan_options)} is not installed. Searching for packages to install...")

        pkg_id, path = self.install_best_matching_package(conan_ref, conan_options, update=update)
        return pkg_id, path

    def install_best_matching_package(self, conan_ref: ConanRef,
                                      conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
        packages: List[ConanPkg] = self.get_matching_package_in_remotes(conan_ref, conan_options)
        if not packages:
            self.info_cache.invalidate_remote_package(conan_ref)
            return ("", Path(INVALID_PATH))

        if self.install_package(conan_ref, packages[0], update):
            package = self.find_best_local_package(conan_ref, conan_options)
            pkg_id = package.get("id", "")
            if not pkg_id:
                return (pkg_id, Path(INVALID_PATH))
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        return ("", Path(INVALID_PATH))

    # Local References and Packages

    def get_best_matching_package_path(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}) -> Tuple[str, Path]:
        package = self.find_best_local_package(conan_ref, conan_options)
        if package.get("id", ""):
            return package.get("id", ""), self.get_package_folder(conan_ref, package.get("id", ""))
        return "", Path(INVALID_PATH)

    def get_all_local_refs(self) -> List[ConanRef]:
        """ Returns all locally installed conan references """
        return self.client_cache.all_refs()

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List[ConanPkg]:
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

    def get_local_pkg_from_id(self, pkg_ref: PkgRef) -> ConanPkg:
        """ Returns an installed pkg from reference and id """
        package = None
        for package in self.get_local_pkgs_from_ref(pkg_ref.ref):
            if package.get("id", "") == pkg_ref.id:
                return package
        return {"id": ""}

    def get_local_pkg_from_path(self, conan_ref: ConanRef, path: Path):
        """ For reverse lookup - give info from path """
        found_package = None
        for package in self.get_local_pkgs_from_ref(conan_ref):
            if self.get_package_folder(conan_ref, package.get("id", "")) == path:
                found_package = package
                break
        return found_package

    def find_best_local_package(self, conan_ref: ConanRef, input_options: Dict[str, str] = {}) -> ConanPkg:
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

    def search_query_in_remotes(self, query: str, remote_name="all") -> List[ConanRef]:
        """ Search in all remotes for a specific query. """
        res_list = []
        search_results = []
        try:
            # no query possible with pattern
            search_results = self.conan.search_recipes(
                query, remote_name=remote_name, case_sensitive=False).get("results", None)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []
        if not search_results:
            return res_list

        for res in search_results:
            for item in res.get("items", []):
                res_list.append(ConanRef.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        self.info_cache.update_remote_package_list(res_list)
        return res_list

    def search_recipe_alternatives_in_remotes(self, conan_ref: ConanRef) -> List[ConanRef]:
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

        res_list: List[ConanRef] = []
        for res in search_results + local_results:
            for item in res.get("items", []):
                res_list.append(ConanRef.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        # update cache
        self.info_cache.update_remote_package_list(res_list)
        return res_list

    def get_packages_in_remote(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
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

    def get_remote_pkg_from_id(self, pkg_ref: PkgRef) -> ConanPkg:
        """ Returns a remote pkg from reference and id """
        package = None
        for remote in self.get_remotes():
            packages = self.get_packages_in_remote(pkg_ref.ref, remote.name)
            for package in packages:
                if package.get("id", "") == pkg_ref.id:
                    return package
        return {"id": ""}

    def get_matching_package_in_remotes(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}) -> List[ConanPkg]:
        """ Find a package with options in the remotes """
        for remote in self.get_remotes():
            packages = self.find_best_matching_packages(conan_ref, conan_options, remote.name)
            if packages:
                return packages
        Logger().info(
            f"Can't find a package '<b>{str(conan_ref)}</b>' with options {conan_options} in the <b>remotes</b>")
        return []

    def find_best_matching_packages(self, conan_ref: ConanRef, input_options: Dict[str, str] = {},
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
            # type: ignore - dynamic prop is ok in try-catch
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
