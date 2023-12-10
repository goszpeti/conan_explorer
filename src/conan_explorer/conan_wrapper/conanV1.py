import os
import platform

from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union
from unittest.mock import patch
from conan_explorer.app.system import delete_path
from conan_explorer.app.typing import SignatureCheckMeta

try:
    from contextlib import chdir
except ImportError:
    from contextlib_chdir import chdir

from .types import (ConanAvailableOptions, ConanOptions, ConanPackageId, ConanPackagePath, 
                    ConanPkg, ConanRef, ConanPkgRef, ConanException, ConanSettings, EditablePkg, 
                    LoggerWriter, Remote, create_key_value_pair_list)
from .unified_api import ConanCommonUnifiedApi

if TYPE_CHECKING:
    from .conan_cache import ConanInfoCache
    from conans.client.conan_api import ClientCache, ConanAPIV1

from conan_explorer import (CONAN_LOG_PREFIX, INVALID_PATH,
                                SEARCH_APP_VERSIONS_IN_LOCAL_CACHE, user_save_path)
from conan_explorer.app.logger import Logger


class ConanApi(ConanCommonUnifiedApi, metaclass=SignatureCheckMeta):
    """ Wrapper around ConanAPIV1 """

    def __init__(self):
        self._conan: "ConanAPIV1"
        self.info_cache: "ConanInfoCache"
        self._client_cache: "ClientCache"
        self._short_path_root = Path("Unknown")

    def init_api(self):
        """ Instantiate the internal Conan api. """
        from conans.client.conan_api import (ConanAPIV1, UserIO)
        from conans.client.output import ConanOutput

        self._fix_editable_file()

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
        # HACK: Removed the  @api_method decorator by getting the original function 
        # from the closure attribute
        self.search_packages = \
                self._conan.search_packages.__closure__[0].cell_contents  # type: ignore
        # don't hang on startup
        try:  # use try-except because of Conan 1.24 envvar errors in tests
            self.remove_locks()
        except Exception as e:
            Logger().debug(str(e))
        from .conan_cache import ConanInfoCache
        self.info_cache = ConanInfoCache(user_save_path, self.get_all_local_refs())
        Logger().debug("Initialized Conan V1 API wrapper")

        return self
    
    def _fix_editable_file(self):
        """ Ensure editables json is valid (Workaround for empty json bug)  
        Must work without using ConanAPIV1, because it can't be called without this
        """
        from conans.client.cache.editable import EDITABLE_PACKAGES_FILE
        from conans.paths import get_conan_user_home # use internal fnc
        try:
            editable_file_path = Path(get_conan_user_home()) / ".conan" / EDITABLE_PACKAGES_FILE
            if not editable_file_path.exists():
                editable_file_path.write_text("{}")
            content = editable_file_path.read_text()
            if not content:
                editable_file_path.write_text("{}")
        except Exception:
            Logger().debug("Reinit editable file package")

    ### General commands ###if 

    def remove_locks(self):
        self._conan.remove_locks()
        Logger().info("Removed Conan cache locks.")

    def get_profiles(self) -> List[str]:
        return self._conan.profile_list()

    def get_profile_settings(self, profile_name: str) -> ConanSettings:
        profile = self._conan.read_profile(profile_name)
        if not profile:
            return {}
        return dict(profile.settings)

    def get_default_settings(self) -> ConanSettings:
        # type: ignore
        default_profile = self._client_cache.default_profile
        if not default_profile:
            return {}
        return dict(default_profile.settings)

    # user_name, autheticated
    def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:
        user_info = {}
        try:
            user_info = self._conan.users_list(remote_name).get("remotes", {})
        except Exception:
            Logger().error(f"Cannot find remote {remote_name} in remote list for fetching user.")
        if len(user_info) < 1:
            return ("", False)
        try:
            return (str(user_info[0].get("user_name", "")),
                    user_info[0].get("authenticated", False))
        except Exception:
            Logger().warning(f"Can't get user info for {remote_name}")
            return ("", False)

    def get_config_file_path(self) -> Path:
        return Path(self._client_cache.conan_conf_path)

    def get_config_entry(self, config_name: str, default_value: Any) -> Any:
        try:
            return self._client_cache.config.get_item(config_name)
        except Exception:
            return default_value

    def get_revisions_enabled(self) -> bool:
        return self._client_cache.config.revisions_enabled

    def get_settings_file_path(self) -> Path:
        return Path(self._client_cache.settings_path)

    def get_profiles_path(self) -> Path:
        return Path(str(self._client_cache.default_profile_path)).parent

    def get_user_home_path(self) -> Path:
        return Path(self._client_cache.cache_folder)

    def get_storage_path(self) -> Path:
        return Path(str(self._client_cache.store))

    def get_editables_file_path(self) -> Path:
        editable_file = Path(self._client_cache.editable_packages._edited_file)
        editable_file.touch()
        return editable_file

    def get_editable_references(self) -> List[ConanRef]:
        try:
            return list(map(ConanRef.loads, self._conan.editable_list().keys()))
        except Exception:
            self._fix_editable_file() # to not crash conan without this
            return []

    def get_editable(self, conan_ref: Union[ConanRef, str]) -> EditablePkg:
        pass
        if isinstance(conan_ref, str):
            conan_ref = ConanRef.loads(conan_ref)
        editable_dict = self._conan.editable_list().get(str(conan_ref), {})
        return EditablePkg(str(conan_ref), editable_dict.get("path", INVALID_PATH),
                           editable_dict.get("output_folder"))

    def get_editables_package_path(self, conan_ref: ConanRef) -> Path:
        pkg_path = Path(INVALID_PATH)
        editable_dict = self._conan.editable_list().get(str(conan_ref), {})
        pkg_path = Path(str(editable_dict.get("path", INVALID_PATH)))
        return pkg_path
    
    def get_editables_output_folder(self, conan_ref: ConanRef) -> Optional[Path]:
        editable_dict = self._conan.editable_list().get(str(conan_ref), {})
        output_folder = editable_dict.get("output_folder")
        if not output_folder:
            return None
        return Path(str(output_folder))

    def add_editable(self, conan_ref: Union[ConanRef, str], path: str, output_folder: str) -> bool:
        try:
            self._conan.editable_add(path, str(conan_ref), None, output_folder, None)
        except Exception as e:
            Logger().error("Error adding editable: " + str(e))
            return False
        return True

    def remove_editable(self, conan_ref: Union[ConanRef, str]) -> bool:
        try:
            self._conan.editable_remove(str(conan_ref))
        except Exception as e:
            Logger().error("Error removing editable: " + str(e))
            return False
        return True

    def get_short_path_root(self) -> Path:
        # only need to get once
        if self._short_path_root.exists() or platform.system() != "Windows":
            return self._short_path_root
        short_home = os.getenv("CONAN_USER_HOME_SHORT")
        if not short_home:
            drive = os.path.splitdrive(
                self._client_cache.cache_folder)[0].upper()
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

    # Remotes

    def get_remotes(self, include_disabled=False) -> List[Remote]:
        remotes = []
        try:
            if include_disabled:
                remotes = self._conan.remote_list()
            else:
                remotes = self._client_cache.registry.load_remotes().values()
        except Exception as e:
            Logger().error(f"Error while reading remotes file: {str(e)}")
        return remotes # type: ignore

    def add_remote(self, remote_name: str, url: str, verify_ssl: bool):
        self._conan.remote_add(remote_name, url, verify_ssl)

    def rename_remote(self, remote_name: str, new_name: str):
        self._conan.remote_rename(remote_name, new_name)

    def remove_remote(self, remote_name: str):
        self._conan.remote_remove(remote_name)

    def disable_remote(self, remote_name: str, disabled: bool):
        self._conan.remote_set_disabled_state(remote_name, disabled)

    def update_remote(self, remote_name: str, url: str, verify_ssl: bool, disabled: bool,
                      index: Optional[int]):
        self.disable_remote(remote_name, disabled)
        self._conan.remote_update(remote_name, url, verify_ssl, index)

    def login_remote(self, remote_name: str, user_name: str, password: str):
        self._conan.authenticate(user_name, password, remote_name)

    ### Install related methods ###

    def install_reference(self, conan_ref: ConanRef, conan_settings: Optional[ConanSettings]=None,
            conan_options: Optional[ConanOptions]=None, profile="", update=True, quiet=False,
            generators: List[str] = []) -> Tuple[ConanPackageId, ConanPackagePath]:
        package_id = ""
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
        profile_names = None
        if profile:
            profile_names = [profile]
        try:
            # Try to redirect custom streams in conanfile, to avoid missing flush method
            devnull = open(os.devnull, 'w')
            # also spoof os.terminal_size(
            spoof_size = os.terminal_size([80,20])
            patched_tersize = patch("os.get_terminal_size")
            with redirect_stdout(devnull), redirect_stderr(devnull):
                mock = patched_tersize.start()
                mock.return_value = spoof_size

                infos = self._conan.install_reference(conan_ref, 
                    settings=settings_list, options=options_list, update=update,
                    profile_names=profile_names, generators=generators)

                patched_tersize.stop()
            if not infos.get("error", True):
                package_id = infos.get("installed", [{}])[0].get(
                                                    "packages", [{}])[0].get("id", "")
            Logger().info(
                f"Installation of '<b>{str(conan_ref)}</b>' finished")
            # Update cache with this package
            package_path = self.get_package_folder(conan_ref, package_id)
            self.info_cache.update_local_package_path(conan_ref, package_path)
            return package_id, package_path
        except ConanException as error:
            Logger().error(
                f"Can't install reference '<b>{str(conan_ref)}</b>': {str(error)}")
            return package_id, Path(INVALID_PATH)

    def get_conan_buildinfo(self, conan_ref: ConanRef, conan_settings: ConanSettings,
                            conan_options: Optional[ConanOptions]=None) -> str:
        # install ref to temp dir and use generator
        temp_path = Path(gettempdir()) / "cal_cuild_info"
        temp_path.mkdir(parents=True, exist_ok=True)
        generated_file = (temp_path / "conanbuildinfo.txt")
        # clean up possible last run
        delete_path(generated_file)

        # use cli here, API cannnot do job easily and we wan to parse the file output
        with chdir(temp_path):
            self.install_reference(conan_ref, conan_settings=conan_settings, 
                                   conan_options=conan_options, generators=["txt"])
        content = ""
        try:
            content = generated_file.read_text()
        except Exception as e:
            Logger().error(
                f"Can't read conanbuildinfo.txt for '<b>{str(conan_ref)}</b>': {str(e)}")
        return content

    def get_options_with_default_values(self, conan_ref: ConanRef) -> Tuple[ConanAvailableOptions, ConanOptions]:
        # this calls external code of the recipe
        default_options = {}
        available_options = {}
        try:
            ref_info = self._conan.info(self.generate_canonical_ref(conan_ref))
            # 0. element is always the conanfile itself
            recipe = ref_info[0].root.dependencies[0].dst.conanfile  # type: ignore
            # type: ignore
            default_options_list = recipe.options.items()
            for option, value in default_options_list:
                default_options.update({option: value})
                # No public API for this :( - seems stable for all versions, in worst case
                # we don't get option defaults
                opts = recipe.options._data[option]._possible_values
                available_options.update({option: opts})
        except Exception as e:
            Logger().debug(
                f"Error while getting default options for {str(conan_ref)}: {str(e)}")
        return available_options, default_options

    # Local References and Packages

    def remove_reference(self, conan_ref: ConanRef, pkg_id: str = ""):
        pkg_ids = [pkg_id] if pkg_id else None
        self._conan.remove(str(conan_ref), packages=pkg_ids, force=True)

    def get_all_local_refs(self) -> List[ConanRef]:
        return self._client_cache.all_refs()  # type: ignore

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List[ConanPkg]:
        result: List[ConanPkg] = []
        response = {}
        try:
            response = self.search_packages(
                self._conan, self.generate_canonical_ref(conan_ref))
        except Exception as error:
            Logger().debug(f"{str(error)}")
            return result
        if not response.get("error", True):
            try:
                result = response.get("results", [{}])[0].get(
                    "items", [{}])[0].get("packages", [{}])
            except Exception:
                Logger().error(
                    f"Received invalid package response format for {str(conan_ref)}")
        return result

    # Remote References and Packages

    def search_recipes_in_remotes(self, query: str, remote_name="all") -> List[ConanRef]:
        res_list: List[ConanRef] = []
        remote_results = []
        try:
            # no query possible with pattern
            remote_results = self._conan.search_recipes(
                query, remote_name=remote_name, case_sensitive=False).get("results", None)
        except Exception as e:
            Logger().error(f"Error while searching for recipe: {str(e)}")
            return []
        if not remote_results:
            return res_list

        for remote_search_res in remote_results:
            res_list += (list(map(lambda item: 
                                ConanRef.loads(item.get("recipe", {}).get("id", "")), 
                                remote_search_res.get("items", []))))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        self.info_cache.update_remote_package_list(res_list)
        return res_list

    def search_recipe_all_versions_in_remotes(self, conan_ref: ConanRef) -> List[ConanRef]:
        remote_results = []
        local_results = []
        try:
            # no query possible with pattern
            remote_results: List = self._conan.search_recipes(
                f"{conan_ref.name}/*@*/*", remote_name="all").get("results", None)
        except Exception as e:
            Logger().warning(str(e))
        try:
            if SEARCH_APP_VERSIONS_IN_LOCAL_CACHE:
                local_results: List = self._conan.search_recipes(
                    f"{conan_ref.name}/*@*/*", remote_name=None).get("results", None)
        except Exception as e:
            Logger().warning(str(e))
            return []

        res_list: List[ConanRef] = []
        for remote_search_res in local_results + remote_results:
            res_list += (list(map(lambda item: 
                                ConanRef.loads(item.get("recipe", {}).get("id", "")), 
                                remote_search_res.get("items", []))))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        # update cache
        self.info_cache.update_remote_package_list(res_list)
        return res_list

    def get_remote_pkgs_from_ref(self, conan_ref: ConanRef, remote: Optional[str], 
                                       query=None) -> List[ConanPkg]:
        found_pkgs: List[ConanPkg] = []
        try:
            search_results = self._conan.search_packages(
                conan_ref.full_str(), query=query, remote_name=remote).get("results", None)
            if search_results:
                found_pkgs = search_results[0].get("items")[0].get("packages")
            Logger().debug(str(found_pkgs))
        except ConanException:  # no problem, next
            return []
        return found_pkgs
