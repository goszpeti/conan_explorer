
""" Use constants in class, so they don't need to be separately accessed """

# constants for option names (value is the ini entry name)
# General
LAST_CONFIG_FILE = "last_config_file"
# Views
DISPLAY_APP_VERSIONS = "disp_app_versions"
DISPLAY_APP_CHANNELS = "disp_app_channels"
GRID_ROWS = "grid_rows"
GRID_COLUMNS = "grid_columns"

# import at the end, to avoid circular imports
from conan_app_launcher.settings.settings import Settings
