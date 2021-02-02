from PyQt5 import QtCore, QtWidgets, QtGui
Qt = QtCore.Qt


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        conan_list = ["myapp/1.0.0@abc/stable", "abc/1.0.0@a/stable"]
        completer = QtWidgets.QCompleter(conan_list, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._validator = QtGui.QRegExpValidator(self)
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
