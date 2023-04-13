import os
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .types import ConanPkg, ConanRef, ConanPkgRef, ConanException, LoggerWriter, create_key_value_pair_list
from .unified_api import ConanUnifiedApi

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
    from .conan_cache import ConanInfoCache
    from conans.client.conan_api import ClientCache, ConanAPIV1

from conan_app_launcher import (CONAN_LOG_PREFIX, INVALID_CONAN_REF, INVALID_PATH,
                                SEARCH_APP_VERSIONS_IN_LOCAL_CACHE, user_save_path)
from conan_app_launcher.app.logger import Logger


class ConanApi(ConanUnifiedApi):
    """ Wrapper around ConanAPIV1 """

    def __init__(self):
        self._conan: "ConanAPIV1"
        self.info_cache: "ConanInfoCache"
        self._client_cache: "ClientCache"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        """ Instantiate the internal Conan api. In some cases it needs to be instatiated anew. """
        from conans.client.conan_api import (ConanAPIV1, UserIO)
        from conans.client.output import ConanOutput
        self._conan = ConanAPIV1(output=ConanOutput(LoggerWriter(
            Logger().info, CONAN_LOG_PREFIX), LoggerWriter(Logger().error, CONAN_LOG_PREFIX)))
        self._conan.user_io = UserIO(out=ConanOutput(LoggerWriter(
            Logger().info, CONAN_LOG_PREFIX), LoggerWriter(Logger().error, CONAN_LOG_PREFIX)))
        self._conan.create_app()
        self._conan.user_io.disable_input()  # error on inputs - nowhere to enter
        if self._conan.app:
            self._client_cache = self._conan.app.cache
        else:
            raise NotImplementedError
        # Experimental fast search - Conan search_packages is VERY slow
        # HACK: Removed the  @api_method decorator by getting the original function from the closure attribute
        self.search_packages = self._conan.search_packages.__closure__[0].cell_contents  # type: ignore
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
        self._conan.remove_locks()
        Logger().info("Removed Conan cache locks.")

    def get_remotes(self, include_disabled=False) -> List["Remote"]:
        remotes = []
        try:
            if include_disabled:
                remotes = self._conan.remote_list()
            else:
                remotes = self._client_cache.registry.load_remotes().values()
        except Exception as e:
            Logger().error(f"Error while reading remotes file: {str(e)}")
        return remotes

    def get_profiles(self) -> List[str]:
        return self._conan.profile_list()

    def get_profile_settings(self, profile_name: str) -> Dict[str, str]:
        profile = self._conan.read_profile(profile_name)
        if not profile:
            return {}
        return dict(profile.settings)

    def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:  # user_name, autheticated
        user_info = self._conan.users_list(remote_name).get("remotes", {})
        if len(user_info) < 1:
            return ("", False)
        try:
            return (str(user_info[0].get("user_name", "")), user_info[0].get("authenticated", False))
        except Exception:
            Logger().warning(f"Can't get user info for {remote_name}")
            return ("", False)

    def get_short_path_root(self) -> Path:
        # only need to get once
        if self._short_path_root.exists() or platform.system() != "Windows":
            return self._short_path_root
        short_home = os.getenv("CONAN_USER_HOME_SHORT")
        if not short_home:
            drive = os.path.splitdrive(self._client_cache.cache_folder)[0].upper()
            short_home = os.path.join(drive, os.sep, ".conan")
        os.makedirs(short_home, exist_ok=True)
        return Path(short_home)

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            layout = self._client_cache.package_layout(conan_ref)
            return Path(layout.package(ConanPkgRef(conan_ref, package_id)))
        except Exception:  # gotta catch 'em all!
            return Path(INVALID_PATH)

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        layout = self._client_cache.package_layout(conan_ref)
        if layout:
            return Path(layout.export())
        return Path(INVALID_PATH)

    def get_conanfile_path(self, conan_ref: ConanRef) -> Path:
        try:
            if conan_ref not in self.get_all_local_refs():
                self._conan.info(self.generate_canonical_ref(conan_ref))
            layout = self._client_cache.package_layout(conan_ref)
            if layout:
                return Path(layout.conanfile())
        except Exception as e:
            Logger().error(f"Can't get conanfile: {str(e)}")
        return Path(INVALID_PATH)

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, profile="", conan_settings: Dict[str, str]={},
                          conan_options: Dict[str, str]={}, update=True) -> Tuple[str, Path]:
        package_id = ""
        options_list = create_key_value_pair_list(conan_options)
        settings_list = create_key_value_pair_list(conan_settings)
        install_message =  f"Installing '<b>{str(conan_ref)}</b>' with profile: {profile}, " \
        f"settings: {str(settings_list)}, " \
        f"options: {str(options_list)} and update={update}\n"
        Logger().info(install_message)
        profile_names = None
        if profile:
            profile_names = [profile_names]
        try:
            infos = self._conan.install_reference(
                conan_ref, settings=settings_list, options=options_list, update=update, profile_names=profile_names)
            if not infos.get("error", True):
                package_id = infos.get("installed", [{}])[0].get("packages", [{}])[0].get("id", "")
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            # Update cache with this package
            package_path = self.get_package_folder(conan_ref, package_id)
            self.info_cache.update_local_package_path(conan_ref, package_path)
            return package_id, package_path
        except ConanException as error:
            Logger().error(f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return package_id, Path(INVALID_PATH)

    # Local References and Packages

    def get_all_local_refs(self) -> List[ConanRef]:
        return self._client_cache.all_refs()

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List[ConanPkg]:
        result: List[ConanPkg] = []
        response = {}
        try:
            response = self.search_packages(self._conan, self.generate_canonical_ref(conan_ref))
        except Exception as error:
            Logger().debug(f"{str(error)}")
            return result
        if not response.get("error", True):
            try:
                result = response.get("results", [{}])[0].get("items", [{}])[0].get("packages", [{}])
            except Exception:
                Logger().error(f"Received invalid package response format for {str(conan_ref)}")
        return result

    # Remote References and Packages

    def search_recipes_in_remotes(self, query: str, remote_name="all") -> List[ConanRef]:
        res_list = []
        search_results = []
        try:
            # no query possible with pattern
            search_results = self._conan.search_recipes(
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
        search_results = []
        local_results = []
        try:
            # no query possible with pattern
            search_results: List = self._conan.search_recipes(f"{conan_ref.name}/*@*/*",
                                                             remote_name="all").get("results", None)
        except Exception as e:
            Logger().warning(str(e))
        try:
            if SEARCH_APP_VERSIONS_IN_LOCAL_CACHE:
                local_results: List = self._conan.search_recipes(f"{conan_ref.name}/*@*/*",
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

    def get_remote_pkgs_from_ref(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
        found_pkgs: List[ConanPkg] = []
        try:
            search_results = self._conan.search_packages(conan_ref.full_str(), query=query,
                                                        remote_name=remote).get("results", None)
            if search_results:
                found_pkgs = search_results[0].get("items")[0].get("packages")
            Logger().debug(str(found_pkgs))
        except ConanException:  # no problem, next
            return []
        return found_pkgs

    def find_best_matching_packages(self, conan_ref: ConanRef, input_options: Dict[str, str] = {},
                                    remote: Optional[str] = None) -> List[ConanPkg]:
        # skip search on default invalid recipe
        if str(conan_ref) == INVALID_CONAN_REF:
            return []

        found_pkgs: List[ConanPkg] = []
        default_settings: Dict[str, str] = {}
        try:
            # type: ignore - dynamic prop is ok in try-catch
            default_settings = dict(self._client_cache.default_profile.settings) # type: ignore
            query = f"(arch=None OR arch={default_settings.get('arch')})" \
                    f" AND (arch_build=None OR arch_build={default_settings.get('arch_build')})" \
                    f" AND (os=None OR os={default_settings.get('os')})"\
                    f" AND (os_build=None OR os_build={default_settings.get('os_build')})"
            found_pkgs = self.get_remote_pkgs_from_ref(conan_ref, remote, query)
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
                self._conan.inspect(str(conan_ref), attributes=["default_options"]).get("default_options", {}))
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
