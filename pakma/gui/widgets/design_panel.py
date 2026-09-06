"""
DesignPanel & Widget Canvas for PyPAKMA matching original JPAKMA DesignPanel.
"""

from __future__ import annotations
import math
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont


class ConnectionWire(QGraphicsPathItem):
    """Effect Arrow / Wire connecting PM nodes."""
    def __init__(self, start_item, end_item, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.setPen(QPen(QColor('#0055aa'), 2, Qt.PenStyle.SolidLine))
        self.setZValue(-1)
        self.update_path()

    def update_path(self):
        if not self.start_item or not self.end_item:
            return
        p1 = self.start_item.scenePos()
        p2 = self.end_item.scenePos()

        path = QPainterPath(p1)
        dx = (p2.x() - p1.x()) * 0.5
        c1 = QPointF(p1.x() + dx, p1.y())
        c2 = QPointF(p2.x() - dx, p2.y())
        path.cubicTo(c1, c2, p2)
        self.setPath(path)


class JPAKMAWidgetNode(QGraphicsRectItem):
    """Visual movable widget matching JPAKMA graphical & physical model widgets."""
    def __init__(self, title: str, widget_type: str = "rect", x: float = 0, y: float = 0):
        super().__init__(-50, -25, 100, 50)
        self.title = title
        self.widget_type = widget_type
        self.setPos(x, y)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Style based on widget type
        if widget_type in ["pm_constant", "pm_function", "pm_accumulate", "pm_measure"]:
            self.setBrush(QBrush(QColor('#eef2fc')))
            self.setPen(QPen(QColor('#3366cc'), 1.5))
        elif widget_type == "spring":
            self.setBrush(QBrush(QColor('#ffffff')))
            self.setPen(QPen(QColor('#555555'), 1.5))
        elif widget_type == "oval":
            self.setBrush(QBrush(QColor('#e8f5e9')))
            self.setPen(QPen(QColor('#2e7d32'), 1.5))
        else:
            self.setBrush(QBrush(QColor('#f8f8f8')))
            self.setPen(QPen(QColor('#666677'), 1))

        # Title Label
        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setFont(QFont("Segoe UI", 9))
        self.title_item.setDefaultTextColor(QColor('#222222'))
        self.title_item.setPos(-45, -15)

    def paint(self, painter: QPainter, option, widget=None):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.widget_type == "oval":
            painter.setBrush(self.brush())
            painter.setPen(self.pen())
            painter.drawEllipse(self.rect())
        elif self.widget_type == "spring":
            painter.setPen(QPen(QColor('#333333'), 2))
            # Draw coil spring
            r = self.rect()
            w = r.width()
            y_mid = r.center().y()
            path = QPainterPath(QPointF(r.left(), y_mid))
            coils = 6
            dx = w / (coils * 2)
            for i in range(coils):
                path.lineTo(r.left() + (2*i + 1)*dx, r.top() + 5)
                path.lineTo(r.left() + (2*i + 2)*dx, r.bottom() - 5)
            path.lineTo(r.right(), y_mid)
            painter.drawPath(path)
        else:
            painter.setBrush(self.brush())
            painter.setPen(self.pen())
            painter.drawRoundedRect(self.rect(), 4, 4)

        painter.restore()
        super().paint(painter, option, widget)


class DesignPanel(QGraphicsView):
    """
    DesignPanel — White canvas supporting grid snap, zoom, and interactive JPAKMA widgets.
    (Ported from de.uniwuerzburg.physik.pakma.gui.widget.DesignPanel)
    """
    def __init__(self, mode: str = "GR", parent=None):
        super().__init__(parent)
        self.mode = mode  # "GR" (GraphView) or "PM" (PMView)
        self.grid_enabled = True
        self.grid_size = 16

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.setScene(self.scene)

        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QBrush(QColor('#ffffff')))
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.widgets: list[JPAKMAWidgetNode] = []

    def toggle_grid(self, enabled: bool | None = None):
        if enabled is None:
            self.grid_enabled = not self.grid_enabled
        else:
            self.grid_enabled = enabled
        self.viewport().update()

    def clear_canvas(self):
        self.scene.clear()
        self.widgets.clear()

    def add_widget_item(self, title: str, widget_type: str, x: float = 0, y: float = 0) -> JPAKMAWidgetNode:
        node = JPAKMAWidgetNode(title, widget_type, x, y)
        self.scene.addItem(node)
        self.widgets.append(node)
        return node

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        if not self.grid_enabled:
            return

        painter.save()
        pen = QPen(QColor('#e0e0ea'), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        for x in range(left, int(rect.right()), self.grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), self.grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

        painter.restore()
