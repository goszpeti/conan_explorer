from pathlib import Path
import tempfile
import pytest
from conan_app_launcher import INVALID_PATH
from conan_app_launcher.ui.plugin import PluginHandler, PluginFile, PluginDescription
from test.conftest import PathSetup

@pytest.mark.conanv2
def test_plugin_file_read(base_fixture: PathSetup, capfd: pytest.CaptureFixture[str]):
    """ test plugin file read method of all failures"""
    # nonexistant file
    plugins = PluginFile.read_file(Path(INVALID_PATH))
    assert plugins == []
    out = capfd.readouterr()
    assert "does not exist" in out.err

    # no content - no error
    empty_file = Path(tempfile.mktemp())
    empty_file.touch()
    plugins = PluginFile.read_file(empty_file)
    assert plugins == []

    # empty section
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_empty_section.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "Can't read PluginData0" in out.err

    # no name
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_name.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'name' is required" in out.err

    # no icon
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_icon.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'icon' is required" in out.err

    # icon invalid path
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_iconpath_invalid.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "icon" in out.err
    assert "does not exist" in out.err

    # no import path
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_importpath.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'import_path' is required" in out.err

    # import path invalid
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_importpath_invalid.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "import_path" in out.err
    assert "does not exist" in out.err

    # no class 
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_class.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'plugin_class' is required" in out.err

    # minimal valid file
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_minimal_valid.ini"
    plugins = PluginFile.read_file(plugin_file)
    assert len(plugins) == 1
    assert plugins[0].name == "Test Plugin"
    assert Path(plugins[0].icon).is_file()
    assert Path(plugins[0].import_path).is_dir()
    assert plugins[0].plugin_class == "TestPlugin"

def test_plugin_file_write():
    pass

def test_plugin_file_register():
    pass

def test_plugin_file_unregister():
    pass

@pytest.mark.conanv2
def test_plugin_handler_conan_version():
    """ Tests the refspec eval and is_plugin_enabled function of PluginHandler """
    assert not PluginHandler.eval_conan_version_spec(">2", "1.58.0")
    assert PluginHandler.eval_conan_version_spec(">2", "2.0.1")
    assert PluginHandler.eval_conan_version_spec("<2", "1.58.0")

    plugin = PluginDescription("", "1.58.0", "", "", "", "", "", False, "<2")
    assert PluginHandler.is_plugin_enabled(plugin)

def test_plugin_handler(base_fixture: PathSetup):
    ph = PluginHandler()

@pytest.mark.conanv1
def test_example_plugin():
    pass