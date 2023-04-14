from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union
from conan_app_launcher import conan_version

if TYPE_CHECKING:
    from typing import TypedDict,  TypeAlias
    from conan_app_launcher.conan_wrapper.conan_cache import ConanInfoCache
else:
    try:
        from typing import TypedDict, Protocol, TypeAlias
    except ImportError:
        from typing_extensions import TypedDict, Protocol, TypeAlias
if conan_version.startswith("1"):
    from conans.model.ref import ConanFileReference, PackageReference
    from conans.paths.package_layouts.package_editable_layout import PackageEditableLayout
    try:
        from conans.util.windows import CONAN_REAL_PATH
    except Exception:
        pass
elif conan_version.startswith("2"):
    from conans.model.recipe_ref import RecipeReference as ConanFileReference  # type: ignore
    from conans.model.package_ref import PkgReference as PackageReference  # type: ignore
else:
    raise RuntimeError("Can't recognize Conan version")

from conans.client.cache.remote_registry import Remote
from conans.errors import ConanException

ConanRef: TypeAlias = ConanFileReference
ConanOptions: TypeAlias = Dict[str, Any]
ConanAvailableOptions: TypeAlias = Dict[str, Union[List[Any], Literal["ANY"]]]
ConanSettings: TypeAlias = Dict[str, str]
ConanPackageId: TypeAlias = str
ConanPackagePath: TypeAlias = Path

class ConanPkgRef(PackageReference): # type: ignore
    """ Compatibility class for changed package_id attribute """
    @property
    def id(self):
        if conan_version.startswith("1"):
            return self.id
        elif conan_version.startswith("2"):
            return self.package_id
    
class ConanPkg(TypedDict, total=False):
    """ Dummy class to type conan returned package dicts """

    id: str
    options: Dict[str, Any]
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


def create_key_value_pair_list(input_dict: Dict[str, Any]) -> List[str]:
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
