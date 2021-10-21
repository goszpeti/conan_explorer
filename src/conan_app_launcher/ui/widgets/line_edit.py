import conan_app_launcher as this
from threading import Thread
from conan_app_launcher.components.conan import ConanApi
from conans.model.ref import ConanFileReference

from PyQt5 import QtCore, QtWidgets, QtGui
Qt = QtCore.Qt


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        conan_list = ["Loading from remotes..."]
        completer = QtWidgets.QCompleter(conan_list, self)
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

        cache_results = this.cache.search_in_remote_refs(text)
        cache_results_str = [str(entry) for entry in cache_results]
        self.completer().model().setStringList(cache_results_str)
        if not any([entry.startswith(text) for entry in cache_results_str]):
            # add label with spinner
            self._validator_thread = Thread(target=self.load_completion, args=[text, ])
            self._validator_thread.start()

    def load_completion(self, text):
        conan = ConanApi()
        recipes = conan.search_query_in_remotes(f"{text}*")
        recipes_str = [str(entry) for entry in recipes]
        self.completer().model().setStringList(recipes_str)
        this.cache.update_remote_package_list(recipes)  # add to cache
