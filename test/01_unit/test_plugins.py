from conan_app_launcher.ui.plugin import PluginHandler


def test_eval_conan_spec():
    assert not PluginHandler.eval_conan_version_spec(">2", "1.58.0")
    assert PluginHandler.eval_conan_version_spec(">2", "2.0.1")
    assert PluginHandler.eval_conan_version_spec("<2", "1.58.0")
