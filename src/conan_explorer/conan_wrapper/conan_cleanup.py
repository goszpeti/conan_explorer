from pathlib import Path
import platform
from typing import TYPE_CHECKING, Dict, List, Set

from conan_explorer import conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import get_folder_size_mb
from conan_explorer.conan_wrapper.types import ConanRef
if TYPE_CHECKING:
    from .conanV1 import ConanApi

class ConanCleanup():

    def __init__(self, conan_api: "ConanApi") -> None:
        self._conan_api = conan_api
        self.cleanup_refs_info: Dict[str, Dict[str, str]] = {}
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
                ref_remote = ref_cache.load_metadata().recipe.remote # type: ignore
            except Exception:
                Logger().debug(f"Can't load metadata for {str(ref)}", exc_info=True)
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

    def get_cleanup_cache_info(self) -> Dict[str, Dict[str, str]]:
        """ Get a list of orphaned short path and cache folders """
        if platform.system() != "Windows" or conan_version.major == 2:
            return {} # TODO: Fix for linux
        from .types import PackageEditableLayout, CONAN_LINK
        del_list = {}
        for ref in self._conan_api.get_all_local_refs():
            # This will not updated to the unified API - only V1 relevant
            ref_cache = self._conan_api._client_cache.package_layout(ref)
            ref_str = str(ref)
            current_ref_info = {}

            # Get orphaned refs
            package_ids = []
            try:
                package_ids = ref_cache.package_ids()
            except Exception:
                try:
                    # old API of Conan
                    package_ids = ref_cache.packages_ids()  # type: ignore
                except Exception as e:
                    Logger().debug("Cannot check pkg id for %s: %s", ref, str(e), exc_info=True)
            for pkg_id in package_ids:
                short_path_dir = self._conan_api.get_package_folder(ref, pkg_id)
                pkg_id_dir = None
                # This will not updated to the unified API - only V1 relevant
                ref_cache = self._conan_api._client_cache.package_layout(ref)
                if not isinstance(ref_cache, PackageEditableLayout):
                    pkg_id_dir = Path(ref_cache.packages()) / pkg_id
                if not short_path_dir.exists():
                    if pkg_id_dir:
                        current_ref_info[str(pkg_id)] = str(pkg_id_dir)
           

            # get temporary dirs
            if not isinstance(ref_cache, PackageEditableLayout):
                source_path = Path(ref_cache.source())
                if source_path.exists():
                    # check for .conan_link
                    if (source_path / CONAN_LINK).is_file():
                        path = (source_path / CONAN_LINK).read_text()
                        current_ref_info["source"] = path.strip()
                    else:
                        current_ref_info["source"] = ref_cache.source()

                if Path(ref_cache.builds()).exists():
                    current_ref_info["build"] = ref_cache.builds()

                scm_source_path = Path(ref_cache.scm_sources())
                if scm_source_path.exists():
                    # check for .conan_link
                    if (scm_source_path / CONAN_LINK).is_file():
                        path = (scm_source_path / CONAN_LINK).read_text()
                        current_ref_info["scm_source"] = path.strip()
                    else:
                        current_ref_info["scm_source"] = ref_cache.scm_sources()
                download_folder = Path(ref_cache.base_folder()) / "dl"
                if download_folder.exists():
                    current_ref_info["download"] = str(download_folder)
                if current_ref_info:
                    del_list[ref_str] = current_ref_info
        self.cleanup_refs_info.update(del_list)

        self.find_orphaned_packages()
        self.cleanup_refs_info = dict(sorted(self.cleanup_refs_info.items()))
        return self.cleanup_refs_info

    def find_orphaned_packages(self):
        """ Reverse search for orphaned packages on windows short paths """
        if platform.system() != "Windows" or conan_version.major == 2:
            return {}
        from .types import CONAN_REAL_PATH

        del_list = {}
        short_path_folders = [f for f in self._conan_api.get_short_path_root().iterdir()
                              if f.is_dir()]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if rp_file.is_file():
                real_path = rp_file.read_text()
                if not Path(real_path).is_dir():
                    conan_ref = "Unknown"
                    type = "Unknown"
                    try:
                        # try to reconstruct conan ref from real_path
                        rel_path = Path(real_path).relative_to(self._conan_api.get_storage_path())
                        type = rel_path.parts[4]
                        conan_ref = str(ConanRef(rel_path.parts[0],
                                 rel_path.parts[1], rel_path.parts[2], rel_path.parts[3]))
                        
                    except Exception:
                        Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
                    if not self.cleanup_refs_info.get(conan_ref):
                        self.cleanup_refs_info[conan_ref] = {}
                    self.cleanup_refs_info[conan_ref][type] = str(short_path)
