import os
import inspect as python_inspect
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from conan_app_launcher import (INVALID_CONAN_REF, INVALID_PATH,user_save_path)
from conan_app_launcher.app.logger import Logger
from .types import ConanAvailableOptions, ConanOptions, ConanPkg, ConanRef, ConanPkgRef, ConanException, ConanSettings, create_key_value_pair_list
from .unified_api import ConanUnifiedApi

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
    from .conan_cache import ConanInfoCache
    from conans.client.cache.cache import ClientCache
    from conan.api.conan_api import ConanAPI

class ConanApi(ConanUnifiedApi):
    """ Wrapper around ConanAPIV2 """

    def __init__(self):
        self.info_cache: "ConanInfoCache"
        self._conan: "ConanAPI"
        self._client_cache: "ClientCache"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        from conan.api.conan_api import ConanAPI
        from conans.client.cache.cache import ClientCache
        from .conan_cache import ConanInfoCache
        self._conan = ConanAPI()
        self._client_cache = ClientCache(self._conan.cache_folder)
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
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            latest_rev_ref = self._conan.list.latest_recipe_revision(conan_ref)
            latest_rev_pkg = self._conan.list.latest_package_revision(ConanPkgRef(latest_rev_ref, package_id))
            assert latest_rev_pkg
            layout = self._client_cache.pkg_layout(latest_rev_pkg)
            return Path(layout.package())
        except Exception:  # gotta catch 'em all!
            return Path(INVALID_PATH)

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        return Path(self._conan.cache.export_path(conan_ref))
    
    def get_conanfile_path(self, conan_ref: ConanRef) -> Path:
        try:
            if conan_ref not in self.get_all_local_refs():
                for remote in self.get_remotes():
                    result = self.search_recipes_in_remotes(str(conan_ref), remote_name=remote.name)
                    if result:
                        latest_rev: ConanRef = self._conan.list.latest_recipe_revision(conan_ref, remote)
                        self._conan.download.recipe(latest_rev, remote)
                        break
            path = self._conan.local.get_conanfile_path(self._conan.cache.export_path(conan_ref), os.getcwd(), py=True)
            if not path:
                return Path(INVALID_PATH)
            return Path(path)
        except Exception as e:
            Logger().error(f"Can't get conanfile: {str(e)}")
        return Path(INVALID_PATH)
    
    def get_default_settings(self) -> ConanSettings:
        from conans.client.profile_loader import ProfileLoader
        profile = ProfileLoader(self._client_cache).load_profile(Path(self._conan.profiles.get_default_host()).name)
        return dict(profile.settings)
            
    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, profile="", conan_settings: ConanSettings={},
                          conan_options: ConanOptions={}, update=True) -> Tuple[str, Path]:
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
            deps_graph = self._conan.graph.load_graph_requires(requires, None, profile_host, profile_host, None,
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
        
    def get_options_with_default_values(self, conan_ref: ConanRef) -> Tuple[ConanAvailableOptions, ConanOptions]:
        # this calls external code of the recipe
        default_options = {}
        available_options = {}
        try:
            path = self.get_conanfile_path(conan_ref)
            conanfile = self._conan.graph.load_conanfile_class(path)
            inspection = python_inspect.getmembers(conanfile)
            for field_name, field in inspection:
                if field_name == "default_options":
                    default_options = field
                elif field_name == "options":
                    available_options = field
            default_options = self._resolve_default_options(default_options)
        except Exception:
            Logger().debug(f"Error while getting default options for {str(conan_ref)}")
        return available_options, default_options

    ### Local References and Packages ###

    def get_all_local_refs(self) -> List[ConanRef]:
        return self._client_cache.all_refs()

    def get_local_pkg_from_path(self, conan_ref: ConanRef, path: Path):
        found_package = None
        for package in self.get_local_pkgs_from_ref(conan_ref):
            if self.get_package_folder(conan_ref, package.get("id", "")) == path:
                found_package = package
                break
        return found_package

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List[ConanPkg]:
        result: List[ConanPkg] = []
        if conan_ref.user == "_":
            conan_ref.user = None
        if conan_ref.channel == "_":
            conan_ref.channel = None
        conan_ref_latest: "RecipeReference" = self._conan.list.latest_recipe_revision(conan_ref) # type: ignore
        if not conan_ref_latest:
            return result
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

    ### Remote References and Packages ###

    def search_recipes_in_remotes(self, query: str, remote_name="all") -> List["ConanRef"]:
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
    
    def get_remote_pkgs_from_ref(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
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