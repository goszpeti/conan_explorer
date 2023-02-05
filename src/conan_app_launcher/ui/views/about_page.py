from conan_app_launcher import APP_NAME, AUTHOR, REPO_URL, __version__, asset_path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFrame, QLabel, QSizePolicy, QSpacerItem,
                             QVBoxLayout)
from conan_app_launcher.ui.fluent_window.plugins import ThemedWidget


class AboutPage(ThemedWidget):
    """ Defines About page """
    html_content = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" />
    <style type="text/css"> p, li {{ white-space: pre-wrap; }} a:link {{color: #6699CC;}}</style></head>
    <body style="font-weight:400; font-style:normal;">
        <p style="font-size:18pt"><strong>{APP_NAME} {__version__}</strong></p>
        <p style="margin: 0px;">Copyright (C), 2023, {AUTHOR}.</p>
        <p style="margin: 0px;">Licensed under LGPL v3.</p>
        <p></p>
        <p style="margin: 0px;">Powered by Qt6 via PySide6 bindings under LGPL v3 license.</p>
        <p>Assets:</p>
        <ul>
            <li>Material icons by Google (https://fonts.google.com/) under Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0)</li>
            <li>Fluent icons by Microsoft (https://www.svgrepo.com/collection/fluent-ui-icons-outlined/) under MIT License (https://opensource.org/licenses/MIT)</li>
            <li>Linux icon by Carbon Design (https://www.svgrepo.com/svg/340563/linux-alt) under Apache License https://opensource.org/licenses/Apache-1.1</li>
            <li>Apple icon by Klever Space (https://www.svgrepo.com/svg/488495/apple) under MIT License</li>
            <li>Windows icon by Klever Space (https://www.svgrepo.com/svg/488736/windows) under MIT License</li>
            <li>Package icon by Neuicons (https://www.svgrepo.com/svg/487645/package) under MIT License</li>
            <li>Open Box icon by wishforge.games (https://www.svgrepo.com/svg/488736/windows) under CC Attribution License (https://creativecommons.org/licenses/by/4.0/legalcode)</li>
        </ul>
        <p style="margin: 0px;">For more information visit <a href="{REPO_URL}">{REPO_URL}</a>.</p>
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
        self._text.setTextFormat(Qt.TextFormat.RichText)
        self._text.setText(self.html_content)
        self._text.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.addWidget(self._logo_label)
        layout.addWidget(self._text)
        layout.addItem(QSpacerItem(
            20, 600, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


