from typing import Union, Literal
import conan_explorer.app as app
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


from conan_explorer.settings import GUI_MODE, GUI_MODE_DARK
class ConfigHighlighter(QSyntaxHighlighter):
    """ 
    Syntax highlighting for Conan Cinfig files: ini and yaml.
    Support dark and light mode.
    """

    def __init__(self, parent, type: Union[Literal["ini"], Literal["yaml"]]) -> None:
        super().__init__(parent)
        self._type = type
        if app.active_settings.get(GUI_MODE) == GUI_MODE_DARK:
            self.key_color = "#9BDCFE"
            self.value_color = "#CE9178"
            self.section_color = "#50C9B1"
        else: 
            self.section_color = "#257F99"
            self.key_color = "#001EFD"
            self.value_color = "#AC1613"
        self.comment_color = "#6B9857"

        # key value constants
        if type == "ini":
            self._separator = "="
            self._key_regex = r"(.*?)(?=\=)"
            self._value_regex = r"(?<=\=)(.*?)$"
        elif type == "yaml":
            self._separator = ":"
            self._key_regex ="(.*?)(?=:)"
            self._value_regex = "(?<=:)(.*?)$"

    def highlightBlock(self, text: str):
        # set default value color for everything
        # modify every other construct with special cases
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(self.value_color))
        if self._separator not in text:
            self.setFormat(0, len(text), value_format)
        else:
            expression = QRegularExpression(self._value_regex)
            match = expression.match(text)
            self.setFormat(match.capturedStart(), match.capturedLength(), value_format)

        # sections
        if self._type == "ini":
            section_format = QTextCharFormat()
            section_format.setFontWeight(QFont.Weight.Bold)
            section_format.setForeground(QColor(self.section_color))
            expression = QRegularExpression(r"\[(.*?)\]")
            i = expression.globalMatch(text)
            while i.hasNext():
                match = i.next()
                self.setFormat(match.capturedStart(), 
                               match.capturedLength(), section_format)
        # key-values
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(self.key_color))
        expression = QRegularExpression(self._key_regex)
        match = expression.match(text)
        self.setFormat(match.capturedStart(), match.capturedLength(), key_format)

        # comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.comment_color))
        expression = QRegularExpression(r"#(?:\s.*?)$")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), 
                           match.capturedLength(), comment_format)
