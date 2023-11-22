from PySide6.QtWidgets import (QTextBrowser)

class PlainTextPasteBrowser(QTextBrowser):
    
    def insertFromMimeData(self, source):
        """ Paste text always as plain, not html """
        self.insertPlainText (source.text())
