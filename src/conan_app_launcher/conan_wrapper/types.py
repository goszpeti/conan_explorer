from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from abc import ABC, abstractmethod
from conan_app_launcher import conan_version

if TYPE_CHECKING:
    from typing import TypedDict,  TypeAlias
    from conan_app_launcher.conan_wrapper.conan_cache import ConanInfoCache
    from conans.client.conan_api import ClientCache
else:
    try:
        from typing import TypedDict, Protocol, TypeAlias
    except ImportError:
        from typing_extensions import TypedDict, Protocol, TypeAlias

if conan_version.startswith("1"):
    from conans.model.ref import ConanFileReference, PackageReference
    from conans.paths.package_layouts.package_editable_layout import PackageEditableLayout
    from conans.client.cache.remote_registry import Remote
    try:
        from conans.util.windows import CONAN_REAL_PATH, path_shortener
    except Exception:
        pass
elif conan_version.startswith("2"):
    from conans.model.recipe_ref import RecipeReference as ConanFileReference  # type: ignore
    from conans.model.package_ref import PkgReference as PackageReference  # type: ignore
    from conans.client.cache.remote_registry import Remote
else:
    raise RuntimeError("Can't recognize Conan version")


ConanRef: TypeAlias = ConanFileReference
PkgRef: TypeAlias = PackageReference


class ConanUnifiedApi(ABC):
    """ 
    API abstraction to provide compatiblity betwwen ConanV1 and V2 APIs. 
    Functions, which are not yet implemented in ConanV2 are commented out, so static type checkers can work.
    """

    def __init__(self) -> None:
        # no direct Conan API access!
        self.client_cache: "ClientCache"  # TODO: Abstract this
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

    # def get_remote_user_info(self, remote_name: str) -> Tuple[str, bool]:  # user_name, authenticated
    #     """ Get username and authenticated info for a remote. """
    #     raise NotImplementedError

    # def get_short_path_root(self) -> Path:
    #     """ Return short path root for Windows. Sadly there is no built-in way to do  """
    # raise NotImplementedError

    def get_package_folder(self, conan_ref: ConanRef, package_id: str) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        raise NotImplementedError

    def get_export_folder(self, conan_ref: ConanRef) -> Path:
        """ Get the export folder form a reference """
        raise NotImplementedError

    # def get_conanfile_path(self, conan_ref: ConanRef) -> Path:
    #     raise NotImplementedError


### Install related methods ###

    # def install_reference(self, conan_ref: ConanRef, conan_settings:  Dict[str, str] = {},
    #                       conan_options: Dict[str, str] = {}, update=True) -> Tuple[str, Path]:
    #     """
    #     Try to install a conan reference (without id) with the provided extra information.
    #     Uses plain conan install (No auto determination of best matching package)
    #     Returns the actual pkg_id and the package path.
    #     """
    #     raise NotImplementedError

    # def install_package(self, conan_ref: ConanRef, package: ConanPkg, update=True) -> bool:
    #     """
    #     Try to install a conan package (id) with the provided extra information.
    #     Returns True, if installation was succesfull.
    #     """
    #     raise NotImplementedError

    # def install_best_matching_package(self, conan_ref: ConanRef,
    #                                   conan_options: Dict[str, str] = {}, update=False) -> Tuple[str, Path]:
    #     raise NotImplementedError


### Local References and Packages ###

    # def get_best_matching_package_path(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}) -> Tuple[str, Path]:
    #     raise NotImplementedError

    def get_all_local_refs(self) -> List[ConanRef]:
        """ Returns all locally installed conan references """
        return self.client_cache.all_refs()

    def get_local_pkgs_from_ref(self, conan_ref: ConanRef) -> List["ConanPkg"]:
        """ Returns all installed pkg ids for a reference. """
        raise NotImplementedError

    def get_local_pkg_from_id(self, pkg_ref: PackageReference) -> "ConanPkg":
        """ Returns an installed pkg from reference and id """
        raise NotImplementedError

    def get_local_pkg_from_path(self, conan_ref: ConanRef, path: Path):
        """ For reverse lookup - give info from path """
        raise NotImplementedError

    # def find_best_local_package(self, conan_ref: ConanRef, input_options: Dict[str, str] = {}) -> ConanPkg:
    #     """ Find a package in the local cache """
    #     raise NotImplementedError

### Remote References and Packages ###

    def search_query_in_remotes(self, query: str, remote_name="all") -> List["ConanRef"]:
        """ Search in all remotes for a specific query. Returns a list if unqiue and ordered ConanRefs. """
        raise NotImplementedError

    # def search_recipe_alternatives_in_remotes(self, conan_ref: ConanRef) -> List[ConanRef]:
    #     """ Search in all remotes for all versions of a conan ref """
    #     raise NotImplementedError

    # def get_packages_in_remote(self, conan_ref: ConanRef, remote: Optional[str], query=None) -> List[ConanPkg]:
    #     raise NotImplementedError

    # def get_remote_pkg_from_id(self, pkg_ref: PackageReference) -> "ConanPkg":
    #     """ Returns a remote pkg from reference and id """
    #     raise NotImplementedError

    # def get_matching_package_in_remotes(self, conan_ref: ConanRef, conan_options: Dict[str, str] = {}) -> List[ConanPkg]:
    #     """ Find a package with options in the remotes """
    #     raise NotImplementedError

    # def find_best_matching_packages(self, conan_ref: ConanRef, input_options: Dict[str, str] = {},
    #                                 remote: Optional[str] = None) -> List[ConanPkg]:
    #     """
    #     This method tries to find the best matching packages either locally or in a remote,
    #     based on the users machine and the supplied options.
    #     """
    #     raise NotImplementedError

### Helper methods ###

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
    def generate_canonical_ref(conan_ref: ConanRef) -> str:
        if conan_ref.user is None and conan_ref.channel is None:
            return str(conan_ref) + "@_/_"
        return str(conan_ref)

    @staticmethod
    def build_conan_profile_name_alias(settings: Dict[str, str]) -> str:
        """ Build a human readable pseduo profile name, like Windows_x64_vs16_v142_release """
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


def create_key_value_pair_list(input_dict: Dict[str, str]) -> List[str]:
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
