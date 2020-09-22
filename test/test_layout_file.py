import os

from conan_app_launcher.layout_file import parse_layout_file


def testCorrectFile(base_fixture):

    tabs = parse_layout_file(base_fixture.testdata_path / "app_config.json")
    assert tabs[0].name == "Basics"
    assert tabs[1].name == "Extra"


def testIncorrectFilename(base_fixture):
    parse_layout_file(base_fixture.testdata_path / "nofile.json")


def testInvalidContent(base_fixture):
    pass

# def testInitOnTarget(mocker):
#     # Mocks call to get info of Rpi
#     mock_platform = mock_run_on_target(mocker)
#     cur_system = RuntimeSystem()
#     assert cur_system.is_target_system
#     # Actual string is platform dependent
#     assert cur_system.platform == mock_platform.return_value


# def testShutdown(mocker):
#     # TODO this would be really cool in Docker with an actual system
#     mock_run_on_target(mocker)
#     mocker.patch('os.system')
#     cur_system = RuntimeSystem()
#     cur_system.shutdown()
#     # not ideal: confidence through duplication
#     os.system.assert_called_once_with('shutdown now')  # pylint: disable=no-member


# def testRestart(mocker):
#     # TODO this would be really cool in Docker with an actual system
#     mock_run_on_target(mocker)
#     mocker.patch('os.system')
#     cur_system = RuntimeSystem()
#     cur_system.restart()
#     # not ideal: confidence through duplication
#     os.system.assert_called_once_with('shutdown -r now')  # pylint: disable=no-member


# def testGetIPOnTarget(mocker):
#     # TODO this would be really cool in Docker with an actual system
#     mock_run_on_target(mocker)
#     cur_system = RuntimeSystem()

#     ip4_ref = "192.168.1.274"
#     ip6_ref = "2001:db8:85a3:8d3:1319:8a2e:370:7348"
#     mock_call = mocker.Mock()

#     # check only ip4
#     mock_call.return_value = ip4_ref.encode("utf-8")
#     mocker.patch('subprocess.check_output', mock_call)
#     [ip4, ip6] = cur_system.get_ip()
#     assert ip4 == ip4_ref
#     assert ip6 is None

#     # check only ip6
#     mock_call.return_value = ip6_ref.encode("utf-8")
#     mocker.patch('subprocess.check_output', mock_call)
#     [ip4, ip6] = cur_system.get_ip()
#     assert ip4 is None
#     assert ip6 == ip6_ref

#     # check both ip4 and ip6
#     mock_call.return_value = (ip4_ref + " " + ip6_ref).encode("utf-8")
#     mocker.patch('subprocess.check_output', mock_call)
#     [ip4, ip6] = cur_system.get_ip()
#     assert ip4 == ip4_ref
#     assert ip6 == ip6_ref
