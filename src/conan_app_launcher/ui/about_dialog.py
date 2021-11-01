from PyQt5 import QtWidgets, QtGui
import conan_app_launcher as this


class AboutDialog(QtWidgets.QDialog):
    """ Defines Help->About Dialog """
    html_content = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; }
    </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:10pt; font-weight:400; font-style:normal;">
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt;">Conan App Launcher ${version}</span></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt;">Copyright (C), 2021, Péter Gosztolya and contributors.</span></p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="https://github.com/goszpeti/conan_app_launcher"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">https://github.com/goszpeti/conan_app_launcher</span></a></p>
    <p style=" margin-top:8px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Icons by <a href="https://icons8.com"><span style=" text-decoration: underline; color:#0000ff;">https://icons8.com</span></a>.</p></body></html>
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        self.resize(430, 280)
        ok_button = QtWidgets.QDialogButtonBox.Ok

        icon = QtGui.QIcon(str(this.asset_path / "icons" / "icon.ico"))
        self._logo_label = QtWidgets.QLabel(self)
        self._logo_label.setPixmap(icon.pixmap(100, 100))
        self._text = QtWidgets.QTextBrowser(self)
        self._text.setOpenExternalLinks(True)
        self._text.setStyleSheet("background-color: #F0F0F0;")
        self._text.setHtml(self.html_content.replace("${version}", this.__version__))
        self._text.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._button_box = QtWidgets.QDialogButtonBox(ok_button)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._logo_label)
        layout.addWidget(self._text)
        layout.addWidget(self._button_box)
        self.setLayout(layout)
