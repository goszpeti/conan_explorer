import logging
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from typing import Self

from conan_explorer import DEBUG_LEVEL, PKG_NAME

class Logger(logging.Logger):
    """
    Singleton instance for the global dual logger (Qt Widget/console)
    """
    _instance: Optional[logging.Logger] = None
    formatter = logging.Formatter(r"%(levelname)s: %(message)s")

    def __new__(cls) -> "Self":
        if cls._instance is None:
            # the user excepts a logger
            cls._instance = cls._init_logger()
        return cls._instance # type: ignore

    def __init__(self) -> None:
        return None

    @classmethod
    def _init_logger(cls):
        """ Set up format and a debug level and register console logger. """
        # restrict root logger
        root = logging.getLogger()
        root.setLevel(logging.ERROR)

        logger = logging.getLogger(PKG_NAME)
        logger.setLevel(logging.DEBUG)
        log_debug_level = logging.INFO
        if DEBUG_LEVEL > 0:
            log_debug_level = logging.DEBUG

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_debug_level)

        console_handler.setFormatter(cls.formatter)

        logger.addHandler(console_handler)

        # otherwise messages appear twice
        logger.propagate = False

        return logger
