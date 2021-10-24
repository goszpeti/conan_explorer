import platform
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

from conans.client.conan_api import ClientCache, ConanAPIV1, UserIO
from conans.model.ref import ConanFileReference, PackageReference
from conans.util.windows import path_shortener

try:
    from conans.util.windows import (CONAN_REAL_PATH, path_shortener,
                                     rm_conandir)
except:
    pass

import conan_app_launcher as this
from conan_app_launcher.base import Logger


class ConanPkg(TypedDict):
    """ Dummy class to type conan package dicts """

    id: str
    options: Dict[str, str]
    settings: Dict[str, str]
    requires: List  # ?
    outdated: bool


class ConanApi():
    """ Wrapper around ConanAPIV1 """

    def __init__(self):
        self.conan: ConanAPIV1 = None
        self.cache: ClientCache = None
        self.user_io: UserIO = None
        self._short_path_root = Path("NULL")
        self.init_api()


    def init_api(self):
        """ Instantiate the api. In some cases it needs to be instatiated anew. """
        self.conan, _, _ = ConanAPIV1.factory()
        self.conan.create_app()
        self.user_io = self.conan.user_io
        self.cache = self.conan.app.cache

    def get_all_local_refs(self) -> List[ConanFileReference]:
        """ Returns all locally installed conan references """
        return self.cache.all_refs()

    def get_local_pkgs_from_ref(self, conan_ref: ConanFileReference) -> List[ConanPkg]:
        """ Returns all installed pkg ids for a reference. """
        response = self.conan.search_packages(str(conan_ref))
        result = response.get("results", [{}])[0].get("items", [{}])[0].get("packages", [{}])
        return result

    def get_short_path_root(self) -> Path:
        """ Return short path root for Windows. Sadly there is no built-in way to do this. """
        # only need to get once
        if self._short_path_root.exists() or platform.system() != "Windows":
            return self._short_path_root

        gen_short_path = Path(path_shortener(tempfile.mkdtemp(), True))
        short_path_root = gen_short_path.parents[1]
        shutil.rmtree(gen_short_path.parent, ignore_errors=True)
        return short_path_root

    def get_cleanup_cache_paths(self) -> List[str]:
        """ Get a list of orphaned short path and cache folders """
        # Blessed are the users Microsoft products!
        if not platform.system() == "Windows":
            return []
        del_list = []
        # search for orphaned refs
        for ref in self.cache.all_refs():
            ref_cache = self.cache.package_layout(ref)
            try:
                package_ids = ref_cache.package_ids()
            except:
                package_ids = ref_cache.packages_ids() # old api
            for pkg_id in package_ids:
                short_path_dir = self.get_package_folder(ref, {"id": pkg_id})
                pkg_id_dir = Path(ref_cache.packages()) / pkg_id
                if not short_path_dir.exists():
                    Logger().debug(f"Can't find {str(short_path_dir)} for {str(ref)}")
                    del_list.append(str(pkg_id_dir))

        # reverse search for orphaned packages on windows short paths
        short_path_folders = [f for f in self.get_short_path_root().iterdir() if f.is_dir()]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if rp_file.is_file():
                with open(str(rp_file)) as fp:
                    real_path = fp.read()
                try:
                    if not Path(real_path).is_dir():
                        Logger().debug(f"Can't find {real_path} for {str(short_path)}")
                        del_list.append(str(short_path))
                except:
                    Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")

        return del_list

    def get_path_or_install(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {}) -> Path:
        """ Return the package folder of a conan reference and install it, if it is not available """

        package = self.find_best_local_package(conan_ref, input_options)
        if package:
            return self.get_package_folder(conan_ref, package)

        packages: List[ConanPkg] = self.search_package_in_remotes(conan_ref, input_options)
        if not packages:
            return Path("NULL")

        if self.install_package(conan_ref, packages[0]):
            package = self.find_best_local_package(conan_ref, input_options)
            return self.get_package_folder(conan_ref, package)
        return Path("NULL")

    def search_query_in_remotes(self, query: str) -> List[ConanFileReference]:
        """ Search in all remotes for a specific query. """
        res_list = []
        try:
            # no query possible with pattern
            search_results = self.conan.search_recipes(query, remote_name="all").get("results", None)
        except Exception:
            return []

        for res in search_results:
            for item in res.get("items", []):
                res_list.append(ConanFileReference.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        return res_list

    def search_recipe_in_remotes(self, conan_ref: ConanFileReference) -> List[ConanFileReference]:
        """ Search in all remotes for all versions of a conan ref """
        res_list = []
        try:
            # no query possible with pattern
            search_results = self.conan.search_recipes(f"{conan_ref.name}/*@*/*",
                                                    remote_name="all").get("results", None)
            if this.SEARCH_APP_VERSIONS_IN_LOCAL_CACHE:
                local_results = self.conan.search_recipes(f"{conan_ref.name}/*@*/*",
                                                        remote_name=None).get("results", None)
        except Exception:
            return []
        search_results = search_results + local_results
        for res in search_results:
            for item in res.get("items", []):
                res_list.append(ConanFileReference.loads(item.get("recipe", {}).get("id", "")))
        res_list = list(set(res_list))  # make unique
        res_list.sort()
        return res_list

    def search_package_in_remotes(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {}) -> List[ConanPkg]:
        """ Find a package with options in the remotes """
        remotes = self.cache.registry.load_remotes()
        for remote in remotes.items():
            if not isinstance(remote, str) and len(remote) > 0:  # only check for len, can be an object or a list
                remote = remote[0]  # for old apis
            packages = self.find_best_matching_packages(conan_ref, input_options, remote)
            if packages:
                return packages
        Logger().warning(f"Can't find a matching package '{str(conan_ref)}' in the remotes")
        return []

    def find_best_local_package(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {}) -> Optional[ConanPkg]:
        """ Find a package in the local cache """
        packages = self.find_best_matching_packages(conan_ref, input_options)
        # TODO what to if multiple ones exits? - for now simply take the first entry
        if packages:
            return packages[0]
        return None

    def get_package_folder(self, conan_ref: ConanFileReference, package: Optional[ConanPkg]) -> Path:
        """ Get the fully resolved package path from the reference and the specific package (id) """
        try:
            layout = self.cache.package_layout(conan_ref)
            return Path(layout.package(PackageReference(conan_ref, package["id"])))
        except Exception:  # gotta catch 'em all!
            return Path("NULL")

    def get_export_folder(self, conan_ref: ConanFileReference) -> Path:
        """ Get the export folder form a reference """
        layout = self.cache.package_layout(conan_ref)
        if layout:
            return Path(layout.export())
        return Path("NULL")

    def install_package(self, conan_ref: ConanFileReference, package: ConanPkg) -> bool:
        """
        Try to install a conan package while guessing the mnost suitable package
        for the current platform.
        """
        package_id = package["id"]
        options_list = _create_key_value_pair_list(package["options"])
        settings_list = _create_key_value_pair_list(package["settings"])
        Logger().info(
            f"Installing '{str(conan_ref)}':{package_id} with settings: {str(settings_list)}, options: {str(options_list)}")
        try:
            self.conan.install_reference(conan_ref, update=True,
                                         settings=settings_list, options=options_list)
            return True
        except BaseException as error:
            Logger().error(f"Can't install package '{str(conan_ref)}': {str(error)}")
            return False

    def find_best_matching_packages(self, conan_ref: ConanFileReference, input_options: Dict[str, str] = {},
                                    remote: str = None) -> List[ConanPkg]:
        """
        This method tries to find the best matching packages either locally or in a remote, 
        based on the users machine and the supplied options.
        """
        # skip search on default invalid recipe
        if str(conan_ref) == this.INVALID_CONAN_REF:
            return []

        found_pkgs: List[ConanPkg] = []
        default_settings: Dict[str, str] = dict(self.cache.default_profile.settings)
        try:
            query = f"(arch=None OR arch={default_settings.get('arch')})" \
                    f" AND (arch_build=None OR arch_build={default_settings.get('arch_build')})" \
                    f" AND (os=None OR os={default_settings.get('os')})"\
                    f" AND (os_build=None OR os_build={default_settings.get('os_build')})"
            search_results = self.conan.search_packages(str(conan_ref), query=query,
                                                        remote_name=remote).get("results", None)
            found_pkgs = search_results[0].get("items")[0].get("packages")
            Logger().debug(str(found_pkgs))
        except Exception:  # no problem, next
            return []

        # remove debug releases
        no_debug_pkgs = list(filter(lambda pkg: pkg["settings"].get(
            "build_type", "").lower() != "debug", found_pkgs))
        # check, if a package remained and only then take the result
        if no_debug_pkgs:
            found_pkgs = no_debug_pkgs

        # filter the found packages by the user options
        if input_options:
            found_pkgs = list(filter(lambda pkg: input_options.items() <=
                                     pkg["options"].items(), found_pkgs))
            if not found_pkgs:
                Logger().warning(
                    f"Can't find a matching package '{str(conan_ref)}' for options {str(input_options)}")
                return found_pkgs
        # get a set of existing options and reduce default options with them
        min_opts_set = set(map(lambda pkg: frozenset(tuple(pkg["options"].keys())), found_pkgs))
        min_opts_list = frozenset()
        if min_opts_set:
            min_opts_list = min_opts_set.pop()

        # TODO this calls external code of the recipe - try catch?
        default_options = self._resolve_default_options(
            self.conan.inspect(str(conan_ref), attributes=["default_options"]).get("default_options", {}))

        if default_options:
            default_options = dict(filter(lambda opt: opt[0] in min_opts_list, default_options.items()))
            # patch user input into default options to combine the two
            default_options.update(input_options)
            # convert vals to string
            default_str_options: Dict[str, str] = dict([key, str(value)]
                                                       for key, value in default_options.items())
            if len(found_pkgs) > 1:
                comb_opts_pkgs = list(filter(lambda pkg: default_str_options.items() <=
                                         pkg["options"].items(), found_pkgs))
                if comb_opts_pkgs:
                    found_pkgs = comb_opts_pkgs


        # now we have all matching packages, but with potentially different compilers
        # reduce with default settings
        if len(found_pkgs) > 1:
            same_comp_pkgs = list(filter(lambda pkg: default_settings.get("compiler", "") ==
                                         pkg["settings"].get("compiler", ""), found_pkgs))
            if same_comp_pkgs:
                found_pkgs = same_comp_pkgs

            same_comp_version_pkgs = list(filter(lambda pkg: default_settings.get("compiler.version", "") ==
                                                 pkg["settings"].get("compiler.version", ""), found_pkgs))
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

    @classmethod
    def build_conan_profile_name_alias(cls, settings: Dict[str, str]) -> str:
        """ Build a  human readable pseduo profile name, like Windows_x64_vs16_v142_release """
        if not settings:
            return "default"
        name = settings.get("os", "")
        arch = settings.get("arch", "")
        if arch:
            if arch == "x86_64":
                arch = "x64"
            name += "_" + arch.lower()
        comp = settings.get("compiler", "")
        if comp:
            if comp == "Visual Studio":
                comp = "vs"
            name += "_" + comp.lower()
        comp_ver = settings.get("compiler.version", "")
        if comp_ver:
            name += comp_ver
        comp_toolset = settings.get("compiler.toolset", "")
        if comp_toolset:
            name += "_" + comp_toolset.lower()
        bt = settings.get("build_type", "")
        if bt:
            name += "_" + bt.lower()
        return name

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
        if "any" in value.lower():
            continue
        res_list.append(name + "=" + value)
    return res_list
