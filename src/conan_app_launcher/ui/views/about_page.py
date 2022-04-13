from conan_app_launcher import AUTHOR, REPO_URL, __version__, asset_path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QFrame, QLabel, QSizePolicy, QSpacerItem,
                             QVBoxLayout, QWidget)


class AboutPage(QWidget):
    """ Defines About page """
    html_content = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" />
    <style type="text/css"> p, li {{ white-space: pre-wrap; }} a:link {{color: #6699CC;}}</style></head>
    <body style="font-weight:400; font-style:normal;">
        <p style="font-size:18pt"><strong>Conan App Launcher {__version__}</strong></p>
        <p style="margin: 0px;">Copyright (C), 2022, {AUTHOR}.</p>
        <p style="margin: 0px;">For more information visit <a href="{REPO_URL}">{REPO_URL}</a>.</p>
        <p>Icons by <a href="https://icons8.com">https://icons8.com</a>.</p>
        <p></p>
    </body>
    </html>
    """

    def __init__(self, parent):
        super().__init__(parent)
        icon = QIcon(str(asset_path / "icons" / "icon.ico"))
        self._logo_label = QLabel(self)
        self._logo_label.setPixmap(icon.pixmap(100, 100))
        self._text = QLabel(self)
        self._text.setObjectName("about_label")
        self._text.setOpenExternalLinks(True)
        self._text.setTextFormat(Qt.RichText)
        self._text.setText(self.html_content)
        self._text.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.addWidget(self._logo_label)
        layout.addWidget(self._text)
        layout.addItem(QSpacerItem(
            20, 600, QSizePolicy.Minimum, QSizePolicy.Expanding))
