from pathlib import Path
import tempfile
import pytest
import conan_explorer.app as app  # using global module pattern
from conan_explorer import BUILT_IN_PLUGIN, INVALID_PATH, AUTHOR
from conan_explorer.settings import PLUGINS_SECTION_NAME
from conan_explorer.ui.plugin import PluginHandler, PluginFile, PluginDescription
from test.conftest import PathSetup
from PySide6 import QtWidgets

def test_plugin_file_read(base_fixture: PathSetup, capfd: pytest.CaptureFixture[str]):
    """ test plugin file read method of all failures"""
    # nonexistant file
    plugins = PluginFile.read(Path(INVALID_PATH))
    assert plugins == []
    out = capfd.readouterr()
    assert "does not exist" in out.err

    # no content - no error
    empty_file = Path(tempfile.mktemp())
    empty_file.touch()
    plugins = PluginFile.read(empty_file)
    assert plugins == []

    # empty section
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_empty_section.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "Can't read PluginData0" in out.err

    # no name
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_name.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'name' is required" in out.err

    # no icon
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_icon.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'icon' is required" in out.err

    # icon invalid path
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_iconpath_invalid.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "icon" in out.err
    assert "does not exist" in out.err

    # no import path
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_importpath.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'import_path' is required" in out.err

    # import path invalid
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_importpath_invalid.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "import_path" in out.err
    assert "does not exist" in out.err

    # no class 
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_no_class.ini"
    plugins = PluginFile.read(plugin_file)
    assert plugins == []
    out = capfd.readouterr()
    assert "'plugin_class' is required" in out.err

    # minimal valid file
    plugin_file = base_fixture.testdata_path / "plugin" / "plugins_minimal_valid.ini"
    plugins = PluginFile.read(plugin_file)
    assert len(plugins) == 1
    assert plugins[0].name == "Test Plugin"
    assert Path(plugins[0].icon).is_file()
    assert Path(plugins[0].import_path).is_dir()
    assert plugins[0].plugin_class == "TestPlugin"

def test_plugin_file_write():
    """ Write out full plugin file with 2 plugins and compare line for line"""
    plugin_descrs = []
    plugin_descrs.append(PluginDescription("WriteTest", "0.0.1", AUTHOR, "icon.ico", "import_path", "PluginClass", "description", False, "<2.0.0"))
    plugin_descrs.append(PluginDescription("WriteTest2", "0.0.1", AUTHOR, "icon.ico", "import_path", "PluginClass", "description", False, "<2.0.0"))

    out_file_path = Path(tempfile.mktemp())
    PluginFile.write(out_file_path, plugin_descrs)
    content = out_file_path.read_text("utf-8")
    assert content == '[PluginDescription0]\nname = WriteTest\nversion = 0.0.1\nauthor = Péter Gosztolya and Contributors\nicon =' \
    ' icon.ico\nimport_path = import_path\nplugin_class = PluginClass\ndescription = description\nside_menu = False\nconan_versions'\
    ' = <2.0.0\n\n[PluginDescription1]\nname = WriteTest2\nversion = 0.0.1\nauthor = Péter Gosztolya and Contributors\nicon = icon.ico\n'\
    'import_path = import_path\nplugin_class = PluginClass\ndescription = description\nside_menu = False\nconan_versions = <2.0.0\n\n'

def test_plugin_file_register_unregister(base_fixture):
    """ Check, that registering a description file generates a uuid - path entry in settings, and the same plugin cannit be registered twice """
    plugin_groups = app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME)
    assert plugin_groups == [BUILT_IN_PLUGIN]

    plugin_file_path = base_fixture.testdata_path / "plugin" / "plugins_minimal_valid.ini"

    PluginFile.register(plugin_file_path)

    plugin_groups  = app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME)
    assert len(plugin_groups) == 2
    settings_plugin_file_path = ""
    for plugin_group in plugin_groups:
        if plugin_group == BUILT_IN_PLUGIN:
            continue
        settings_plugin_file_path = app.active_settings.get_string(plugin_group)
    assert Path(settings_plugin_file_path) == plugin_file_path

    # Check, that unregistering the description file removes it from settings
    PluginFile.unregister(plugin_file_path)
    plugin_groups  = app.active_settings.get_settings_from_node(PLUGINS_SECTION_NAME)
    assert len(plugin_groups) == 1

@pytest.mark.conanv2
def test_plugin_handler_conan_version():
    """ Tests the refspec eval and is_plugin_enabled function of PluginHandler """
    assert not PluginHandler.eval_conan_version_spec(">2", "1.58.0")
    assert PluginHandler.eval_conan_version_spec(">2", "2.0.1")
    assert PluginHandler.eval_conan_version_spec("<2", "1.58.0")

    plugin = PluginDescription("", "1.58.0", "", "", "", "", "", False, "<2")
    from conan_explorer import conan_version

    if conan_version.startswith("1"):
        assert PluginHandler.is_plugin_enabled(plugin)
    if conan_version.startswith("2"):
        assert not PluginHandler.is_plugin_enabled(plugin)


def test_plugin_handler(app_qt_fixture, base_fixture: PathSetup, mocker):
    """ Check loading and unloading mechanism """
    root_obj = QtWidgets.QWidget()
    app_qt_fixture.addWidget(root_obj)
    ph = PluginHandler(root_obj, None, None)
    plugin_file_path = base_fixture.testdata_path / "plugin" / "plugins_minimal_valid.ini"

    # add
    register_func_mock = mocker.patch.object(PluginFile, "register")
    ph.add_plugin(plugin_path=str(plugin_file_path))
    
    register_func_mock.assert_called_with(str(plugin_file_path))

    plugin_descrs = PluginFile.read(plugin_file_path)
    plugin_object = ph.get_plugin_by_description(plugin_descrs[0])
    assert plugin_object is not None
    plugin_object.show()
    app_qt_fixture.waitExposed(plugin_object)

    # remove
    unregister_func_mock = mocker.patch.object(PluginFile, "unregister")
    ph.remove_plugin(plugin_path=str(plugin_file_path))

    unregister_func_mock.assert_called_with(str(plugin_file_path))
    assert ph.get_plugin_by_description(plugin_descrs[0]) is None

