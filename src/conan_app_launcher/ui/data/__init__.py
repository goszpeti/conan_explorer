
from typing import Union
from conan_app_launcher import INVALID_CONAN_REF, PathLike
from abc import ABC, abstractmethod

from typing import Dict, List, TYPE_CHECKING
from dataclasses import dataclass, field

UI_CONFIG_JSON_TYPE = "json"

# classes representing the ui config (Data Transfer Objects) - this is a bit overblown for this usecase,
# but ot is worth an experiment
if TYPE_CHECKING:  # pragma: no cover
    from ..modules.app_grid.model import UiAppLinkModel, UiTabModel


@dataclass
class UiAppLinkConfig():
    name: str = "New App"
    conan_ref: str = INVALID_CONAN_REF
    executable: str = ""
    icon: str = ""
    is_console_application: bool = False
    args: str = ""
    conan_options: Dict[str, str] = field(default_factory=dict)


@dataclass
class UiTabConfig():
    name: str = "New Tab"
    # TODO: The Union is a workaround. How to say, that this is the base class?
    apps: List[Union[UiAppLinkConfig, "UiAppLinkModel"]] = field(default_factory=list)

    def __post_init__(self):
        if not self.apps:
            self.apps.append(UiAppLinkConfig())


@dataclass
class UiAppGridConfig():
    # TODO: The Union is a workaround. How to say, that this is the base class?
    tabs: List[Union[UiTabConfig, "UiTabModel"]] = field(default_factory=list)

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


class UiConfigInterface(ABC):
    """
    Abstract Class to implement ui config mechanism.
    Source artefact should be passed by constructor an and is not changeable.
    """

    @abstractmethod
    def load(self) -> UiConfig:
        raise NotImplementedError

    @abstractmethod
    def save(self, app_config: UiConfig):
        raise NotImplementedError
