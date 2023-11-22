import logging
from threading import Lock

from conan_explorer import CONAN_LOG_PREFIX
from conan_explorer.app.logger import Logger
from PySide6.QtCore import SignalInstance


class QtLogHandler(logging.Handler):
    """
    This log handler sends a logger string to a qt widget.
    update_signal needs str as argument.
    """
    _lock = Lock()
    _formatter = logging.Formatter(r"%(levelname)s: %(message)s")

    def __init__(self, update_signal: SignalInstance):
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
                    print("QT Logger errored")  # don't log here with logger...


def init_qt_logger(logger: Logger, name: str, update_signal: SignalInstance):
    """Redirects the logger to QT widget.
    Needs to be called when GUI objects are available.
    update_signal needs str as argument.
    """
    qt_handler = QtLogHandler(update_signal)
    qt_handler.set_name(name)
    log_debug_level = logging.INFO
    qt_handler.setLevel(log_debug_level)
    qt_handler.setFormatter(qt_handler._formatter)

    logger.addHandler(qt_handler)


def remove_qt_logger(logger: Logger, name: str) -> bool:
    """ Remove qt logger (to be called before gui closes) """
    for handler in logger.handlers:
        if handler.get_name() == name:
            logger.removeHandler(handler)
            if handler:
                del(handler)
            return True
    return False
