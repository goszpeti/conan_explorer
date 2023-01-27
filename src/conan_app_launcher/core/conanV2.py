from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

from conan_app_launcher.core.conan_common import ConanPkg
from conan_app_launcher.app.logger import Logger

if TYPE_CHECKING:
    from conans.client.cache.remote_registry import Remote
try:
    from conan.api.conan_api import ConanAPIV2, client_version
    from conans.client.cache.cache import ClientCache
    from conans.client.userio import UserInput
    from conan.api.output import ConanOutput
    from conans.errors import ConanException
    from conans.model.recipe_ref import RecipeReference as ConanFileReference
    from conans.model.package_ref import RecipeReference as PackageReference
except:
    Logger().error("Trying to import Conan 2 without probably being installed...")

try:
    from conans.util.windows import CONAN_REAL_PATH, path_shortener
except Exception:
    pass

from conan_app_launcher import (CONAN_LOG_PREFIX, INVALID_CONAN_REF,
                                SEARCH_APP_VERSIONS_IN_LOCAL_CACHE, base_path)

from .conan_cache import ConanInfoCache

class ConanApi():
    """ Wrapper around ConanAPIV2 """

    def __init__(self):
        self.conan: ConanAPIV2
        self.client_cache: ClientCache
        self.info_cache: ConanInfoCache
        self.client_version = client_version
        self._short_path_root = Path("Unknown")
