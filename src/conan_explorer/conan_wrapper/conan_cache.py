import json
from multiprocessing import RLock
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from conan_explorer import INVALID_CONAN_REF, INVALID_PATH, conan_version
from conan_explorer.app.logger import Logger
from conan_explorer.app.system import delete_path
from .types import ConanRef
from .unified_api import ConanCommonUnifiedApi as ConanAPI


class ConanInfoCache():
    """
    This is a cache to accelerate calls which need remote access.
    It also has an option to store the local package path.
    """
    CACHE_FILE_NAME = "cache.json"
    if conan_version.major == 2:
        CACHE_FILE_NAME = "cacheV2.json"

    def __init__(self, cache_dir: Path, local_refs: Optional[List[ConanRef]] = None):
        if not local_refs:
            local_refs = []

        self._cache_file = cache_dir / self.CACHE_FILE_NAME
        self._local_packages: Dict[str, str] = {}
        self._remote_packages: Dict[str, Dict[str, List[str]]] = {}
        self._read_only = False  # for testing purposes
        self._all_local_refs = local_refs
        self._access_lock = RLock()

        # create cache file, if it does not exist
        if not self._cache_file.exists():
            self._cache_file.touch()
            return

        # read cached info
        self._load()

    def get_local_package_path(self, conan_ref: ConanRef) -> Path:
        """ Return cached package path of a locally installed package. """
        conan_ref_str = ConanAPI.generate_canonical_ref(conan_ref)
        if not conan_ref_str or conan_ref_str == INVALID_CONAN_REF:
            return Path(INVALID_PATH)

        with self._access_lock:
            pkg_path_str = self._local_packages.get(conan_ref_str, "")
        if not pkg_path_str:
            pkg_path = Path(INVALID_PATH)
        else:
            pkg_path = Path(pkg_path_str)

        # validate own cache - remove element if path does not exist
        with self._access_lock:
            if not pkg_path.exists() and conan_ref_str in self._local_packages.keys():
                self._local_packages.pop(conan_ref_str)
            return pkg_path

    def get_similar_pkg_refs(self, name: str, user: str):
        """ Return cached info on all available conan refs from the same ref name and user. """
        return self.get_similar_remote_pkg_refs(name, user) + \
            self.get_similar_local_pkg_refs(name, user)

    def get_similar_remote_pkg_refs(self, name: str, user: str) -> List[ConanRef]:
        """ Return cached info on remotely available conan refs from the same ref name and user. """
        if not user:  # official pkgs have no user, substituted by _
            user = "_"
        refs: List[ConanRef] = []
        with self._access_lock:
            if user == "*":  # find all refs with same name
                name_pkgs = self._remote_packages.get(name, {})
                for user in name_pkgs:
                    for version_channel in self._remote_packages.get(name, {}).get(user, []):
                        version, channel = version_channel.split("/")
                        refs.append(ConanRef(name, version, user, channel))
            else:
                user_pkgs = self._remote_packages.get(name, {}).get(user, [])
                for version_channel in user_pkgs:
                    version, channel = version_channel.split("/")
                    refs.append(ConanRef(name, version, user, channel))
        return refs

    def get_similar_local_pkg_refs(self, name: str, user: str) -> List[ConanRef]:
        """ Return cached info on locally available conan refs from the same ref name and user. """
        refs: List[ConanRef] = []
        with self._access_lock:
            for ref in self._all_local_refs:
                if ref.name == name:
                    if user != "*" and ref.user != user:
                        continue  # doe not match user
                    refs.append(ref)
        return refs

    def get_all_remote_refs(self) -> List[str]:
        """ Return all remote references. Updating, when queries finish. """
        refs = []
        with self._access_lock:
            for name in self._remote_packages:
                for user in self._remote_packages[name]:
                    for version_channel in self._remote_packages.get(name, {}).get(user, []):
                        version, channel = version_channel.split("/")
                        refs.append(
                            str(ConanRef(name, version, user, channel)))
        return refs

    def get_all_local_refs(self) -> List[str]:
        """ 
        Return all locally installed references.
        Cache updating on start and when installing in this app.
        """
        refs = []
        with self._access_lock:
            for ref in self._all_local_refs:
                refs.append(str(ref))
        return refs

    def search(self, query: str) -> Tuple[Set[str], Set[str]]:
        """
        Return cached info on available conan refs from a query 
        <Currently unsused!>
        """
        with self._access_lock:

            remote_refs = set()
            local_refs = set()
            # try to extract name and user from query
            split_query = query.split("/")
            name = split_query[0]
            user = "*"
            if len(split_query) > 1:
                user_split = split_query[1].split("@")
                if len(user_split) > 1:
                    user = user_split[1]
            for ref in self.get_similar_remote_pkg_refs(name, user):
                remote_refs.add(str(ref))

            for ref in self._all_local_refs:
                if query in str(ref):
                    local_refs.add(str(ref))
            return (local_refs, remote_refs)

    def update_local_package_path(self, conan_ref: ConanRef, folder: Path):
        """ Update the cache with the path of a local package path. """
        with self._access_lock:
            if self._local_packages.get(str(conan_ref)) == str(folder):
                return
            self._local_packages.update(
                {ConanAPI.generate_canonical_ref(conan_ref): str(folder.as_posix())})
            self._save()

    def invalidate_remote_package(self, conan_ref: ConanRef):
        """ Remove a package, wich was removed on the remote """
        version_channels = self._remote_packages.get(
            conan_ref.name, {}).get(str(conan_ref.user), [])
        invalid_version_channel = f"{conan_ref.version}/{conan_ref.channel}"
        if invalid_version_channel in version_channels:
            Logger().debug(f"Invalidated {str(conan_ref)} from remote cache.")
            version_channels.remove(f"{conan_ref.version}/{conan_ref.channel}")
            self._save()

    def update_remote_package_list(self, remote_packages: List[ConanRef], invalidate=False):
        """
        Update the cache with the info of several remote packages. 
        Invalidate option clears the cache.
        """
        with self._access_lock:
            if invalidate:  # clear cache
                self._remote_packages.clear()
                self._save()
            for ref in remote_packages:
                # convert back the official cache entries
                user = str(ref.user)
                channel = ref.channel
                if ref.user is None and ref.channel is None:
                    user = "_"
                    channel = "_"
                current_version_channel = f"{ref.version}/{channel}"
                version_channels = set(
                    self._remote_packages.get(ref.name, {}).get(user, []))
                if current_version_channel not in version_channels:
                    version_channels.add(current_version_channel)
                    version_channels_list = list(version_channels)
                    if not self._remote_packages.get(ref.name):
                        self._remote_packages.update({ref.name: {}})
                    self._remote_packages.get(ref.name, {}).update(
                        {user: version_channels_list})

            self._save()

    def _load(self):
        """ Load the cache. """
        json_data = {}
        try:
            with open(self._cache_file, "r") as json_file:
                content = json_file.read()
                if len(content) > 0:
                    json_data = json.loads(content)
        except Exception:  # possibly corrupt, delete cache file
            Logger().debug("ConanCache: Can't read speedup-cache file, deleting it.")
            delete_path(self._cache_file)
            # create file anew
            self._cache_file.touch()
            return
        self._local_packages = json_data.get("local_packages", {})
        self._remote_packages = json_data.get("remote_packages", {})
        self._read_only = json_data.get("read_only", False)

    def _save(self):
        """ Write the cache to file. """
        if self._read_only:
            return
        json_data = {}
        with self._access_lock:
            json_data["read_only"] = self._read_only
            json_data["remote_packages"] = self._remote_packages
            json_data["local_packages"] = self._local_packages
            try:
                with open(self._cache_file, "w") as json_file:
                    json.dump(json_data, json_file)
            except Exception:
                Logger().debug("ConanCache: Can't save speedup-cache file.")
