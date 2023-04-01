import os
import inspect as python_inspect

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from conan_app_launcher.conan_wrapper.types import ConanPkg, ConanUnifiedApi
from conan_app_launcher.app.logger import Logger

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
    from .conan_cache import ConanInfoCache

from conan.api.conan_api import ConanAPI, client_version
from conans.client.cache.cache import ClientCache
from conans.errors import ConanException
from conan_app_launcher import (INVALID_CONAN_REF, INVALID_PATH,
                                user_save_path)
from conan_app_launcher.conan_wrapper.types import ConanPkg, ConanRef, PkgRef,  ConanUnifiedApi, LoggerWriter, create_key_value_pair_list

class ConanApi(ConanUnifiedApi):
    """ Wrapper around ConanAPIV2 """

    def __init__(self):
        self.conan: ConanAPI
        self.client_cache: ClientCache
        self.info_cache: "ConanInfoCache"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        self.conan = ConanAPI()
        self.client_cache = ClientCache(self.conan.cache_folder)
        from .conan_cache import ConanInfoCache
        self.info_cache = ConanInfoCache(user_save_path, self.get_all_local_refs())
        return self

    ### General commands ###

    def remove_locks(self):
        pass # command does not exist

    def get_remotes(self, include_disabled=False) -> List["Remote"]:
        remotes = []
        try:
            remotes = self.conan.remotes.list(None, only_enabled=not include_disabled)
        except Exception as e:
            Logger().error(f"Error while reading remotes: {str(e)}")
        return remotes
    
    def get_profiles(self)-> List[str]:
        return self.conan.profiles.list()

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            latest_rev_ref = self.conan.list.latest_recipe_revision(conan_ref)
            latest_rev_pkg = self.conan.list.latest_package_revision(PkgRef(latest_rev_ref, package_id))
            assert latest_rev_pkg
            layout = self.client_cache.pkg_layout(latest_rev_pkg)
            return Path(layout.package())
        except Exception:  # gotta catch 'em all!
            return Path(INVALID_PATH)

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        """ Get the export folder form a reference """
        return Path(self.conan.cache.export_path(conan_ref))


    ### Install related methods ###

    ### Local References and Packages ###

    def get_all_local_refs(self) -> List[ConanRef]:
        """ Returns all locally installed conan references """
        return self.client_cache.all_refs()

    def get_local_pkg_from_path(self, conan_ref: ConanRef, path: Path):
        """ For reverse lookup - give info from path """
        found_package = None
        for package in self.get_local_pkgs_from_ref(conan_ref):
            if self.get_package_folder(conan_ref, package.get("id", "")) == path:
                found_package = package
                break
        return found_package

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List[ConanPkg]:
        """ Returns all installed pkg ids for a reference. """
        result: List[ConanPkg] = []
        if conan_ref.user == "_":
            conan_ref.user = None
        if conan_ref.channel == "_":
            conan_ref.channel = None
        conan_ref = self.conan.list.latest_recipe_revision(conan_ref)
        refs = self.conan.list.packages_configurations(conan_ref)
        for ref, pkg_info in refs.items():
            pkg = ConanPkg()
            pkg["id"] = str(ref.package_id)
            pkg["options"] = pkg_info.get("options", {})
            pkg["settings"] = pkg_info.get("settings", {})
            pkg["requires"] = []
            pkg["outdated"] = False
            result.append(pkg)
        return result

    def get_local_pkg_from_id(self, pkg_ref: PkgRef) -> ConanPkg:
        """ Returns an installed pkg from reference and id """
        package = None
        for package in self.get_local_pkgs_from_ref(pkg_ref.ref):
            if package.get("id", "") == pkg_ref.package_id:
                return package
        return {"id": ""}

    @staticmethod
    def generate_canonical_ref(conan_ref: ConanRef) -> str:
        if conan_ref.user is None and conan_ref.channel is None:
            return str(conan_ref) + "@_/_"
        return str(conan_ref)

    def get_path_or_auto_install(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
        """ Return the pkg_id and package folder of a conan reference 
        and auto-install it with the best matching package, if it is not available """
        if not update:
            pkg_id, path = self.get_best_matching_package_path(conan_ref, conan_options)
            if pkg_id:
                return pkg_id, path
            Logger().info(
                f"'<b>{conan_ref}</b>' with options {repr(conan_options)} is not installed. Searching for packages to install...")

        # pkg_id, path = self.install_best_matching_package(conan_ref, conan_options, update=update)
        # return pkg_id, path
        return "", Path()

    def get_best_matching_package_path(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}) -> Tuple[str, Path]:
        package = self.find_best_local_package(conan_ref, conan_options)
        if package.get("id", ""):
            return package.get("id", ""), self.get_package_folder(conan_ref, package.get("id", ""))
        return "", Path(INVALID_PATH)

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
        Logger().debug(f"No matching local packages found for <b>{str(conan_ref)}</b>")
        return {"id": ""}

    ### Remote References and Packages ###

    def search_query_in_remotes(self, query: str, remote_name="all") -> List["ConanRef"]:
        """ Search in all remotes for a specific query. """
        search_results = []
        if remote_name == "all":
            remote_name = None
        try:
            # no query possible with pattern
            for remote in self.get_remotes():
                search_results: List["ConanRef"] = self.conan.search.recipes(query, remote=remote)
                # .get("results", None)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []

        search_results = list(set(search_results))  # make unique
        search_results.sort()
        return search_results

    def find_best_matching_packages(self, conan_ref: ConanRef, input_options: Dict[str, str] = {},
                                    remote: Optional[str] = None) -> List[ConanPkg]:
        """
        This method tries to find the best matching packages either locally or in a remote,
        based on the users machine and the supplied options.
        """
        # skip search on default invalid recipe
        if str(conan_ref) == INVALID_CONAN_REF:
            return []
        from conans.model.profile import Profile
        from conans.client.profile_loader import ProfileLoader

        found_pkgs: List[ConanPkg] = []
        default_settings: Dict[str, str] = {}
        try:
            # type: ignore - dynamic prop is ok in try-catch
            pr = ProfileLoader(self.client_cache).load_profile(Path(self.conan.profiles.get_default_host()).name)
            default_settings = dict(pr.settings)
            query = f"(arch=None OR arch={default_settings.get('arch')})" \
                    f" AND (os=None OR os={default_settings.get('os')})"
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
            path = self.conan.local.get_conanfile_path(self.conan.cache.export_path(conan_ref), os.getcwd(), py=True)
            conanfile = self.conan.graph.load_conanfile_class(path)
            inspection = python_inspect.getmembers_static(conanfile)
            found_field = {}
            for field_name, field in inspection:
                if field_name == "default_options":
                    found_field = field
                    break
            default_options = self._resolve_default_options(found_field)


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

    def get_packages_in_remote(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
        found_pkgs: List[ConanPkg] = []
        try:
            from conan.api.model import ListPattern
            pattern = ListPattern(str(conan_ref) + ":*", rrev=None, prev=None)
            search_results = self.conan.list.select(pattern, remote=remote, package_query=query)
            if search_results:
                latest_rev = self.conan.list.latest_recipe_revision(conan_ref)
                if latest_rev:
                    found_pkgs_dict = search_results.recipes.get(str(conan_ref), {}).get("revisions", {}).get(latest_rev.revision, {}).get("packages", {})
                    for id, info in found_pkgs_dict.items():
                        found_pkgs.append(ConanPkg(id=id, options=info.get("info", {}).get("options", {}),
                                           settings=info.get("info", {}).get("settings", {}),
                                           requires=[], outdated=False))
            Logger().debug(str(found_pkgs))
        except ConanException:  # no problem, next
            return []
        return found_pkgs

