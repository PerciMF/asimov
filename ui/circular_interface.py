import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget


class CircularInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)

        self.angle = 0
        self.main_text = "ASIMOV"
        self.sub_text = "ONLINE"
        self.energy_level = 100
        self.status_color = QColor("#00E5FF")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    def animate(self) -> None:
        self.angle = (self.angle + 2) % 360
        self.update()

    def set_state(self, state: str) -> None:
        state_upper = state.upper()

        mapping = {
            "ONLINE": {"sub_text": "SISTEMA ONLINE", "color": "#00E5FF", "energy": 100},
            "OCIOSA": {"sub_text": "AGUARDANDO", "color": "#81C784", "energy": 88},
            "PROCESSANDO": {"sub_text": "ANALISANDO", "color": "#FFD54F", "energy": 72},
            "AJUDA": {"sub_text": "MODO SUPORTE", "color": "#64B5F6", "energy": 91},
            "ERRO": {"sub_text": "FALHA DETECTADA", "color": "#EF5350", "energy": 35},
            "RESET": {"sub_text": "REINICIALIZANDO", "color": "#BA68C8", "energy": 60},
        }

        config = mapping.get(state_upper, mapping["ONLINE"])
        self.main_text = "ASIMOV"
        self.sub_text = config["sub_text"]
        self.status_color = QColor(config["color"])
        self.energy_level = config["energy"]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, QColor("#10161F"))

        center = rect.center()
        size = min(rect.width(), rect.height()) - 40
        radius = size / 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(18, 28, 40, 180))
        painter.drawEllipse(center, radius, radius)

        pen_outer = QPen(self.status_color, 2)
        painter.setPen(pen_outer)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius - 10, radius - 10)

        pen_mid = QPen(QColor("#90CAF9"), 1)
        painter.setPen(pen_mid)
        painter.drawEllipse(center, radius - 35, radius - 35)

        pen_arc = QPen(self.status_color, 6)
        painter.setPen(pen_arc)
        arc_rect = QRectF(
            center.x() - (radius - 55),
            center.y() - (radius - 55),
            2 * (radius - 55),
            2 * (radius - 55),
        )
        painter.drawArc(arc_rect, (90 - self.angle) * 16, 110 * 16)

        pen_arc2 = QPen(QColor("#29B6F6"), 3)
        painter.setPen(pen_arc2)
        arc_rect2 = QRectF(
            center.x() - (radius - 75),
            center.y() - (radius - 75),
            2 * (radius - 75),
   import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget


class CircularInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)

        self.angle = 0
        self.main_text = "ASIMOV"
        self.sub_text = "ONLINE"
        self.energy_level = 100
        self.status_color = QColor("#00E5FF")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    def animate(self) -> None:
        self.angle = (self.angle + 2) % 360
        self.update()

    def set_state(self, state: str) -> None:
        state_upper = state.upper()

        mapping = {
            "ONLINE": {"sub_text": "SISTEMA ONLINE", "color": "#00E5FF", "energy": 100},
            "OCIOSA": {"sub_text": "AGUARDANDO", "color": "#81C784", "energy": 88},
            "PROCESSANDO": {"sub_text": "ANALISANDO", "color": "#FFD54F", "energy": 72},
            "AJUDA": {"sub_text": "MODO SUPORTE", "color": "#64B5F6", "energy": 91},
            "ERRO": {"sub_text": "FALHA DETECTADA", "color": "#EF5350", "energy": 35},
            "RESET": {"sub_text": "REINICIALIZANDO", "color": "#BA68C8", "energy": 60},
        }

        config = mapping.get(state_upper, mapping["ONLINE"])
        self.main_text = "ASIMOV"
        self.sub_text = config["sub_text"]
        self.status_color = QColor(config["color"])
        self.energy_level = config["energy"]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, QColor("#10161F"))

        center = rect.center()
        size = min(rect.width(), rect.height()) - 40
        radius = size / 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(18, 28, 40, 180))
        painter.drawEllipse(center, radius, radius)

        pen_outer = QPen(self.status_color, 2)
        painter.setPen(pen_outer)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius - 10, radius - 10)

        pen_mid = QPen(QColor("#90CAF9"), 1)
        painter.setPen(pen_mid)
        painter.drawEllipse(center, radius - 35, radius - 35)

        pen_arc = QPen(self.status_color, 6)
        painter.setPen(pen_arc)
        arc_rect = QRectF(
            center.x() - (radius - 55),
            center.y() - (radius - 55),
            2 * (radius - 55),
            2 * (radius - 55),
        )
        painter.drawArc(arc_rect, (90 - self.angle) * 16, 110 * 16)

        pen_arc2 = QPen(QColor("#29B6F6"), 3)
        painter.setPen(pen_arc2)
        arc_rect2 = QRectF(
            center.x() - (radius - 75),
            center.y() - (radius - 75),
            2 * (radius - 75),
            2 * (radius - 75),
        )
        painter.drawArc(arc_rect2, (220 + self.angle) * 16, 70 * 16)

        marker_radius = radius - 8
        painter.setBrush(self.status_color)
        painter.setPen(Qt.NoPen)

        for i in range(8):
            ang = math.radians((360 / 8) * i + self.angle)
            x = center.x() + math.cos(ang) * marker_radius
            y = center.y() + math.sin(ang) * marker_radius
            painter.drawEllipse(QPointF(x, y), 4, 4)

        painter.setBrush(QColor(10, 20, 30, 220))
        painter.setPen(QPen(self.status_color, 2))
        painter.drawEllipse(center, radius - 95, radius - 95)

        painter.setPen(QColor("#E3F2FD"))
        font_main = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font_main)
        text_rect = QRectF(center.x() - 120, center.y() - 30, 240, 40)
        painter.drawText(text_rect, Qt.AlignCenter, self.main_text)

        font_sub = QFont("Segoe UI", 10)
        painter.setFont(font_sub)
        sub_rect = QRectF(center.x() - 120, center.y() + 10, 240, 30)
        painter.drawText(sub_rect, Qt.AlignCenter, self.sub_text)

        energy_rect = QRectF(center.x() - 120, center.y() + 38, 240, 25)
        painter.drawText(energy_rect, Qt.AlignCenter, f"NÚCLEO: {self.energy_level}%")
         2 * (radius - 75),
        )
        painter.drawArc(arc_rect2, (220 + self.angle) * 16, 70 * 16)

        marker_radius = radius - 8
        painter.setBrush(self.status_color)
        painter.setPen(Qt.NoPen)

        for i in range(8):
            ang = math.radians((360 / 8) * i + self.angle)
            x = center.x() + math.cos(ang) * marker_radius
            y = center.y() + math.sin(ang) * marker_radius
            painter.drawEllipse(QPointF(x, y), 4, 4)

        painter.setBrush(QColor(10, 20, 30, 220))
        painter.setPen(QPen(self.status_color, 2))
        painter.drawEllipse(center, radius - 95, radius - 95)

        painter.setPen(QColor("#E3F2FD"))
        font_main = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font_main)
        text_rect = QRectF(center.x() - 120, center.y() - 30, 240, 40)
        painter.drawText(text_rect, Qt.AlignCenter, self.main_text)

        font_sub = QFont("Segoe UI", 10)
        painter.setFont(font_sub)
        sub_rect = QRectF(center.x() - 120, center.y() + 10, 240, 30)
        painter.drawText(sub_rect, Qt.AlignCenter, self.sub_text)

        energy_rect = QRectF(center.x() - 120, center.y() + 38, 240, 25)
        painter.drawText(energy_rect, Qt.AlignCenter, f"NÚCLEO: {self.energy_level}%")
