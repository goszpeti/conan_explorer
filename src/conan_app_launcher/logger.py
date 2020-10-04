import logging
from typing import Optional
import time
from PyQt5 import QtWidgets
from threading import Lock
from conan_app_launcher import DEBUG_LEVEL, PROG_NAME
lock = Lock()


class Logger(logging.Logger):
    """
    Singleton instance for the global dual logger (Qt Widget/console)
    """
    _instance: Optional[logging.Logger] = None
    formatter = logging.Formatter(r"%(levelname)s: %(message)s")
    qt_handler_name = "qt_handler"

    def __new__(cls):
        if cls._instance is None:
            # the user excepts a logger
            cls._instance = cls._init_logger()
        return cls._instance

    @classmethod
    def _init_logger(cls) -> logging.Logger:
        """ Set up format and a debug level and register console logger. """
        # restrict root logger
        root = logging.getLogger()
        root.setLevel(logging.ERROR)

        logger = logging.getLogger(PROG_NAME)
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

    class QtLogHandler(logging.Handler):
        """ This log handler prints to a qt widget """

        def __init__(self, widget: QtWidgets.QWidget):
            super().__init__(logging.DEBUG)
            self._widget = widget

        def emit(self, record):
            record = self.format(record)
            if record:
                with lock:
                    self._widget.text = record
                    self._widget.logging.emit()

    @classmethod
    def init_qt_logger(cls, widget):
        """
        Redirects the logger to QT widget.
        Needs to be called when GUI objects are available.
        """
        logger = cls._instance
        qt_handler = Logger.QtLogHandler(widget)
        qt_handler.set_name(cls.qt_handler_name)
        log_debug_level = logging.INFO
        if DEBUG_LEVEL > 0:
            log_debug_level = logging.DEBUG
        qt_handler.setLevel(log_debug_level)
        qt_handler.setFormatter(cls.formatter)

        logger.addHandler(qt_handler)

    @classmethod
    def remove_qt_logger(cls) -> bool:
        logger = cls._instance

        for handler in logger.handlers:
            if handler.get_name() == cls.qt_handler_name:
                logger.removeHandler(handler)
                return True
        return False
