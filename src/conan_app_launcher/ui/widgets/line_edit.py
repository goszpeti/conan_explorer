import conan_app_launcher as this
from threading import Thread
from conan_app_launcher.components.conan import ConanApi
from conans.model.ref import ConanFileReference

from PyQt5 import QtCore, QtWidgets, QtGui
Qt = QtCore.Qt


class LineEdit(QtWidgets.QLineEdit):
    completion_finished = QtCore.pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        completer = QtWidgets.QCompleter([], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._validator = QtGui.QRegExpValidator(self)
        self._validator_thread = None
        # setup range
        part_regex = r"[a-zA-Z0-9_][a-zA-Z0-9_\+\.-]{1,50}"
        recipe_regex = f"{part_regex}/{part_regex}(@{part_regex}/{part_regex})?"
        self._validator.setRegExp(QtCore.QRegExp(recipe_regex))
        self.setCompleter(completer)
        self.textChanged.connect(self.validate_text)

    def validate_text(self, text):
        if self._validator.validate(text, 0)[0] < self._validator.Acceptable:
            self.setStyleSheet("background: LightCoral;")
        else:
            self.setStyleSheet("background: PaleGreen;")
            return
        
        cache_results = this.cache.search(text)
        self.completer().model().setStringList(cache_results)
        if not any([entry.startswith(text) for entry in cache_results]):
            # add label with spinner?
            if self._validator_thread and self._validator_thread.is_alive(): # one query at a time
                return
            self._validator_thread = Thread(target=self.load_completion, args=[text, ])
            self._validator_thread.start()

    def load_completion(self, text):
        conan = ConanApi()
        recipes = conan.search_query_in_remotes(f"{text}*")
        this.cache.update_remote_package_list(recipes)  # add to cache

