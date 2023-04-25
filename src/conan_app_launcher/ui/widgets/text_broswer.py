# void QTextEdit::insertFromMimeData ( const QMimeData * source )
# {
#          void QTextEdit::insertPlainText ( source->text() );
# }

from PySide6.QtCore import Qt, SignalInstance, QObject
from PySide6.QtWidgets import (QApplication, QTreeView, QPushButton, QTextBrowser, QListWidget)

class PlainTextPasteBrowser(QTextBrowser):
    
    def insertFromMimeData(self, source):
        """ Paste text always as plain, not html """
        self.insertPlainText (source.text())
