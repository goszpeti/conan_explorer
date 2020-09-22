import logging

from PyQt5 import QtCore, QtWidgets
from conan_app_launcher.config import DEBUG_LEVEL, PROG_NAME, base_path


class QtLogHandler(logging.Handler):

    def __init__(self, widget:QtWidgets.QWidget):
        super().__init__(logging.INFO)
        self._widget = widget

    def emit(self, record):
        record = self.format(record)
        if record:
            self._widget.append('%s\n' % record)


class Logger(logging.Logger):
    """
    Singleton instance for the global dual logger (file/console)
    """
    _instance = None
    formatter = logging.Formatter(
            r"%(asctime)s :: %(levelname)s :: %(message)s")

    def __new__(cls):
        if cls._instance is None:
            # the user excepts a logger
            cls._instance = cls._init_logger()
        return cls._instance

    @classmethod
    def _init_logger(cls) -> logging.Logger:
        """ Set up format and a debug level and register loggers. """
        # restrict root logger
        root = logging.getLogger()
        root.setLevel(logging.ERROR)

        # set up file logger - log everything in file and stdio
        logger = logging.getLogger(PROG_NAME)
        logger.setLevel(logging.DEBUG)
        log_debug_level = logging.INFO
        if DEBUG_LEVEL > 0:
            log_debug_level = logging.DEBUG

        #file_handler = logging.FileHandler(
        #    str(base_path / "conan_app_launcher.log"))
        #file_handler.setLevel(log_debug_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_debug_level)

        console_handler.setFormatter(cls.formatter)
        #file_handler.setFormatter(cls.formatter)

        logger.addHandler(console_handler)
        #logger.addHandler(file_handler)

        # otherwise messages appear twice
        logger.propagate = False

        return logger

    @classmethod
    def init_qt_logger(cls, widget):
        logger = cls._instance

        qt_handler = QtLogHandler(widget)
        qt_handler.setLevel(logger.level)
        qt_handler.setFormatter(cls.formatter)
        logger.addHandler(qt_handler)