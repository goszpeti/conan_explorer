from . import ConanApi
from pathlib import Path
import platform
from typing import Set

from conan_explorer import conan_version
from conan_explorer.app.logger import Logger

class ConanCleanup():

    def __init__(self, conan_api: ConanApi) -> None:
        self._conan_api = conan_api
        self.orphaned_references: Set[str] = set()
        self.orphaned_packages: Set[str] = set()

    def get_cleanup_cache_paths(self) -> Set[str]:
        """ Get a list of orphaned short path and cache folders """
        # Blessed are the users Microsoft products!
        if platform.system() != "Windows" or conan_version.startswith("2"):
            return set()
        self.find_orphaned_references()
        self.find_orphaned_packages()
        return self.orphaned_references.union(self.orphaned_packages)

    def find_orphaned_references(self):
        from .types import PackageEditableLayout
        del_list = []
        for ref in self._conan_api.get_all_local_refs():
            # This will not updated to the unified API - only V1 relevant
            ref_cache = self._conan_api._client_cache.package_layout(ref)
            # get_local_pkgs_from_ref will not find orphaned packages...
            package_ids = []
            try:
                package_ids = ref_cache.package_ids()
            except Exception:
                try:
                    package_ids = ref_cache.packages_ids()  # type: ignore - old API of Conan
                except Exception as e:
                    Logger().debug("Cannot check pkg id for %s: %s", ref, str(e))
            for pkg_id in package_ids:
                short_path_dir = self._conan_api.get_package_folder(ref, pkg_id)
                pkg_id_dir = None
                # This will not updated to the unified API - only V1 relevant
                ref_cache = self._conan_api._client_cache.package_layout(ref)
                if not isinstance(ref_cache, PackageEditableLayout):
                    pkg_id_dir = Path(ref_cache.packages()) / pkg_id
                if not short_path_dir.exists():
                    Logger().debug(f"Can't find {str(short_path_dir)} for {str(ref)}")
                    if pkg_id_dir:
                        del_list.append(str(pkg_id_dir))
        self.orphaned_references = set(del_list)

    def find_orphaned_packages(self):
        """ Reverse search for orphaned packages on windows short paths """
        from .types import CONAN_REAL_PATH

        del_list = []
        short_path_folders = [f for f in self._conan_api.get_short_path_root().iterdir()
                              if f.is_dir()]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if rp_file.is_file():
                with open(str(rp_file)) as fp:
                    real_path = fp.read()
                try:
                    if not Path(real_path).is_dir():
                        Logger().debug(f"Can't find {real_path} for {str(short_path)}")
                        del_list.append(str(short_path))
                except Exception:
                    Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
        self.orphaned_packages = set(del_list)
