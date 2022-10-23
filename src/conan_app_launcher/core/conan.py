from pathlib import Path
from platform import platform
from typing import TYPE_CHECKING, Dict, List, Set
import conans

from conan_app_launcher.app.logger import Logger
if conans.__version__.startswith("1"):
    from conans.model.ref import ConanFileReference, PackageReference
    from conans.paths.package_layouts.package_editable_layout import \
        PackageEditableLayout

else:
    from conans.model.recipe_ref import RecipeReference as ConanFileReference
    from conans.model.package_ref import RecipeReference as PackageReference

try:
    from conans.util.windows import CONAN_REAL_PATH, path_shortener
except Exception:
    pass

if TYPE_CHECKING:
    from typing import TypedDict
else:
    try:
        from typing import TypedDict
    except ImportError:
        from typing_extensions import TypedDict

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


class ConanCleanup():

    def __init__(self, conan_api: "ConanApi") -> None:
        self._conan_api = conan_api
        self.orphaned_references: Set[str] = set()
        self.orphaned_packages: Set[str] = set()

    def get_cleanup_cache_paths(self) -> Set[str]:
        """ Get a list of orphaned short path and cache folders """
        # Blessed are the users Microsoft products!
        if platform.system() != "Windows":
            return set()
        self.find_orphaned_references()
        self.find_orphaned_packages()
        return self.orphaned_references.union(self.orphaned_packages)

    def find_orphaned_references(self):
        del_list = []
        for ref in self._conan_api.client_cache.all_refs():
            ref_cache = self._conan_api.client_cache.package_layout(ref)
            try:
                package_ids = ref_cache.package_ids()
            except Exception:
                package_ids = ref_cache.packages_ids()  # type: ignore - old API of Conan
            for pkg_id in package_ids:
                short_path_dir = self._conan_api.get_package_folder(ref, pkg_id)
                pkg_id_dir = None
                if not isinstance(ref_cache, PackageEditableLayout):
                    pkg_id_dir = Path(ref_cache.packages()) / pkg_id
                if not short_path_dir.exists():
                    Logger().debug(f"Can't find {str(short_path_dir)} for {str(ref)}")
                    if pkg_id_dir:
                        del_list.append(str(pkg_id_dir))
        self.orphaned_references = set(del_list)

    def find_orphaned_packages(self):
        """ Reverse search for orphaned packages on windows short paths """
        del_list = []
        short_path_folders = [f for f in self._conan_api.get_short_path_root().iterdir() if f.is_dir()]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if rp_file.is_file():
                with open(str(rp_file)) as fp:
                    real_path = fp.read()
                try:
                    if not Path(real_path).is_dir():
                        Logger().debug(f"Can't find {real_path} for {str(short_path)}")
                        del_list.append(str(short_path))
                except Exception:
                    Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
        self.orphaned_packages = set(del_list)


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
