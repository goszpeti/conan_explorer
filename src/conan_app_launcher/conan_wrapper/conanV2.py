from contextlib import chdir
import os
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from conan_app_launcher import INVALID_PATH, user_save_path
from conan_app_launcher.app.logger import Logger
from conan_app_launcher.app.typing import SignatureCheckMeta

from .types import (ConanAvailableOptions, ConanException, ConanOptions, ConanPackageId,
    ConanPackagePath, ConanPkg, ConanPkgRef, ConanRef, ConanSettings, Remote, 
    create_key_value_pair_list)
from .unified_api import ConanCommonUnifiedApi

if TYPE_CHECKING:
    from conan.api.conan_api import ConanAPI
    from conans.client.cache.cache import ClientCache
    from .conan_cache import ConanInfoCache


class ConanApi(ConanCommonUnifiedApi, metaclass=SignatureCheckMeta):
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
        self.info_cache = ConanInfoCache(
            user_save_path, self.get_all_local_refs())
        return self

    ### General commands ###

    def remove_locks(self):
        pass  # command does not exist

    def get_profiles(self) -> List[str]:
        return self._conan.profiles.list()

    def get_profile_settings(self, profile_name: str) -> ConanSettings:
        from conans.client.profile_loader import ProfileLoader
        try:
            profile = ProfileLoader(
                self._client_cache).load_profile(profile_name)
            return profile.settings
        except Exception as e:
            Logger().error(
                f"Can't get profile {profile_name} settings: {str(e)}")
        return {}

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        if not package_id:  # will give the base path ortherwise
            return Path(INVALID_PATH)
        try:
            latest_rev_ref = self._conan.list.latest_recipe_revision(conan_ref)
            latest_rev_pkg = self._conan.list.latest_package_revision(
                ConanPkgRef(latest_rev_ref, package_id))
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
                    result = self.search_recipes_in_remotes(
                        str(conan_ref), remote_name=remote.name)
                    if result:
                        latest_rev: ConanRef = self._conan.list.latest_recipe_revision(
                            conan_ref, remote)
                        self._conan.download.recipe(latest_rev, remote)
                        break
            path = self._conan.local.get_conanfile_path(
                self._conan.cache.export_path(conan_ref), os.getcwd(), py=True)
            if not path:
                return Path(INVALID_PATH)
            return Path(path)
        except Exception as e:
            Logger().error(f"Can't get conanfile: {str(e)}")
        return Path(INVALID_PATH)

    def get_default_settings(self) -> ConanSettings:
        from conans.client.profile_loader import ProfileLoader
        profile = ProfileLoader(self._client_cache).load_profile(
            Path(self._conan.profiles.get_default_host()).name)
        return dict(profile.settings)

    # user_name, authenticated
    def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:
        try:
            info = self._conan.remotes.user_info(
                self._conan.remotes.get(remote_name))
        except Exception as e:
            Logger().error(
                f"Can't get remote {remote_name} user info: {str(e)}")
            return "", False
        return str(info.get("user_name", "")), info.get("authenticated", False)

    def get_config_file_path(self) -> Path:
        return Path(self._client_cache.new_config_path)

    def get_config_entry(self, config_name: str, default_value: Any) -> Any:
        return self._client_cache.new_config.get(config_name, default_value)

    def get_revisions_enabled(self) -> bool:
        return True

    def get_settings_file_path(self) -> Path:
        return Path(self._client_cache.settings_path)

    def get_profiles_path(self) -> Path:
        return Path(self._client_cache.profiles_path)

    def get_editables_file_path(self) -> Path:
        return  Path(self._client_cache.editable_packages._edited_file)

    def get_user_home_path(self) -> Path:
        return Path(self._client_cache.cache_folder)

    def get_storage_path(self) -> Path:
        return Path(str(self._client_cache.store))

    def get_short_path_root(self) -> Path:
        # there is no short_paths feature in conan 2
        return Path(INVALID_PATH)

    # Remotes

    def get_remotes(self, include_disabled=False) -> List["Remote"]:
        remotes = []
        try:
            remotes = self._conan.remotes.list(
                None, only_enabled=not include_disabled)
        except Exception as e:
            Logger().error(f"Error while reading remotes: {str(e)}")
        return remotes

    def add_remote(self, remote_name: str, url: str, verify_ssl: bool):
        remote = Remote(remote_name, url, verify_ssl, False)
        self._conan.remotes.add(remote)

    def rename_remote(self, remote_name: str, new_name: str):
        self._conan.remotes.rename(remote_name, new_name)

    def remove_remote(self, remote_name: str):
        self._conan.remotes.remove(remote_name)

    def disable_remote(self, remote_name: str, disabled: bool):
        if disabled:
            self._conan.remotes.disable(remote_name)
        else:
            self._conan.remotes.enable(remote_name)

    def update_remote(self, remote_name: str, url: str, verify_ssl: bool, disabled: bool,
                      index: Optional[int]):
        self._conan.remotes.update(
            remote_name, url, verify_ssl, disabled, index)

    def login_remote(self, remote_name: str, user_name: str, password: str):
        self._conan.remotes.login(self._conan.remotes.get(
            remote_name), user_name, password)

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, conan_settings: Optional[ConanSettings],
            conan_options: Optional[ConanOptions]=None, profile="", update=True, quiet=False,
            generators: List[str] = []) -> Tuple[ConanPackageId, ConanPackagePath]:
        pkg_id = ""
        if conan_options is None:
            conan_options = {}
        if conan_settings is None:
            conan_settings = {}
        options_list = create_key_value_pair_list(conan_options)
        settings_list = create_key_value_pair_list(conan_settings)
        if not quiet:
            install_message = f"Installing '<b>{str(conan_ref)}</b>' with profile: {profile}, " \
                f"settings: {str(settings_list)}, " \
                f"options: {str(options_list)} and update={update}\n"
            Logger().info(install_message)
        from conan.cli.printers.graph import print_graph_basic, print_graph_packages

        try:
            # Basic collaborators, remotes, lockfile, profiles
            remotes = self._conan.remotes.list(None)
            profiles = [profile] if profile else []
            profile_host = self._conan.profiles.get_profile(profiles, 
                                        settings=settings_list, options=options_list)
            requires = [conan_ref]
            deps_graph = self._conan.graph.load_graph_requires(requires, None, 
                            profile_host, profile_host, None, remotes, update)
            print_graph_basic(deps_graph)
            deps_graph.report_graph_error()
            self._conan.graph.analyze_binaries(deps_graph, build_mode=None, remotes=remotes, update=update,
                                               lockfile=None)
            print_graph_packages(deps_graph)
            self._conan.install.install_binaries(deps_graph=deps_graph, remotes=remotes)
            # Currently unused
            self._conan.install.install_consumer(deps_graph=deps_graph, generators=generators, output_folder=None,
                                            source_folder=gettempdir())
            info = None
            for node in deps_graph.nodes:
                if node.ref == conan_ref:
                    info = node
                    break
            if info is None:
                raise ConanException(
                    "Can't read information of installed recipe from graph.")
            pkg_id = info.package_id
            Logger().info(
                f"Installation of '<b>{str(conan_ref)}</b>' finished")
            # Update cache with this package
            self.info_cache.update_local_package_path(
                conan_ref, self.get_package_folder(conan_ref, pkg_id))
            return (pkg_id, self.get_package_folder(conan_ref, pkg_id))
        except ConanException as error:
            Logger().error(
                f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return (pkg_id, Path(INVALID_PATH))

    def get_options_with_default_values(self, 
                    conan_ref: ConanRef) -> Tuple[ConanAvailableOptions, ConanOptions]:
        # this calls external code of the recipe
        default_options = {}
        available_options = {}
        try:
            path = self.get_conanfile_path(conan_ref)
            from conan.internal.conan_app import ConanApp
            app = ConanApp(self._conan.cache_folder)
            conanfile = app.loader.load_conanfile(path, conan_ref)
            default_options = conanfile.default_options
            available_options = conanfile.options
            default_options = self._resolve_default_options(default_options)
        except Exception as e:  # silent error - if we have no options don't spam the user
            Logger().debug(
                f"Error while getting default options for {str(conan_ref)}: {str(e)}")
        return available_options, default_options

    ### Local References and Packages ###

    def get_conan_buildinfo(self, conan_ref: ConanRef, conan_settings: ConanSettings,
                            conan_options: Optional[ConanOptions]=None) -> str:
        """ TODO: Currently there is no equivalent to txt generator from ConanV1 """
        raise NotImplementedError
    
    def get_editables_package_path(self, conan_ref: ConanRef) -> Path:
        """ Get package path of an editable reference. """
        editables_dict = self._conan.local.editable_list()
        return Path(editables_dict.get(conan_ref, {}).get("path", INVALID_PATH))

    def get_editable_references(self) -> List[str]:
        """ Get all local editable references. """
        editables_dict = self._conan.local.editable_list()
        return list(map(str, editables_dict.keys()))

    def remove_reference(self, conan_ref: ConanRef, pkg_id: str = ""):
        if pkg_id:
            conan_pkg_ref = ConanPkgRef.loads(str(conan_ref) + ":" + pkg_id)
            self._conan.remove.package(
                conan_pkg_ref, remote=None)  # type: ignore
        else:
            self._conan.remove.recipe(conan_ref, remote=None)  # type: ignore

    def get_all_local_refs(self) -> List[ConanRef]:
        return self._client_cache.all_refs()  # type: ignore

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
        if not conan_ref.revision:
            try:
                conan_ref_latest: ConanRef = self._conan.list.latest_recipe_revision(
                    conan_ref)  # type: ignore
            except Exception as e:
                Logger().error(
                    f"Error while getting latest recipe for {str(conan_ref)}: {str(e)}")
                return result
            if not conan_ref_latest:
                return result
        else:
            conan_ref_latest = conan_ref
        try:  # errors with invalid pkg
            refs = self._conan.list.packages_configurations(conan_ref_latest)
        except Exception as e:
            Logger().error(
                f"Error while getting packages for recipe {str(conan_ref)}: {str(e)}")
            return result
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
                search_results: List["ConanRef"] = self._conan.search.recipes(
                    query, remote=remote)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []

        search_results = list(set(search_results))  # make unique
        search_results.sort()
        return search_results

    def search_recipe_all_versions_in_remotes(self, conan_ref: ConanRef) -> List[ConanRef]:
        search_results = []
        local_results = []
        try:
            # no query possible with pattern
            search_results: List = self.search_recipes_in_remotes(f"{conan_ref.name}/*@*/*",
                                                                  remote_name="all")
        except Exception as e:
            Logger().warning(str(e))
        # TODO: There is no extra remote=None anymore... What to do with this?
        # try:
        #     if SEARCH_APP_VERSIONS_IN_LOCAL_CACHE:
        #         local_results: List = self.search_recipes_in_remotes(f"{conan_ref.name}/*@*/*",
        #                                                          remote_name=None)
        # except Exception as e:
        #     Logger().warning(str(e))
        #     return []

        res_list: List[ConanRef] = search_results
        # for res in search_results + local_results:
        #     for item in res.get("items", []):
        #         res_list.append(ConanRef.loads(item.get("recipe", {}).get("id", "")))
        # res_list = list(set(res_list))  # make unique
        # res_list.sort()
        # update cache
        self.info_cache.update_remote_package_list(res_list)
        return res_list

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
            search_results = self._conan.list.select(
                pattern, remote=remote_obj, package_query=query)
            if search_results:
                latest_rev = self._conan.list.latest_recipe_revision(
                    conan_ref, remote_obj)
                if latest_rev:
                    found_pkgs_dict = search_results.recipes.get(str(conan_ref), {}).get(
                        "revisions", {}).get(latest_rev.revision, {}).get("packages", {})
                    for id, info in found_pkgs_dict.items():
                        found_pkgs.append(ConanPkg(id=id, options=info.get("info", {}).get("options", {}),
                                                   settings=info.get("info", {}).get(
                                                       "settings", {}),
                                                   requires=[], outdated=False))
            Logger().debug(str(found_pkgs))
        except ConanException:  # no problem, next
            return []
        return found_pkgs
