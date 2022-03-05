import logging
from threading import Lock
from typing import Optional

from PyQt5.QtCore import pyqtBoundSignal

from conan_app_launcher import CONAN_LOG_PREFIX, DEBUG_LEVEL, PKG_NAME


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

    class QtLogHandler(logging.Handler):
        """
        This log handler sends a logger string to a qt widget.
        update_signal needs str as argument.
        """
        _lock = Lock()

        def __init__(self, update_signal: pyqtBoundSignal):
            super().__init__(logging.DEBUG)
            self._update_signal = update_signal

        def emit(self, record: logging.LogRecord):
            # don't access the qt object directly, since updates will only work
            # correctly in main loop, so instead send a PyQt Signal with the text to the Ui
            
            if not record.message.startswith(CONAN_LOG_PREFIX):
                message = self.format(record)
            else:
                # remove log formatting for conan logs
                message = record.message.replace(CONAN_LOG_PREFIX, "")
            if message and self._lock:  # one log at a time
                with self._lock:
                    try:
                        self._update_signal.emit(message)
                    except Exception:
                        print("QT Logger errored") # don't log here with logger...

    @classmethod
    def init_qt_logger(cls, update_signal: pyqtBoundSignal):
        """
        Redirects the logger to QT widget.
        Needs to be called when GUI objects are available.
        update_signal needs str as argument.
        """
        if not cls._instance:
            raise RuntimeError
        logger = cls._instance
        qt_handler = Logger.QtLogHandler(update_signal)
        qt_handler.set_name(cls.qt_handler_name)
        log_debug_level = logging.INFO
        qt_handler.setLevel(log_debug_level)
        qt_handler.setFormatter(cls.formatter)

        logger.addHandler(qt_handler)

    @classmethod
    def remove_qt_logger(cls) -> bool:
        """ Remove qt logger (to be called before gui closes) """
        if not cls._instance:
            return True # don't care, if it is not actually there
        logger = cls._instance

        for handler in logger.handlers:
            if handler.get_name() == cls.qt_handler_name:
                logger.removeHandler(handler)
                if handler:
                    del(handler)
                return True
        return False
