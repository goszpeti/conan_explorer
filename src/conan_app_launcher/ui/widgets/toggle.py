from datetime import datetime, timedelta
from gc import isenabled
from PySide6.QtCore import (QEasingCurve, QPoint, QPointF, QPropertyAnimation,
                          QRectF, QSequentialAnimationGroup, QSize, Qt, 
                          Property, Slot) # type: ignore
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QCheckBox, QApplication


class AnimatedToggle(QCheckBox):

    ANIM_DURATION_MS = 600
    MAX_WIDTH = 65
    MAX_HEIGHT = 55
    def __init__(self, parent=None, bar_color=Qt.GlobalColor.gray, checked_color="#00B0FF", 
                handle_color=Qt.GlobalColor.white, pulse_unchecked_color="#44999999", pulse_checked_color="#4400B0EE"):

        super().__init__(parent)
        self._transparent_pen = QPen(Qt.GlobalColor.transparent)
        self._light_grey_pen = QPen(Qt.GlobalColor.lightGray)

        # needed for paintEvent.
        self._background_color_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._disabled_checked_brush = QBrush(QColor(bar_color).darker())
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget.

        self.setContentsMargins(8, 0, 0, 0)
        self._handle_position = 0
        self.setMaximumWidth(self.MAX_WIDTH+ 20)
        self.setFixedWidth(self.MAX_WIDTH)
        self.setFixedHeight(self.MAX_HEIGHT)

        self.stateChanged.connect(self.handle_state_change)

        self.handle_anim = QPropertyAnimation(self, b"handle_position", self)  # type: ignore
        self.handle_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.handle_anim.setDuration(0)  # ms
        self.handle_anim.finished.connect(self._set_anim_length)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.handle_anim)
        self._first_show = True

    def _set_anim_length(self):
        if self._first_show:
            self._first_show = False
            self.handle_anim.setDuration(self.ANIM_DURATION_MS)  # ms
            return

    def wait_for_anim_finish(self):
        # wait so all animations can finish
        start = datetime.now()
        while datetime.now() - start <= timedelta(milliseconds=self.ANIM_DURATION_MS):
            QApplication.processEvents()

    def sizeHint(self):
        return QSize(self.MAX_WIDTH, self.MAX_HEIGHT)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @Property(float)
    def handle_position(self):  # type: ignore
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()

    @Slot(int)
    def handle_state_change(self, value):

        self.animations_group.stop()
        if value:
            self.handle_anim.setEndValue(1)
        else:
            self.handle_anim.setEndValue(0)
        self.animations_group.start()

    def paintEvent(self, e: QPaintEvent):

        cont_rect = self.contentsRect()
        handle_radius = round(0.2* cont_rect.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(self._transparent_pen)
        bar_rect = QRectF(0, 0,
            cont_rect.width() - handle_radius, 0.40 * cont_rect.height()
        )
        bar_rect.moveCenter(QPointF(cont_rect.center()))
        rounding = bar_rect.height() / 2

        # the handle will move along this line
        trail_length = cont_rect.width() - 2 * handle_radius

        x_pos = cont_rect.x() + handle_radius + trail_length * self._handle_position

        if not self.isEnabled():
            painter.setBrush(self._disabled_checked_brush)
            painter.drawRoundedRect(bar_rect, rounding, rounding)
            painter.setBrush(self._background_color_brush)
        else:
            if self.isChecked():
                painter.setBrush(self._bar_checked_brush)
                painter.drawRoundedRect(bar_rect, rounding, rounding)
                painter.setBrush(self._handle_checked_brush)
            else:
                painter.setBrush(self._background_color_brush)
                painter.drawRoundedRect(bar_rect, rounding, rounding)
                painter.setPen(self._light_grey_pen)
                painter.setBrush(self._handle_brush)

        painter.drawEllipse(
            QPointF(x_pos, bar_rect.center().y()),
            handle_radius, handle_radius)

        painter.end()
