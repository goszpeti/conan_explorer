import os

import tempfile
from distutils.file_util import copy_file

from pathlib import Path

from conan_app_launcher.components.cache import ConanInfoCache
from conans.model.ref import ConanFileReference as CFR


def testNewCache():
    """
    Test, if a new cache file is generated, if it does not exist.
    """
    temp_dir = Path(tempfile.gettempdir())
    temp_cache_path = temp_dir / "cache.json"
    if temp_cache_path.exists():
        os.remove(str(temp_cache_path))
    cache = ConanInfoCache(temp_cache_path)
    assert temp_cache_path.exists()


def testReadCache(base_fixture):
    """
    Test reading from a cache file. Check internal state and use public API.
    """
    temp_cache_path = Path(tempfile.gettempdir()) / "cache.json"
    copy_file(str(base_fixture.testdata_path / "cache" / "cache_read.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path)
    assert cache._local_packages == {"my_package/1.0.0@myself/stable": "",
                                     "my_package/2.0.0@myself/stable": "C:\\.conan\\pkg"}
    assert cache._remote_packages == {
        "my_package@myself": [
            "1.0.0/stable",
            "2.0.0/stable",
            "2.0.0/testing"
        ],
        "other_package@others": [
            "1.0.0/testing",
            "2.0.0/stable",
            "3.0.0/stable"
        ]
    }

    assert str(cache.get_local_package_path("my_package/2.0.0@myself/stable")) == "C:\\.conan\\pkg"
    assert str(cache.get_local_package_path("my_package/1.0.0@myself/stable")) == "NULL"

    pkgs = cache.get_remote_pkg_refs("my_package", "myself")
    assert len(pkgs) == 3
    assert CFR.loads("my_package/1.0.0@myself/stable") in pkgs
    assert CFR.loads("my_package/2.0.0@myself/stable") in pkgs
    assert CFR.loads("my_package/2.0.0@myself/testing") in pkgs


def testReadAndDeleteCorruptCache(base_fixture):
    """Test, that an invalid jsonfile is deleted and a new one created"""
    temp_cache_path = Path(tempfile.gettempdir()) / "cache.json"
    copy_file(str(base_fixture.testdata_path / "cache" / "cache_read_corrupt.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path)
    info = ""
    with open(temp_cache_path) as tcf:
        info = tcf.read()
    assert info == ""


def testUpdateCache(base_fixture):
    """
    Test, if updating with new values appends/updates the values correctly in the file
    """
    temp_cache_path = Path(tempfile.gettempdir()) / "cache.json"
    copy_file(str(base_fixture.testdata_path / "cache" / "cache_write.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path)
    pkg = CFR.loads("new_pkg/1.0.0@me/stable")
    path = Path(r"C:\temp")
    cache.update_local_package_path(pkg, path)

    assert cache.get_local_package_path(pkg) == path

    add_packages = [CFR.loads("new_pkg/1.0.0@me/stable"), CFR.loads("new_pkg/1.1.0@me/stable"),
                    CFR.loads("new_pkg/1.1.0@me/testing"), CFR.loads("new_pkg/2.0.0@me/stable")]
    cache.update_remote_package_list(add_packages)

    remote_pkgs = cache.get_remote_pkg_refs("new_pkg", "me")
    assert set(remote_pkgs) == set(add_packages)
    remote_pkgs = cache.get_remote_pkg_refs("my_package", "myself")
    assert len(remote_pkgs) == 3

    cache.update_remote_package_list(add_packages, invalidate=True)
    remote_pkgs = cache.get_remote_pkg_refs("new_pkg", "me")
    assert set(remote_pkgs) == set(add_packages)
    remote_pkgs = cache.get_remote_pkg_refs("my_package", "myself")
    assert not remote_pkgs
