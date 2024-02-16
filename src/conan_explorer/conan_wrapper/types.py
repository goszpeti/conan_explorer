from __future__ import annotations
from dataclasses import dataclass

import os
import pprint

from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from conan_explorer import conan_version

if TYPE_CHECKING:
    from typing import TypedDict, TypeAlias, Literal
else:
    try:
        from typing import Literal, TypedDict, Protocol, TypeAlias
    except ImportError:
        from typing_extensions import Literal, TypedDict, Protocol, TypeAlias


if conan_version.startswith("1"):
    from conans.model.ref import ConanFileReference, PackageReference # type: ignore
    from conans.paths.package_layouts.package_editable_layout import PackageEditableLayout
    try:
        from conans.util.windows import CONAN_REAL_PATH
    except Exception:
        pass
elif conan_version.startswith("2"):
    from conans.model.recipe_ref import RecipeReference as ConanFileRef  # type: ignore
    from conans.model.package_ref import PkgReference  # type: ignore
    class PackageReference(PkgReference): # type: ignore
        """ Compatibility class for changed package_id attribute """
        ref: ConanRef
        
        @property
        def id(self):
            return self.package_id

        @staticmethod
        def loads(text: str) -> ConanPkgRef:
            pkg_ref = PkgReference.loads(text)
            return PackageReference(pkg_ref.ref, pkg_ref.package_id, 
                                    pkg_ref.revision,pkg_ref.timestamp)

    class ConanFileReference(ConanFileRef):
        name: str
        version: str
        user: Optional[str]
        channel: Optional[str]

        @staticmethod
        def loads(text: str, validate=True) -> ConanRef:
            ref: ConanRef = ConanFileRef().loads(text) # type: ignore
            if validate:
                # validate_ref creates an own output stream which can't log to console
                # if it is running as a gui application
                devnull = open(os.devnull, 'w')
                with redirect_stdout(devnull):
                    with redirect_stderr(devnull):
                        ref.validate_ref(allow_uppercase=True)
            return ref
        

else:
    raise RuntimeError("Can't recognize Conan version")


@dataclass
class Remote():
    name: str
    url: str
    verify_ssl: bool
    disabled: bool

from conans.errors import ConanException

ConanRef: TypeAlias = ConanFileReference
ConanPkgRef: TypeAlias = PackageReference
ConanOptions: TypeAlias = Dict[str, Any]
ConanAvailableOptions: TypeAlias = Dict[str, Union[List[Any], Literal["ANY"]]]
ConanSettings: TypeAlias = Dict[str, str]
ConanPackageId: TypeAlias = str
ConanPackagePath: TypeAlias = Path

    
class ConanPkg(TypedDict, total=False):
    """ Dummy class to type conan returned package dicts """

    id: ConanPackageId
    options: ConanOptions
    settings: ConanSettings
    requires: List[Any]
    outdated: bool


@dataclass
class EditablePkg():
    conan_ref: str
    path: str # path to conanfile or folder
    output_folder: Optional[str]

def pretty_print_pkg_info(pkg_info: ConanPkg) -> str:
    return pprint.pformat(pkg_info).translate(
        {ord("{"): None, ord("}"): None, ord("'"): None})


class LoggerWriter:
    """
    Dummy stream to log directly to a logger object, when writing in the stream.
    Used to redirect custom stream from Conan. 
    Adds a prefix to do some custom formatting in the Logger.
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
