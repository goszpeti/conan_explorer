
import tempfile
import pytest
from shutil import copyfile
from pathlib import Path
from conan_explorer import INVALID_PATH
from conan_explorer import conan_version

from conan_explorer.conan_wrapper import ConanInfoCache
from conan_explorer.conan_wrapper.types import ConanRef as CFR
from test.conftest import PathSetup


@pytest.mark.conanv2
def test_new_cache():
    """
    Test, if a new cache file is generated, if it does not exist.
    """
    temp_dir = Path(tempfile.mkdtemp())
    ConanInfoCache(temp_dir)
    assert (temp_dir / ConanInfoCache.CACHE_FILE_NAME).exists()


@pytest.mark.conanv2
def test_read_cache(base_fixture: PathSetup):
    """
    Test reading from a cache file. Check internal state and use public API.
    """
    temp_cache_path = Path(tempfile.mkdtemp()) / ConanInfoCache.CACHE_FILE_NAME
    copyfile(str(base_fixture.testdata_path / "cache" / "cache_read.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path.parent)
    assert cache._local_packages == {"my_package/1.0.0@user/channel": "",
                                     "my_package/2.0.0@user/channel": "C:\\.conan\\pkg"}
    assert cache._remote_packages == {
        "my_package": {"user": [
            "1.0.0/channel",
            "2.0.0/channel"]
        },
        "other_package": {"others": [
            "1.0.0/testing",
            "2.0.0/stable",
            "3.0.0/stable"],
            "local": [
                "1.0.0/testing"
        ]
        }
    }
    assert str(cache.get_local_package_path(CFR.loads("my_package/2.0.0@user/channel"))) == "C:\\.conan\\pkg"
    assert str(cache.get_local_package_path(CFR.loads("my_package/1.0.0@user/channel"))) == INVALID_PATH

    pkgs = cache.get_similar_remote_pkg_refs("my_package", "user")
    assert len(pkgs) == 2
    assert CFR.loads("my_package/1.0.0@user/channel") in pkgs
    assert CFR.loads("my_package/2.0.0@user/channel") in pkgs


@pytest.mark.conanv2
def test_read_and_delete_corrupt_cache(base_fixture: PathSetup):
    """Test, that an invalid jsonfile is deleted and a new one created"""
    temp_cache_path = Path(tempfile.mkdtemp()) / ConanInfoCache.CACHE_FILE_NAME
    copyfile(str(base_fixture.testdata_path / "cache" / "cache_read_corrupt.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path.parent)
    info = ""
    with open(temp_cache_path) as tcf:
        info = tcf.read()
    assert info == ""


@pytest.mark.conanv2
def test_update_cache(base_fixture: PathSetup):
    """
    Test, if updating with new values appends/updates the values correctly in the file
    """
    temp_cache_path = Path(tempfile.mkdtemp()) / ConanInfoCache.CACHE_FILE_NAME
    copyfile(str(base_fixture.testdata_path / "cache" / "cache_write.json"), str(temp_cache_path))

    cache = ConanInfoCache(temp_cache_path.parent)
    pkg = CFR.loads("new_pkg/1.0.0@me/stable")
    path = Path(r"C:\temp")
    cache.update_local_package_path(pkg, path)
    assert cache.get_local_package_path(pkg) == path

    # test official - does not work in Conan 2
    if conan_version.major == 1:
        pkg = CFR.loads("official_pkg/1.0.0@_/_")
        path = Path(r"C:\temp")
        cache.update_local_package_path(pkg, path)
        assert cache.get_local_package_path(pkg) == path

    add_packages = [CFR.loads("new_pkg/1.0.0@me/stable"), CFR.loads("new_pkg/1.1.0@me/stable"),
                    CFR.loads("new_pkg/1.1.0@me/testing"), CFR.loads("new_pkg/2.0.0@me/stable")]
    cache.update_remote_package_list(add_packages)

    remote_pkgs = cache.get_similar_remote_pkg_refs("new_pkg", "me")
    assert set(remote_pkgs) == set(add_packages)
    remote_pkgs = cache.get_similar_remote_pkg_refs("my_package", "myself")
    assert len(remote_pkgs) == 3
    remote_pkgs = cache.get_similar_remote_pkg_refs("other_package", "*")
    assert len(remote_pkgs) == 4

    cache.update_remote_package_list(add_packages, invalidate=True)
    remote_pkgs = cache.get_similar_remote_pkg_refs("new_pkg", "me")
    assert set(remote_pkgs) == set(add_packages)
    remote_pkgs = cache.get_similar_remote_pkg_refs("my_package", "myself")
    assert not remote_pkgs
