"""
This module contains all interfaces and backend functions
containing the applications core functionality.
Settings need to be already set up for usage.
"""

from conan_explorer import conan_version
if conan_version.startswith("1"):
    from .conanV1 import ConanApi
elif conan_version.startswith("2"):
    from .conanV2 import ConanApi
else:
    raise RuntimeError("Can't recognize Conan version")
from .conan_cache import ConanInfoCache
from .conan_worker import ConanWorker
