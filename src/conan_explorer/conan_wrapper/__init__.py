"""
This module contains all interfaces and backend functions
containing the applications core functionality.
Settings need to be already set up for usage.
"""

from conan_explorer import conan_version

# if hasattr(typing, "override"):
#     override = typing.override
# else:

from .unified_api import ConanCommonUnifiedApi


def ConanApiSingleton() -> ConanCommonUnifiedApi:
    if conan_version.startswith("1"):
        from .conanV1 import ConanApi
    elif conan_version.startswith("2"):
        from .conanV2 import ConanApi
    else:
        raise RuntimeError("Can't recognize Conan version")
    return ConanApi() # type: ignore
from .conan_cache import ConanInfoCache
from .conan_worker import ConanWorker
