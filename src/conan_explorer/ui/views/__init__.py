"""Main views of the the Application (without opening a new dialog)"""

from .about import AboutPage
from .app_grid import AppGridView
from .conan_conf import ConanConfigView
from .conan_search import ConanSearchView
from .package_explorer import LocalConanPackageExplorer
from .plugins_manager import PluginsPage

__all__ = [
    "AppGridView",
    "LocalConanPackageExplorer",
    "ConanSearchView",
    "ConanConfigView",
    "AboutPage",
    "PluginsPage",
]
