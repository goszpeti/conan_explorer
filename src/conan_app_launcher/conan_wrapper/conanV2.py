import os
import inspect as python_inspect
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from conan_app_launcher import (INVALID_CONAN_REF, INVALID_PATH,user_save_path)
from conan_app_launcher.app.logger import Logger
from .types import ConanPkg, ConanRef, PkgRef, ConanException, create_key_value_pair_list
from .unified_api import ConanUnifiedApi

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
    from .conan_cache import ConanInfoCache
    from conans.client.cache.cache import ClientCache
    from conan.api.conan_api import ConanAPI

class ConanApi(ConanUnifiedApi):
    """ Wrapper around ConanAPIV2 """

    def __init__(self):
        self.client_cache: "ClientCache"
        self.info_cache: "ConanInfoCache"
        self._conan: "ConanAPI"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        from conan.api.conan_api import ConanAPI
        from conans.client.cache.cache import ClientCache
        from .conan_cache import ConanInfoCache
        self._conan = ConanAPI()
        self.client_cache = ClientCache(self._conan.cache_folder)
        self.info_cache = ConanInfoCache(user_save_path, self.get_all_local_refs())
        return self

    ### General commands ###

    def remove_locks(self):
        pass # command does not exist

    def get_remotes(self, include_disabled=False) -> List["Remote"]:
        remotes = []
        try:
            remotes = self._conan.remotes.list(None, only_enabled=not include_disabled)
        except Exception as e:
            Logger().error(f"Error while reading remotes: {str(e)}")
        return remotes
    
    def get_profiles(self)-> List[str]:
        return self._conan.profiles.list()

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            latest_rev_ref = self._conan.list.latest_recipe_revision(conan_ref)
            latest_rev_pkg = self._conan.list.latest_package_revision(PkgRef(latest_rev_ref, package_id))
            assert latest_rev_pkg
            layout = self.client_cache.pkg_layout(latest_rev_pkg)
            return Path(layout.package())
        except Exception:  # gotta catch 'em all!
            return Path(INVALID_PATH)

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        """ Get the export folder form a reference """
        return Path(self._conan.cache.export_path(conan_ref))

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, profile= "", conan_settings:  Dict[str, str] = {},
                          conan_options: Dict[str, str] = {}, update=True) -> Tuple[str, Path]:
        """
        Try to install a conan reference (without id) with the provided extra information.
        Uses plain conan install (No auto determination of best matching package).
        Returns the actual pkg_id and the package path.
        """
        from conans.errors import ConanException
        pkg_id = ""
        options_list = create_key_value_pair_list(conan_options)
        settings_list = create_key_value_pair_list(conan_settings)
        install_message=  f"Installing '<b>{str(conan_ref)}</b>' with profile: {profile}, " \
        f"settings: {str(settings_list)}, " \
        f"options: {str(options_list)} and update={update}\n"
        Logger().info(install_message)
        from conan.cli.printers.graph import print_graph_packages, print_graph_basic

        try:
            # Basic collaborators, remotes, lockfile, profiles
            remotes = self._conan.remotes.list(None)
            profiles = [profile] if profile else []
            profile_host = self._conan.profiles.get_profile(profiles, settings=settings_list, options=options_list)
            requires = [conan_ref]
            deps_graph = self._conan.graph.load_graph_requires(requires, None,
                                                                profile_host, profile_host, None,
                                                                remotes, update)
            print_graph_basic(deps_graph)
            deps_graph.report_graph_error()
            self._conan.graph.analyze_binaries(deps_graph, build_mode=None, remotes=remotes, update=update,
                                            lockfile=None)
            print_graph_packages(deps_graph)
            self._conan.install.install_binaries(deps_graph=deps_graph, remotes=remotes)
            # Currently unused
            # self.conan.install.install_consumer(deps_graph=deps_graph, generators=None, output_folder=None,
            #                                 source_folder=gettempdir(), deploy=True)
            info = None
            for node in deps_graph.nodes:
                if node.ref ==conan_ref:
                    info = node
                    break
            if info is None: 
                raise ConanException("Can't read information of installed recipe from graph.")
            pkg_id = info.package_id
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            # Update cache with this package
            self.info_cache.update_local_package_path(conan_ref, self.get_package_folder(conan_ref, pkg_id))
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        except ConanException as error:
            Logger().error(f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return (pkg_id, Path(INVALID_PATH))

    def install_package(self, conan_ref: ConanRef, package: ConanPkg, update=True) -> Tuple[str, Path]:
        package_id = package.get("id", "")
        options = package.get("options", {})
        settings = package.get("settings", {})
        Logger().info(
            f"Installing '<b>{str(conan_ref)}</b>':{package_id} with settings: {str(settings)}, "
            f"options: {str(options)} and update={update}\n")
        try:
            installed_id, package_path = self.install_reference(conan_ref, update=update, conan_settings=settings, conan_options=options)
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            if installed_id != package_id:
                Logger().warning("Installed {installed_id} instead of selected {package_id}." \
                           "This can happen, if there transitive settings changed in comparison to the build time.")
            return installed_id, package_path
        except ConanException as e:
            Logger().error(f"Can't install package '<b>{str(conan_ref)}</b>': {str(e)}")
            return "", Path(INVALID_PATH)

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
        conan_ref_latest: "RecipeReference" = self._conan.list.latest_recipe_revision(conan_ref) # type: ignore
        refs = self._conan.list.packages_configurations(conan_ref_latest)
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
                search_results: List["ConanRef"] = self._conan.search.recipes(query, remote=remote)
                # .get("results", None)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []

        search_results = list(set(search_results))  # make unique
        search_results.sort()
        return search_results
    
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
        # from conans.model.profile import Profile
        from conans.client.profile_loader import ProfileLoader

        found_pkgs: List[ConanPkg] = []
        default_settings: Dict[str, str] = {}
        try:
            # type: ignore - dynamic prop is ok in try-catch
            pr = ProfileLoader(self.client_cache).load_profile(Path(self._conan.profiles.get_default_host()).name)
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
            found_pkgs = list(filter(lambda pkg: input_options.items() <= pkg.get("options", {}).items(), found_pkgs))
            if not found_pkgs:
                return found_pkgs
        # get a set of existing options and reduce default options with them
        min_opts_set = set(map(lambda pkg: frozenset(tuple(pkg.get("options", {}).keys())), found_pkgs))
        min_opts_list = frozenset()
        if min_opts_set:
            min_opts_list = min_opts_set.pop()

        # this calls external code of the recipe
        try:
            # TODO: Workaround, until there is a dedicated api function for this.
            path = self._conan.local.get_conanfile_path(self._conan.cache.export_path(conan_ref), os.getcwd(), py=True)
            conanfile = self._conan.graph.load_conanfile_class(path)
            inspection = python_inspect.getmembers(conanfile)
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
            pattern = ListPattern(str(conan_ref) + ":*", rrev="", prev="")
            search_results = None
            remote_obj = None
            if remote:
                for remote_obj in self.get_remotes():
                    if remote_obj.name == remote:
                        break
            search_results = self._conan.list.select(pattern, remote=remote_obj, package_query=query)
            if search_results:
                latest_rev = self._conan.list.latest_recipe_revision(conan_ref, remote_obj)
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

