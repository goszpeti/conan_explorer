"""
This module contains all interfaces and backend functions
containing the applications core functionality.
Settings need to be already set up for usage.
"""
from .conan_cache import ConanInfoCache
from .conan_worker import ConanWorker
from .system import (open_cmd_in_path, open_file, open_in_file_manager, run_file)
import conan
try:
    from .conanV1 import ConanApi
except:
    from .conanV2 import ConanApi