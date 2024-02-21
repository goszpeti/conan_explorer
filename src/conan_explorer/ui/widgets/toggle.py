from datetime import datetime, timedelta

from PySide6.QtCore import (Property, QEasingCurve, QPoint,  # type: ignore
                            QPointF, QPropertyAnimation, QRectF,
                            QSequentialAnimationGroup, Qt, Slot)
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QApplication, QCheckBox
from typing_extensions import override


class AnimatedToggle(QCheckBox):

    ANIM_DURATION_MS = 400
    FIXED_WIDTH = 60
    FIXED_HEIGHT = 50
    THUMB_REL_SIZE = 0.15
    TRACK_REL_SIZE = 0.4

    def __init__(self, parent=None, bar_color=Qt.GlobalColor.gray, checked_color="#00B0FF", 
                thumb_color=Qt.GlobalColor.white, pulse_unchecked_color="#44999999", pulse_checked_color="#4400B0EE"):

        super().__init__(parent)
        self._transparent_pen = QPen(Qt.GlobalColor.transparent)
        self._light_grey_pen = QPen(Qt.GlobalColor.lightGray)

        # needed for paintEvent.
        self._background_color_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._disabled_checked_brush = QBrush(QColor(bar_color).darker())
        self._thumb_brush = QBrush(thumb_color)
        self._thumb_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget.

        self.setContentsMargins(8, 0, 0, 0)
        self._thumb_position: float = 0
        self.setFixedWidth(self.FIXED_WIDTH)
        self.setFixedHeight(self.FIXED_HEIGHT)

        self.stateChanged.connect(self.thumb_state_change)

        self.thumb_anim = QPropertyAnimation(self, b"thumb_position", self)  # type: ignore
        self.thumb_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.thumb_anim.setDuration(0)  # ms

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.thumb_anim)
        self._first_show = True

    def wait_for_anim_finish(self):
        # wait so all animations can finish
        start = datetime.now()
        while datetime.now() - start <= timedelta(milliseconds=self.ANIM_DURATION_MS):
            QApplication.processEvents()

    @override
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @Property(float) # type: ignore
    def thumb_position(self):  # type: ignore
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos: float):
        self._thumb_position = pos
        self.update()

    @Slot(int)
    def thumb_state_change(self, value):
        self.animations_group.stop()
        if value:
            self.thumb_anim.setEndValue(1)
        else:
            self.thumb_anim.setEndValue(0)
        self.animations_group.start()

    @override
    def paintEvent(self, e: QPaintEvent):
        cont_rect = self.contentsRect()
        thumb_radius = round(self.THUMB_REL_SIZE * cont_rect.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Print 
        painter.setPen(self._transparent_pen)
        track_rect = QRectF(0, 0,
                          cont_rect.width() - thumb_radius,
                          self.TRACK_REL_SIZE * cont_rect.height()
        )
        track_rect.moveCenter(QPointF(cont_rect.center()))
        rounding = track_rect.height() / 2

        # the thumb will move along this line
        thumb_offset: float = (self.TRACK_REL_SIZE - (self.THUMB_REL_SIZE * 2)) * cont_rect.width()
        trail_length = cont_rect.width() + thumb_offset - 2 * thumb_radius
        x_pos = cont_rect.x() + thumb_offset +  thumb_radius + (trail_length - 3.5 * thumb_offset) * self._thumb_position
        # switch brush to reflect disabled, enabled ON, and enabled OFF states
        if not self.isEnabled():
            painter.setBrush(self._disabled_checked_brush)
            painter.drawRoundedRect(track_rect, rounding, rounding)
            painter.setBrush(self._background_color_brush)
        else:
            if self.isChecked():
                painter.setBrush(self._bar_checked_brush)
                painter.drawRoundedRect(track_rect, rounding, rounding)
                painter.setBrush(self._thumb_checked_brush)
            else:
                painter.setBrush(self._background_color_brush)
                painter.drawRoundedRect(track_rect, rounding, rounding)
                painter.setPen(self._light_grey_pen)
                painter.setBrush(self._thumb_brush)

        # fraw thumb
        painter.drawEllipse(
            QPointF(x_pos, track_rect.center().y()),
            thumb_radius, thumb_radius)

        painter.end()

        # set anim length after first show (otherwise on opening the application all toggles will slide)
        if self._first_show:
            self._first_show = False
            self.thumb_anim.setDuration(self.ANIM_DURATION_MS)  # ms
