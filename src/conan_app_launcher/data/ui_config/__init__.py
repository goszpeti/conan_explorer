
from conans.model.ref import ConanFileReference
from conan_app_launcher import INVALID_CONAN_REF, PathLike
from typing import Union
from abc import ABC, abstractmethod

from typing import Dict, List, TYPE_CHECKING, Optional
from dataclasses import dataclass, field

UI_CONFIG_JSON_TYPE = "json"

# classes representing the ui config (Data Transfer Objects)

@dataclass
class AppLinkConfig():
    name: str = "New App"
    conan_ref: ConanFileReference = ConanFileReference.loads(INVALID_CONAN_REF)
    executable: str = ""
    icon: str = ""
    is_console_application: bool = False
    args: str = ""
    conan_options: Dict[str, str] = field(default_factory=dict)


@dataclass
class TabConfig():
    name: str = "New Tab"
    apps: List[AppLinkConfig] = field(default_factory=list)


def UiConfigFactory(type: str, source: PathLike) -> "UiConfigInterface":

    if type == UI_CONFIG_JSON_TYPE:
        from .json_file import JsonUiConfig
        implementation = JsonUiConfig(source)
    else:
        raise NotImplementedError
    return implementation

# Interface for Settings to implement

class UiConfigInterface(ABC):
    """
    Abstract Class to implement settings mechanisms.
    Source artefact should be passed by constructor an and is not changeable.
    """

    @abstractmethod
    def load(self) -> List[TabConfig]:
        raise NotImplementedError

    @abstractmethod
    def save(self, tabs: List[TabConfig]):
        raise NotImplementedError
