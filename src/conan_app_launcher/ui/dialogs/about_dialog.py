from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QSizePolicy, QDialogButtonBox, QFrame, QLabel, QVBoxLayout
from PyQt5.QtGui import QIcon
from conan_app_launcher import asset_path, __version__, REPO_URL, AUTHOR


class AboutDialog(QDialog):
    """ Defines Help->About Dialog """
    html_content = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" />
    <style type="text/css"> p, li {{ white-space: pre-wrap; }} a:link {{color: #6699CC;}}</style></head>
    <body style=" font-family:'MS Shell Dlg 2'; font-weight:400; font-style:normal;">
    <p style=""><strong>Conan App Launcher {__version__}</strong></p>
    <p style="margin: 0px;">Copyright (C), 2022, {AUTHOR}.</p>
    <p style="margin: 0px;">For more information visit <a href="{REPO_URL}">{REPO_URL}</a>.</p>
    <p>Icons by <a href="https://icons8.com">https://icons8.com</a>.</p>
    </body></html>
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)

        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                            QSizePolicy.MinimumExpanding)
        self.setSizePolicy(size_policy)
        ok_button = QDialogButtonBox.Ok

        icon = QIcon(str(asset_path / "icons" / "icon.ico"))
        self._logo_label = QLabel(self)
        self._logo_label.setPixmap(icon.pixmap(100, 100))
        self._text = QLabel(self)
        self._text.setOpenExternalLinks(True)
        self._text.setSizePolicy(size_policy)
        self._text.setTextFormat(Qt.RichText)
        self._text.setText(self.html_content)
        self._text.setFrameShape(QFrame.NoFrame)

        self._button_box = QDialogButtonBox(ok_button)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._logo_label)
        layout.addWidget(self._text)
        layout.addWidget(self._button_box)
