from typing import TYPE_CHECKING, Dict, List

from conan_app_launcher.app.logger import Logger
import conan

try:
    from conans.model.ref import ConanFileReference, PackageReference
    from conans.paths.package_layouts.package_editable_layout import PackageEditableLayout
except:
    from conans.model.recipe_ref import RecipeReference as ConanFileReference  # type: ignore
    from conans.model.package_ref import RecipeReference as PackageReference  # type: ignore

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
