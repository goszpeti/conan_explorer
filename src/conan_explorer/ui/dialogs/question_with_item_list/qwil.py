from typing import Optional

from PySide6.QtWidgets import QDialog, QStyle, QWidget


class QuestionWithItemListDialog(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget],
        icon: QStyle.StandardPixmap = QStyle.StandardPixmap.SP_MessageBoxQuestion,
    ) -> None:
        super().__init__(parent)
        from .qwil_ui import Ui_Dialog

        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        std_icon = self.style().standardIcon(icon)
        self._ui.icon.setPixmap(std_icon.pixmap(40, 40))
        self.button_box = self._ui.button_box
        self.item_list_widget = self._ui.list_widget

    def set_question_text(self, text: str):
        self._ui.question_label.setText(text)
