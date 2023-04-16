from typing import TYPE_CHECKING, Union
import conan_app_launcher.app as app
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor

if TYPE_CHECKING:
    from typing import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal

from conan_app_launcher.settings import GUI_MODE, GUI_MODE_DARK
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
        if type == "ini":
            self._separator = "="
            self._key_regex = "(.*?)(?=\=)"
            self._value_regex = "(?<=\=)(.*?)$" # ((.|\n)*)(?=\=)            
        elif type == "yaml":
            self._separator = ":"
            self._key_regex ="(.*?)(?=:)"
            self._value_regex = "(?<=:)(.*?)$"

    def highlightBlock(self, text: str):
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(self.value_color))
        if not self._separator in text:
            self.setFormat(0, len(text), value_format)
        else:
            expression = QRegularExpression(self._value_regex)
            i = expression.globalMatch(text)
            while i.hasNext():
                match = i.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), value_format)

        if self._type == "ini":
            section_format = QTextCharFormat()
            section_format.setFontWeight(QFont.Weight.Bold)
            section_format.setForeground(QColor(self.section_color))
            expression = QRegularExpression("\[(.*?)\]")
            i = expression.globalMatch(text)
            while i.hasNext():
                match = i.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), section_format)

        key_format = QTextCharFormat()
        key_format.setForeground(QColor(self.key_color))
        expression = QRegularExpression(self._key_regex)
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), key_format)

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.comment_color))
        expression = QRegularExpression("#(?:\s.*?)$")
        i = expression.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), comment_format)
