from PyQt5 import QtWidgets, QtGui, QtCore
from conan_app_launcher import asset_path, __version__, REPO_URL, AUTHOR

class AboutDialog(QtWidgets.QDialog):
    """ Defines Help->About Dialog """
    html_content = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" />
    <style type="text/css"> p, li {{ white-space: pre-wrap; }}</style></head>
    <body style=" font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;">
    <p style=""><strong>Conan App Launcher {__version__}</strong></p>
    <p style="margin: 0px;">Copyright (C), 2021, {AUTHOR}.</p>
    <p style="margin: 0px;">For more information visit <a href="{REPO_URL}">{REPO_URL}</a>.</p>
    <p>Icons by <a href="https://icons8.com"><span style="text-decoration: underline; color:#0000ff;">https://icons8.com</span></a>.</p>
    </body></html>
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.MinimumExpanding)
        self.setSizePolicy(size_policy)
        ok_button = QtWidgets.QDialogButtonBox.Ok

        icon = QtGui.QIcon(str(asset_path / "icons" / "icon.ico"))
        self._logo_label = QtWidgets.QLabel(self)
        self._logo_label.setPixmap(icon.pixmap(100, 100))
        self._text = QtWidgets.QLabel(self)
        self._text.setOpenExternalLinks(True)
        self._text.setSizePolicy(size_policy)
        self._text.setTextFormat(QtCore.Qt.RichText)
        self._text.setStyleSheet("background-color: #F0F0F0;")
        self._text.setText(self.html_content)
        self._text.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._button_box = QtWidgets.QDialogButtonBox(ok_button)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._logo_label)
        layout.addWidget(self._text)
        layout.addWidget(self._button_box)
