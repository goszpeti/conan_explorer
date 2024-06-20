from pathlib import Path
import platform
from typing import TYPE_CHECKING, List, Set

from conan_explorer import conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import get_folder_size
if TYPE_CHECKING:
    from .conanV1 import ConanApi

class ConanCleanup():

    def __init__(self, conan_api: "ConanApi") -> None:
        self._conan_api = conan_api
        self.orphaned_references: Set[str] = set()
        self.orphaned_packages: Set[str] = set()
        self.invalid_metadata_refs: Set[str] = set()

    def gather_invalid_remote_metadata(self) -> List[str]:
        """ Gather all references with invalid remotes """
        invalid_refs = []
        remotes = self._conan_api.get_remotes(include_disabled=True)
        remote_names = [r.name for r in remotes]
        for ref in self._conan_api.get_all_local_refs():
            # This will not updated to the unified API - only V1 relevant
            ref_cache = self._conan_api._client_cache.package_layout(ref)
            ref_remote = ""
            try:
                ref_remote = ref_cache.load_metadata().recipe.remote
            except Exception:
                Logger().debug(f"Can't load metadata for {str(ref)}")
                continue
            if ref_remote not in remote_names:
                invalid_refs.append(str(ref))
        self.invalid_metadata_refs = set(invalid_refs)
        return invalid_refs
    
    def repair_invalid_remote_metadata(self, invalid_ref):
        """ Repair all references with invalid remotes """
        # calling inspect with a correct remote repiars the metadata    
        for remote in self._conan_api.get_remotes():
            try:
                self._conan_api._conan.inspect(invalid_ref, None, remote.name)
                break
            except Exception:
                continue

    def get_cleanup_cache_paths(self) -> Set[str]:
        """ Get a list of orphaned short path and cache folders """
        # Blessed are the users Microsoft products!
        if platform.system() != "Windows" or conan_version.major == 2:
            return set()
        self.find_orphaned_references()
        self.find_orphaned_packages()
        return self.orphaned_references.union(self.orphaned_packages)
    
    def get_cumulated_cleanup_size(self):
        size_mbytes = 0
        for ref in self.orphaned_references:
            size_mbytes += get_folder_size(Path(ref))
        return size_mbytes

    def find_orphaned_references(self):
        from .types import PackageEditableLayout, CONAN_LINK
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
                    # old API of Conan
                    package_ids = ref_cache.packages_ids()  # type: ignore
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
           
            if not isinstance(ref_cache, PackageEditableLayout):
                source_path = Path(ref_cache.source())
                if source_path.exists():
                    # check for .conan_link
                    if (source_path / CONAN_LINK).is_file():
                        path = (source_path / CONAN_LINK).read_text()
                        del_list.append(path.strip())
                    else:
                        del_list.append(ref_cache.source())

                if Path(ref_cache.builds()).exists():
                    del_list.append(ref_cache.builds())

                scm_source_path = Path(ref_cache.scm_sources())
                if scm_source_path.exists():
                    # check for .conan_link
                    if (scm_source_path / CONAN_LINK).is_file():
                        path = (scm_source_path / CONAN_LINK).read_text()
                        del_list.append(path.strip())
                    else:
                        del_list.append(ref_cache.scm_sources())
                download_folder = Path(ref_cache.base_folder()) / "dl"
                if download_folder.exists():
                    del_list.append(str(download_folder))
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
                real_path = rp_file.read_text()
                try:
                    if not Path(real_path).is_dir():
                        Logger().debug(f"Can't find {real_path} for {str(short_path)}")
                        del_list.append(str(short_path))
                except Exception:
                    Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
        self.orphaned_packages = set(del_list)
