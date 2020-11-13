
# use constants in class, so they don't need to be separately accessed
# use constants for string options


# constants for option names (value is the ini entry name)
# general
LAST_CONFIG_FILE = "last_config_file"
DISPLAY_APP_VERSIONS = "disp_app_versions"
DISPLAY_APP_CHANNELS = "disp_app_channels"


# import at the end, to avoid circular imports
from conan_app_launcher.settings.settings import Settings
