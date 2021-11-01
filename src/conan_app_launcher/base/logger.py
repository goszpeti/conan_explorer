import logging
from threading import Lock
from typing import TYPE_CHECKING, Optional

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtBoundSignal, pyqtSignal

from conan_app_launcher import DEBUG_LEVEL, PROG_NAME

if TYPE_CHECKING:
    from conan_app_launcher.ui.main_window import MainWindow


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

    def __init__(self) -> None:
        return None

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
        _lock = Lock()

        def __init__(self, update_signal: pyqtBoundSignal):
            super().__init__(logging.DEBUG)
            self._update_signal = update_signal

        def emit(self, record):
            # don't access the qt object directly, since updates will only work
            # correctly in main loop, so instead send a PyQt Signal with the text to the Ui
            record = self.format(record)
            if record and self._lock:
                with self._lock:
                    self._update_signal.emit(record)

    @classmethod
    def init_qt_logger(cls, update_signal: pyqtBoundSignal):
        """
        Redirects the logger to QT widget.
        Needs to be called when GUI objects are available.
        """
        if not cls._instance:
            raise RuntimeError
        logger = cls._instance
        qt_handler = Logger.QtLogHandler(update_signal)
        qt_handler.set_name(cls.qt_handler_name)
        log_debug_level = logging.INFO
        if DEBUG_LEVEL > 0:
            log_debug_level = logging.DEBUG
        qt_handler.setLevel(log_debug_level)
        qt_handler.setFormatter(cls.formatter)

        logger.addHandler(qt_handler)

    @classmethod
    def remove_qt_logger(cls) -> bool:
        """ Remove qt logger (to be called before gui closes) """
        if not cls._instance:
            raise RuntimeError
        logger = cls._instance

        for handler in logger.handlers:
            if handler.get_name() == cls.qt_handler_name:
                logger.removeHandler(handler)
                if handler:
                    del(handler)
                return True
        return False
