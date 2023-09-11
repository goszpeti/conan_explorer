

import ctypes
import platform


def gen_obj_name(name: str) -> str:
    """ Generates an object name from a menu title or name
    (spaces to underscores and lowercase) """
    return name.replace(" ", "_").lower()

def get_display_scaling():
    if platform.system() == "Windows":
        return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    else:  # TODO not yet implemented for Linux
        return 2.2

LEFT_MENU_MIN_WIDTH = 80
LEFT_MENU_MAX_WIDTH = int(310 + 20*(2/get_display_scaling()))
RIGHT_MENU_MIN_WIDTH = 0
RIGHT_MENU_MAX_WIDTH = int(160 + 200*(2/get_display_scaling()))

from .fluent_window import FluentWindow
from .side_menu import SideSubMenu