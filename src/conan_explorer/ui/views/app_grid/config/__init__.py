
""" Classes representing the ui config (Data Transfer Objects) 
this is a bit overblown for this usecase, but it is worth an experiment """

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

from conan_explorer import INVALID_CONAN_REF, PathLike

UI_CONFIG_JSON_TYPE = "json"

if TYPE_CHECKING:
    from ..model import UiAppLinkModel, UiTabModel


@dataclass
class UiAppLinkConfig():
    name: str = "New App"
    executable: str = ""
    icon: str = ""
    is_console_application: bool = False
    args: str = ""
    conan_options: Dict[str, str] = field(default_factory=dict)
    conan_ref: str = INVALID_CONAN_REF


@dataclass
class UiTabConfig():
    name: str = "New Tab"
    # The Union is a workaround. How to say, that this is the base class?
    apps: List["UiAppLinkConfig | UiAppLinkModel"] = field(default_factory=list)

    def __post_init__(self):
        if not self.apps:
            self.apps.append(UiAppLinkConfig())


@dataclass
class UiAppGridConfig():
    # The Union is a workaround. How to say, that this is the base class?
    tabs: List["UiTabConfig | UiTabModel"] = field(default_factory=list)

    def __post_init__(self):
        if not self.tabs:
            self.tabs.append(UiTabConfig())


@dataclass
class UiConfig():
    app_grid: UiAppGridConfig = field(default_factory=UiAppGridConfig)


def ui_config_factory(type: str, source: PathLike) -> "UiConfigInterface":

    if type == UI_CONFIG_JSON_TYPE:
        from .json_file import JsonUiConfig
        implementation = JsonUiConfig(source)
    else:
        raise NotImplementedError
    return implementation


def get_ui_config_file_ext(type: str) -> str:
    if type == UI_CONFIG_JSON_TYPE:
        from .json_file import JsonUiConfig
        file_ext = JsonUiConfig.get_file_ext()
    else:
        raise NotImplementedError
    return file_ext


class UiConfigInterface():
    """
    Abstract Class to implement ui config mechanism.
    Source artefact should be passed by constructor an and is not changeable.
    """

    @classmethod
    def get_file_ext(cls) -> str:  # enter file extesnion like .yaml
        raise NotImplementedError

    @abstractmethod
    def load(self) -> UiConfig:
        raise NotImplementedError

    @abstractmethod
    def save(self, app_config: UiConfig):
        raise NotImplementedError
