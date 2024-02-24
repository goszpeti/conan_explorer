"""
This module contains all interfaces and backend functions
containing the applications core functionality.
Settings need to be already set up for usage.
"""

from conan_explorer import conan_version, Version
from .unified_api import ConanCommonUnifiedApi
from .conan_cache import ConanInfoCache
from .conan_worker import ConanWorker

def ConanApiFactory() -> ConanCommonUnifiedApi:
    """ Isntantiate ConanApi in the correct version """
    if conan_version.major == 1:
        from conan_explorer.conan_wrapper.conanV1 import ConanApi
        return ConanApi()
    elif conan_version.major == 2:
        from .conanV2 import ConanApi
        return ConanApi()
    else:
        raise RuntimeError("Can't recognize Conan version")

