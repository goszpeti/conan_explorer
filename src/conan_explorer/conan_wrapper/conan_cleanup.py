import platform
from pathlib import Path
from typing import Dict, List, Set

import conan_explorer.app as app
from conan_explorer import conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.conan_wrapper.types import ConanRef


class ConanCleanup:
    def __init__(self) -> None:
        self.cleanup_refs_info: Dict[str, Dict[str, str]] = {}
        self.invalid_metadata_refs: Set[str] = set()

    def gather_invalid_remote_metadata(self) -> List[str]:
        """Gather all references with invalid remotes"""
        invalid_refs = []
        remotes = app.conan_api.get_remotes(include_disabled=True)
        remote_names = [r.name for r in remotes]
        for ref in app.conan_api.get_all_local_refs():
            # This will not updated to the unified API - only V1 relevant
            ref_cache = app.conan_api._client_cache.package_layout(ref)  # type: ignore
            ref_remote = ""
            try:
                ref_remote = ref_cache.load_metadata().recipe.remote  # type: ignore
            except Exception:
                Logger().debug("Can't load metadata for %s", str(ref), exc_info=True)
                continue
            if ref_remote not in remote_names:
                invalid_refs.append(str(ref))
        self.invalid_metadata_refs = set(invalid_refs)
        return invalid_refs

    def repair_invalid_remote_metadata(self, invalid_ref):
        """Repair all references with invalid remotes"""
        # calling inspect with a correct remote repairs the metadata
        for remote in app.conan_api.get_remotes():
            try:
                app.conan_api._conan.inspect(invalid_ref, None, remote.name)  # type: ignore
                break
            except Exception:
                continue

    def get_cleanup_cache_info(self) -> Dict[str, Dict[str, str]]:
        """Get a list of orphaned short path and cache folders"""
        if platform.system() != "Windows" or conan_version.major == 2:
            return {}  # TODO: Update for linux
        from .types import CONAN_LINK

        editables = app.conan_api.get_editable_references()

        for conan_ref in app.conan_api.get_all_local_refs():
            if conan_ref in editables:
                continue
            current_ref_info = {}

            # this will not updated to the unified API - only V1 relevant
            ref_cache = app.conan_api._client_cache.package_layout(conan_ref)  # type: ignore

            # get orphaned refs
            package_ids = []
            try:
                package_ids = ref_cache.package_ids()
            except Exception:
                try:
                    # old API of Conan
                    package_ids = ref_cache.packages_ids()  # type: ignore
                except Exception as e:
                    Logger().debug(
                        "Cannot check pkg id for %s: %s", str(conan_ref), str(e), exc_info=True
                    )

            for pkg_id in package_ids:
                short_path_dir = app.conan_api.get_package_folder(conan_ref, pkg_id)
                if not short_path_dir.exists():
                    current_ref_info[str(pkg_id)] = str(Path(ref_cache.packages()) / pkg_id)

            # get temporary dirs
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
                self.cleanup_refs_info[str(conan_ref)] = current_ref_info

        self.find_orphaned_packages()
        self.cleanup_refs_info = dict(sorted(self.cleanup_refs_info.items()))
        return self.cleanup_refs_info

    def find_orphaned_packages(self):
        """Reverse search for orphaned packages on windows short paths"""
        if platform.system() != "Windows" or conan_version.major == 2:
            return {}
        from .types import CONAN_REAL_PATH

        short_path_folders = [
            f for f in app.conan_api.get_short_path_root().iterdir() if f.is_dir()
        ]
        for short_path in short_path_folders:
            rp_file = short_path / CONAN_REAL_PATH
            if not rp_file.is_file():
                continue
            real_path = rp_file.read_text()

            if Path(real_path).is_dir():
                continue
            conan_ref = "Unknown"
            info_type = "Unknown"
            try:
                # try to reconstruct conan ref from real_path
                rel_path = Path(real_path).relative_to(app.conan_api.get_storage_path())
                info_type = rel_path.parts[4]
                conan_ref = str(
                    ConanRef(
                        rel_path.parts[0],
                        rel_path.parts[1],
                        rel_path.parts[2],
                        rel_path.parts[3],
                    )
                )

            except Exception:
                Logger().error(f"Can't read {CONAN_REAL_PATH} in {str(short_path)}")
            if not self.cleanup_refs_info.get(conan_ref):
                self.cleanup_refs_info[conan_ref] = {}
            self.cleanup_refs_info[conan_ref][info_type] = str(short_path)
