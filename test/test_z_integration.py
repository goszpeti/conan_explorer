"""
This test starts the application.
It is called z_integration, so that it launches last.
"""

import os
import sys
import threading
import time



def testDebugDisabledForRelease(base_fixture):
    from piweather import config
    assert config.DEBUG_LEVEL == 0  # debug level should be 0 for release


def testMinimalUseCase(base_fixture):
    from conan_app_launcher import main, config
    sys.argv = []

    main_thread = threading.Thread(target=main.main, args=[base_fixture.testdata_path / "integration", ])
    main_thread.start()

    time.sleep(3)
    
    # check after init
    # components.temp_hum_sensor.get_temperature()
    try:
        config.qt_app.quit()
        time.sleep(5)
    finally:
        if main_thread:
            main_thread.join(5)
        if config.qt_app:
            config.qt_app.quit()

    # TODO press option, return to main ui, repeat a few times
