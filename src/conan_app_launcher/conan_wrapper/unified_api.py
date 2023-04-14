from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
from abc import ABC
from conan_app_launcher import INVALID_PATH
from conan_app_launcher.app.logger import Logger
from .types import ConanAvailableOptions, ConanOptions, ConanPackageId, ConanPackagePath, ConanPkg, ConanRef, ConanPkgRef, ConanSettings, Remote

if TYPE_CHECKING:
    from conan_app_launcher.conan_wrapper.conan_cache import ConanInfoCache


class ConanUnifiedApi(ABC):
    """ 
    API abstraction to provide compatiblity betwwen ConanV1 and V2 APIs. 
    Functions, which are not yet implemented in ConanV2 are commented out, so static type checkers still work.
    High level functions, which use only other ConanUnifiedApi functions are implemented here.
    """

    def __init__(self) -> None:
        # no direct Conan API access!
        self.info_cache: "ConanInfoCache"
        super().__init__()

    def init_api(self):
        """ Instantiate the internal Conan api. In some cases it needs to be instatiated anew. """
        raise NotImplementedError

### General commands ###

    def remove_locks(self):
        """ Remove local cache locks (Currently for V1 only) """
        raise NotImplementedError

    def get_remotes(self, include_disabled=False) -> List[Remote]:
        """ Return a list of all remotes. """
        raise NotImplementedError

    def get_profiles(self) -> List[str]:
        """ Return a list of all profiles """
        raise NotImplementedError

    def get_profile_settings(self, profile_name: str) -> ConanSettings:
        """ Return a dict of settings for a profile """
        raise NotImplementedError

    def get_profiles_with_settings(self) -> Dict[str, ConanSettings]:
        """ Return a list of all profiles and the corresponding settings """
        profiles_dict = {}
        for profile in self.get_profiles():
            profiles_dict[profile] = self.get_profile_settings(profile)
        return profiles_dict

    # def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:  # user_name, authenticated
    #     """ Get username and authenticated info for a remote. """
    #     raise NotImplementedError

    # def get_short_path_root(self) -> Path:
    #     """ Return short path root for Windows. Sadly there is no built-in way to do  """
    # raise NotImplementedError

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> ConanPackagePath:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        raise NotImplementedError

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        """ Get the export folder form a reference """
        raise NotImplementedError

    def get_conanfile_path(self, conan_ref: ConanRef) -> Path:
        """ Get local conanfile path. If it is not localy available, download it."""
        raise NotImplementedError


### Install related methods ###


    def install_reference(self, conan_ref: ConanRef, conan_settings:  ConanSettings = {},
                          conan_options: ConanOptions = {}, update=True) -> Tuple[ConanPackageId, ConanPackagePath]:
        """
        Try to install a conan reference (without id) with the provided extra information.
        Uses plain conan install (No auto determination of best matching package)
        Returns the actual pkg_id and the package path.
        """
        raise NotImplementedError

    def install_package(self, conan_ref: ConanRef, package: ConanPkg, update=True) -> Tuple[ConanPackageId, ConanPackagePath]:
        """
        Try to install a conan package (id) with the provided extra information.
        Returns the installed id and a valid package path, if installation was succesfull.
        WARNING: The installed id can differ from the requested one, because there is no built-in way in conan to install a specific package id!
        """
        from conans.errors import ConanException
        package_id = package.get("id", "")
        options = package.get("options", {})
        settings = package.get("settings", {})
        Logger().info(
            f"Installing '<b>{str(conan_ref)}</b>':{package_id} with settings: {str(settings)}, "
            f"options: {str(options)} and update={update}\n")
        try:
            installed_id, package_path = self.install_reference(
                conan_ref, update=update, conan_settings=settings, conan_options=options)
            Logger().info(f"Installation of '<b>{str(conan_ref)}</b>' finished")
            if installed_id != package_id:
                Logger().warning("Installed {installed_id} instead of selected {package_id}."
                                 "This can happen, if there transitive settings changed in comparison to the build time.")
            return installed_id, package_path
        except ConanException as e:
            Logger().error(f"Can't install package '<b>{str(conan_ref)}</b>': {str(e)}")
            return "", Path(INVALID_PATH)

    def get_path_or_auto_install(self, conan_ref: ConanRef, conan_options: ConanOptions = {}, 
                                 update=False) -> Tuple[ConanPackageId, ConanPackagePath]:
        """ Return the pkg_id and package folder of a conan reference 
        and auto-install it with the best matching package, if it is not available """
        if not update:
            pkg_id, path = self.get_best_matching_local_package_path(conan_ref, conan_options)
            if pkg_id:
                return pkg_id, path
            Logger().info(
                f"'<b>{conan_ref}</b>' with options {repr(conan_options)} is not installed. Searching for packages to install...")

        pkg_id, path = self.install_best_matching_package(conan_ref, conan_options, update=update)
        return pkg_id, path

    def install_best_matching_package(self, conan_ref: ConanRef,
                                      conan_options: ConanOptions = {}, update=False) -> Tuple[ConanPackageId, ConanPackagePath]:
        packages: List[ConanPkg] = self.find_best_matching_package_in_remotes(conan_ref, conan_options)
        if not packages:
            self.info_cache.invalidate_remote_package(conan_ref)
            return ("", Path(INVALID_PATH))
        pkg_id, package_path = self.install_package(conan_ref, packages[0], update)
        if package_path.exists():
            return pkg_id, package_path
        return "", Path(INVALID_PATH)

    def get_options_with_default_values(self, conan_ref: ConanRef) -> Tuple[ConanAvailableOptions, ConanOptions]:
        """ Return the available options and their default values as dict."""
        raise NotImplementedError


### Local References and Packages ###


    def find_best_matching_local_package(self, conan_ref: ConanRef, conan_options: ConanOptions = {}) -> ConanPkg:
        """ Find a package in the local cache """
        packages = self.find_best_matching_packages(conan_ref, conan_options, remote_name=None)
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

    def get_best_matching_local_package_path(self, conan_ref: ConanRef,
                                             conan_options: ConanOptions = {}) -> Tuple[ConanPackageId, ConanPackagePath]:
        """ Return the pkg_id and package folder of a conan reference, if it is installed. """
        package = self.find_best_matching_local_package(conan_ref, conan_options)
        if package.get("id", ""):
            return package.get("id", ""), self.get_package_folder(conan_ref, package.get("id", ""))
        return "", Path(INVALID_PATH)

    def get_all_local_refs(self) -> List[ConanRef]:
        """ Returns all locally installed conan references """
        raise NotImplementedError

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List["ConanPkg"]:
        """ Returns all installed pkg ids for a reference. """
        raise NotImplementedError

    def get_local_pkg_from_id(self, pkg_ref: ConanPkgRef) -> "ConanPkg":
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


### Remote References and Packages ###


    def search_recipes_in_remotes(self, query: str, remote_name="all") -> List[ConanRef]:
        """ Search in all remotes for a specific query. Returns a list if unqiue and ordered ConanRefs. """
        raise NotImplementedError

    def search_recipe_all_versions_in_remotes(self, conan_ref: ConanRef) -> List[ConanRef]:
        """ Search in all remotes for all versions of a conan ref """
        raise NotImplementedError

    def get_remote_pkgs_from_ref(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
        """ Return all packages for a reference in a specific remote with an optional query.  """
        raise NotImplementedError

    def get_remote_pkg_from_id(self, pkg_ref: ConanPkgRef) -> ConanPkg:
        """ Returns a remote pkg from reference and id """
        package = None
        for remote in self.get_remotes():
            packages = self.get_remote_pkgs_from_ref(pkg_ref.ref, remote.name)
            for package in packages:
                if package.get("id", "") == pkg_ref.id:
                    return package
        return {"id": ""}

    def find_best_matching_package_in_remotes(self, conan_ref: ConanRef, conan_options: ConanOptions = {}) -> List[ConanPkg]:
        """ Find a package with options in the remotes """
        for remote in self.get_remotes():
            packages = self.find_best_matching_packages(conan_ref, conan_options, remote.name)
            if packages:
                return packages
        Logger().info(
            f"Can't find a package '<b>{str(conan_ref)}</b>' with options {conan_options} in the <b>remotes</b>")
        return []

    def find_best_matching_packages(self, conan_ref: ConanRef, conan_options: ConanOptions = {},
                                    remote_name: Optional[str] = None) -> List[ConanPkg]:
        """
        This method tries to find the best matching packages either locally or in a remote,
        based on the users machine and the supplied options.
        """
        raise NotImplementedError

### Helper methods ###

    @staticmethod
    def _resolve_default_options(default_options_raw: Any) -> ConanOptions:
        """ Default options can be a a dict or name=value as string, or a tuple of it """
        default_options: Dict[str, Any] = {}
        if default_options_raw and isinstance(default_options_raw, str):
            default_option_str = default_options_raw.split("=")
            default_options.update({default_option_str[0]: default_option_str[1]})
        elif default_options_raw and isinstance(default_options_raw, (list, tuple)):
            for default_option in default_options_raw:
                default_option_str = default_option.split("=")
                default_options.update({default_option_str[0]: default_option_str[1]})
        else:
            default_options = default_options_raw
        return default_options

    @staticmethod
    def generate_canonical_ref(conan_ref: ConanRef) -> str:
        """ Creates a full ref from a short ref, e.g. product/1.0.0 -> product/1.0.0@_/_ """
        if conan_ref.user is None and conan_ref.channel is None:
            return str(conan_ref) + "@_/_"
        return str(conan_ref)

    @staticmethod
    def build_conan_profile_name_alias(conan_settings: ConanSettings) -> str:
        """ Build a human readable pseduo profile name, like Windows_x64_vs16_v142_release """
        if not conan_settings:
            return "No Settings"

        os = conan_settings.get("os", "")
        if not os:
            os = conan_settings.get("os_target", "")
            if not os:
                os = conan_settings.get("os_build", "")

        arch = conan_settings.get("arch", "")
        if not arch:
            arch = conan_settings.get("arch_target", "")
            if not arch:
                arch = conan_settings.get("arch_build", "")
        if arch == "x86_64":  # shorten x64
            arch = "x64"

        comp = conan_settings.get("compiler", "")
        if comp == "Visual Studio":
            comp = "vs"
        comp_ver = conan_settings.get("compiler.version", "")
        comp_text = comp.lower() + comp_ver.lower()

        comp_toolset = conan_settings.get("compiler.toolset", "")

        bt = conan_settings.get("build_type", "")

        alias = os
        for item in [arch.lower(), comp_text, comp_toolset.lower(), bt.lower()]:
            if item:
                alias += "_" + item

        return alias
