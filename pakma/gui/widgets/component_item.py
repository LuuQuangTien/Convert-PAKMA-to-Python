"""
PakmaComponentItem & ResizeHandle — Core interactive graphical component engine for PyPAKMA.
Provides rich graphical rendering, 8-point resize handles, selection, rotation, and property bindings.
Ported & Enhanced from JPAKMA:
  - de.uniwuerzburg.physik.pakma.gui.widget.Widget
  - de.uniwuerzburg.physik.pakma.gui.widget.ResizeModifier
  - de.uniwuerzburg.physik.pakma.gui.widget.gauges.*
  - de.uniwuerzburg.physik.pakma.gui.widget.PMWidget
"""

from __future__ import annotations
import math
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem, QWidget
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QFont, 
    QLinearGradient, QRadialGradient, QCursor, QPolygonF
)


class HandlePosition:
    TOP_LEFT = 0
    TOP = 1
    TOP_RIGHT = 2
    RIGHT = 3
    BOTTOM_RIGHT = 4
    BOTTOM = 5
    BOTTOM_LEFT = 6
    LEFT = 7


class ResizeHandle(QGraphicsRectItem):
    """
    Interactive square handle positioned on corners/edges of a component for resizing.
    """
    HANDLE_SIZE = 7.0

    def __init__(self, position: int, parent: PakmaComponentItem):
        super().__init__(
            -self.HANDLE_SIZE / 2, 
            -self.HANDLE_SIZE / 2, 
            self.HANDLE_SIZE, 
            self.HANDLE_SIZE, 
            parent
        )
        self.position = position
        self.parent_item: PakmaComponentItem = parent

        self.setBrush(QBrush(QColor('#ffffff')))
        self.setPen(QPen(QColor('#0055cc'), 1.2))
        self.setZValue(100)
        self.setAcceptHoverEvents(True)

        self._set_cursor_for_position()

    def _set_cursor_for_position(self):
        cursors = {
            HandlePosition.TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
            HandlePosition.TOP: Qt.CursorShape.SizeVerCursor,
            HandlePosition.TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
            HandlePosition.RIGHT: Qt.CursorShape.SizeHorCursor,
            HandlePosition.BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
            HandlePosition.BOTTOM: Qt.CursorShape.SizeVerCursor,
            HandlePosition.BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
            HandlePosition.LEFT: Qt.CursorShape.SizeHorCursor,
        }
        self.setCursor(QCursor(cursors.get(self.position, Qt.CursorShape.ArrowCursor)))

    def update_handle_pos(self, rect: QRectF):
        """Places handle at designated coordinate along parent component boundary."""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        positions = {
            HandlePosition.TOP_LEFT: (x, y),
            HandlePosition.TOP: (x + w / 2, y),
            HandlePosition.TOP_RIGHT: (x + w, y),
            HandlePosition.RIGHT: (x + w, y + h / 2),
            HandlePosition.BOTTOM_RIGHT: (x + w, y + h),
            HandlePosition.BOTTOM: (x + w / 2, y + h),
            HandlePosition.BOTTOM_LEFT: (x, y + h),
            HandlePosition.LEFT: (x, y + h / 2),
        }
        pos = positions.get(self.position, (0, 0))
        self.setPos(pos[0], pos[1])


class PakmaComponentItem(QGraphicsRectItem):
    """
    Universal visual & interactive component for PyPAKMA.
    Supports geometric bodies, springs, vectors, gauges, controls, and physical model blocks.
    """
    MIN_WIDTH = 20.0
    MIN_HEIGHT = 15.0

    def __init__(
        self, 
        title: str, 
        widget_type: str = "rect", 
        x: float = 0, 
        y: float = 0, 
        width: float = 100, 
        height: float = 60
    ):
        super().__init__(-width / 2, -height / 2, width, height)
        self.title = title
        self.widget_type = widget_type
        self.setPos(x, y)

        # Property attributes dictionary (stored for document/model serialization & dialog)
        self.properties: Dict[str, Any] = {
            "name": title,
            "widget_type": widget_type,
            "variable_name": "",
            "expression": "",
            "value": 0.0,
            "min_val": 0.0,
            "max_val": 100.0,
            "step": 1.0,
            "unit": "",
            "fill_color": "#eef2fc",
            "border_color": "#3366cc",
            "border_width": 1.5,
            "font_size": 9,
            "locked": False,
            "grid_snap": True,
        }

        # Setup flags
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        # Setup 8 Resize Handles
        self.handles: List[ResizeHandle] = [
            ResizeHandle(i, self) for i in range(8)
        ]
        self._init_type_styles()
        self._update_handles_visibility()
        self._layout_handles()

        # Interaction tracking
        self._active_handle: Optional[ResizeHandle] = None
        self._drag_start_rect: Optional[QRectF] = None
        self._drag_start_pos: Optional[QPointF] = None

    def _init_type_styles(self):
        """Sets authentic styling defaults based on component category."""
        wt = self.widget_type
        props = self.properties

        if wt in ["pm_constant", "pm_function", "pm_accumulate", "pm_variation", "pm_measure", "pm_adopt", "pm_steer", "pm_trigger"]:
            props["fill_color"] = "#f0f4fc"
            props["border_color"] = "#2b579a"
            props["border_width"] = 1.5
        elif wt in ["spring"]:
            props["fill_color"] = "#ffffff"
            props["border_color"] = "#333333"
            props["border_width"] = 2.0
            props["variable_name"] = "k"
            props["value"] = 10.0
            props["unit"] = "N/m"
        elif wt in ["arrow", "fat_arrow", "simple_arrow", "vector", "chain_vector", "multi_vector"]:
            props["fill_color"] = "#d83b01"
            props["border_color"] = "#a80000"
            props["border_width"] = 2.0
            props["variable_name"] = "F"
            props["unit"] = "N"
        elif wt in ["anagauge", "analog_gauge"]:
            props["fill_color"] = "#fafafa"
            props["border_color"] = "#444444"
            props["border_width"] = 2.0
            props["min_val"] = -10.0
            props["max_val"] = 10.0
            props["value"] = 3.5
            props["unit"] = "V"
        elif wt in ["diggauge", "digital_gauge"]:
            props["fill_color"] = "#1e1e1e"
            props["border_color"] = "#555555"
            props["border_width"] = 1.5
            props["value"] = 12.34
            props["unit"] = "m/s"
        elif wt in ["lingauge", "linear_gauge", "thermgauge", "thermometer"]:
            props["fill_color"] = "#f7f9fa"
            props["border_color"] = "#333333"
            props["border_width"] = 1.5
            props["value"] = 25.0
            props["unit"] = "°C" if "therm" in wt else "cm"
        elif wt in ["button", "choice", "option", "scrollbar", "touchpad", "editfield", "edit"]:
            props["fill_color"] = "#f3f3f3"
            props["border_color"] = "#888888"
            props["border_width"] = 1.2
        elif wt == "oval":
            props["fill_color"] = "#e8f5e9"
            props["border_color"] = "#2e7d32"
            props["border_width"] = 1.5
            props["variable_name"] = "m"
            props["value"] = 1.0
            props["unit"] = "kg"
        else:
            props["fill_color"] = "#fdfdfd"
            props["border_color"] = "#555555"
            props["border_width"] = 1.5

    def _update_handles_visibility(self):
        show = self.isSelected() and not self.properties.get("locked", False)
        for h in self.handles:
            h.setVisible(show)

    def _layout_handles(self):
        r = self.rect()
        for h in self.handles:
            h.update_handle_pos(r)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            # Update handles on selection change
            for h in self.handles:
                h.setVisible(bool(value) and not self.properties.get("locked", False))
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if self.properties.get("locked", False):
                return self.pos()
            if self.properties.get("grid_snap", True) and isinstance(value, QPointF):
                grid = 8.0
                return QPointF(
                    round(value.x() / grid) * grid,
                    round(value.y() / grid) * grid
                )
        return super().itemChange(change, value)

    def set_custom_size(self, width: float, height: float):
        """Resizes the item centered at its current position."""
        w = max(self.MIN_WIDTH, width)
        h = max(self.MIN_HEIGHT, height)
        self.setRect(-w / 2, -h / 2, w, h)
        self._layout_handles()
        self.update()

    # --- Mouse Event Handling for 8-Point Resizing ---
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.isSelected():
            # Check if clicking on one of the resize handles
            click_pos = event.pos()
            for h in self.handles:
                if h.isVisible() and h.contains(h.mapFromParent(click_pos)):
                    self._active_handle = h
                    self._drag_start_rect = self.rect()
                    self._drag_start_pos = event.scenePos()
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self._active_handle is not None and self._drag_start_rect is not None and self._drag_start_pos is not None:
            delta = event.scenePos() - self._drag_start_pos
            r = QRectF(self._drag_start_rect)
            pos = self._active_handle.position

            # Apply delta based on handle position in local item coordinates
            dx = delta.x()
            dy = delta.y()

            if pos in [HandlePosition.TOP_LEFT, HandlePosition.LEFT, HandlePosition.BOTTOM_LEFT]:
                new_left = r.left() + dx
                if r.right() - new_left >= self.MIN_WIDTH:
                    r.setLeft(new_left)
            if pos in [HandlePosition.TOP_RIGHT, HandlePosition.RIGHT, HandlePosition.BOTTOM_RIGHT]:
                new_right = r.right() + dx
                if new_right - r.left() >= self.MIN_WIDTH:
                    r.setRight(new_right)
            if pos in [HandlePosition.TOP_LEFT, HandlePosition.TOP, HandlePosition.TOP_RIGHT]:
                new_top = r.top() + dy
                if r.bottom() - new_top >= self.MIN_HEIGHT:
                    r.setTop(new_top)
            if pos in [HandlePosition.BOTTOM_LEFT, HandlePosition.BOTTOM, HandlePosition.BOTTOM_RIGHT]:
                new_bottom = r.bottom() + dy
                if new_bottom - r.top() >= self.MIN_HEIGHT:
                    r.setBottom(new_bottom)

            self.setRect(r)
            self._layout_handles()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self._active_handle is not None:
            self._active_handle = None
            self._drag_start_rect = None
            self._drag_start_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def boundingRect(self) -> QRectF:
        """
        Bounding rect covering item body, spring labels, and 8 resize handles.
        Prevents Qt clipping artifacts and trail ghosting during movement.
        """
        r = self.rect()
        margin_x = 14.0
        margin_top = 24.0
        margin_bottom = 14.0
        return QRectF(
            r.left() - margin_x,
            r.top() - margin_top,
            r.width() + 2 * margin_x,
            r.height() + margin_top + margin_bottom
        )

    # --- Graphical Component Paint Engine ---
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = self.rect()
        wt = self.widget_type
        props = self.properties

        fill_color = QColor(props.get("fill_color", "#ffffff"))
        border_color = QColor(props.get("border_color", "#333333"))
        border_width = float(props.get("border_width", 1.5))
        font_size = int(props.get("font_size", 9))

        pen = QPen(border_color, border_width)
        brush = QBrush(fill_color)
        painter.setPen(pen)
        painter.setBrush(brush)

        # 1. Render specific widget types
        if wt == "oval":
            self._paint_oval(painter, rect, fill_color, border_color)
        elif wt == "spring":
            self._paint_spring(painter, rect, border_color)
        elif wt in ["arrow", "fat_arrow", "simple_arrow", "vector", "chain_vector", "multi_vector"]:
            self._paint_vector_arrow(painter, rect, fill_color, border_color)
        elif wt in ["anagauge", "analog_gauge"]:
            self._paint_analog_gauge(painter, rect, fill_color, border_color)
        elif wt in ["diggauge", "digital_gauge"]:
            self._paint_digital_gauge(painter, rect, fill_color, border_color)
        elif wt in ["lingauge", "linear_gauge", "thermgauge", "thermometer"]:
            self._paint_linear_gauge(painter, rect, fill_color, border_color)
        elif wt in ["button"]:
            self._paint_button(painter, rect, fill_color, border_color)
        elif wt in ["scrollbar"]:
            self._paint_scrollbar(painter, rect, fill_color, border_color)
        elif wt in ["touchpad"]:
            self._paint_touchpad(painter, rect, fill_color, border_color)
        elif wt in ["coordinate", "graph"]:
            self._paint_coordinate_graph(painter, rect, fill_color, border_color)
        elif wt in ["bar"]:
            self._paint_bar(painter, rect, fill_color, border_color)
        elif wt.startswith("pm_"):
            self._paint_pm_block(painter, rect, fill_color, border_color)
        else:
            # Default styled rounded rectangle
            painter.drawRoundedRect(rect, 4, 4)
            self._draw_standard_label(painter, rect, self.title)

        painter.restore()

    def _draw_standard_label(self, painter: QPainter, rect: QRectF, text: str, offset_y: float = 0):
        painter.setFont(QFont("Segoe UI", self.properties.get("font_size", 9), QFont.Weight.DemiBold))
        painter.setPen(QPen(QColor('#222222')))
        painter.drawText(
            rect.adjusted(4, 4 + offset_y, -4, -4 + offset_y), 
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, 
            text
        )

    def _paint_oval(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        grad = QRadialGradient(rect.center(), max(rect.width(), rect.height()) / 2)
        grad.setColorAt(0, fill.lighter(130))
        grad.setColorAt(1, fill)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(rect)
        self._draw_standard_label(painter, rect, self.title)

    def _paint_spring(self, painter: QPainter, rect: QRectF, border: QColor):
        # Draw coiled harmonic spring
        painter.setPen(QPen(border, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        w = rect.width()
        h = rect.height()
        y_mid = rect.center().y()
        left = rect.left()

        path = QPainterPath(QPointF(left, y_mid))
        path.lineTo(left + 10, y_mid)
        coils = 7
        dx = (w - 20) / (coils * 2)
        amplitude = min(h / 2 - 4, 18.0)

        for i in range(coils):
            path.lineTo(left + 10 + (2 * i + 1) * dx, y_mid - amplitude)
            path.lineTo(left + 10 + (2 * i + 2) * dx, y_mid + amplitude)
        path.lineTo(rect.right() - 10, y_mid)
        path.lineTo(rect.right(), y_mid)

        painter.drawPath(path)
        # Label above spring
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor('#333333')))
        painter.drawText(QRectF(rect.left(), rect.top() - 14, rect.width(), 16), Qt.AlignmentFlag.AlignCenter, self.title)

    def _paint_vector_arrow(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        # Draw directional vector arrow with arrowhead
        y_mid = rect.center().y()
        arrow_w = min(20.0, rect.width() * 0.3)
        shaft_h = min(12.0, rect.height() * 0.4)

        poly = QPolygonF([
            QPointF(rect.left(), y_mid - shaft_h / 2),
            QPointF(rect.right() - arrow_w, y_mid - shaft_h / 2),
            QPointF(rect.right() - arrow_w, rect.top()),
            QPointF(rect.right(), y_mid),
            QPointF(rect.right() - arrow_w, rect.bottom()),
            QPointF(rect.right() - arrow_w, y_mid + shaft_h / 2),
            QPointF(rect.left(), y_mid + shaft_h / 2),
        ])
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, fill.lighter(120))
        grad.setColorAt(1, fill)
        painter.setBrush(QBrush(grad))
        painter.drawPolygon(poly)
        self._draw_standard_label(painter, rect, self.title)

    def _paint_analog_gauge(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        # Outer gauge frame
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(rect, 6, 6)

        # Gauge dial arc
        dial_rect = rect.adjusted(6, 6, -6, -18)
        painter.setPen(QPen(QColor('#888888'), 1.5))
        painter.drawArc(dial_rect, 30 * 16, 120 * 16)

        # Scale tick marks
        cx = dial_rect.center().x()
        cy = dial_rect.bottom()
        r = min(dial_rect.width(), dial_rect.height()) * 0.8
        for i in range(7):
            ang = math.radians(150 - i * 20)
            p1 = QPointF(cx + (r - 6) * math.cos(ang), cy - (r - 6) * math.sin(ang))
            p2 = QPointF(cx + r * math.cos(ang), cy - r * math.sin(ang))
            painter.drawLine(p1, p2)

        # Needle indicator
        val = float(self.properties.get("value", 3.5))
        min_v = float(self.properties.get("min_val", -10.0))
        max_v = float(self.properties.get("max_val", 10.0))
        norm = (val - min_v) / (max_v - min_v) if max_v != min_v else 0.5
        needle_ang = math.radians(150 - norm * 120)
        p_needle = QPointF(cx + r * 0.9 * math.cos(needle_ang), cy - r * 0.9 * math.sin(needle_ang))

        painter.setPen(QPen(QColor('#d83b01'), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(cx, cy), p_needle)

        # Pivot center
        painter.setBrush(QBrush(QColor('#333333')))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 3, 3)

        # Value text at bottom
        unit = self.properties.get("unit", "V")
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor('#0055aa')))
        painter.drawText(
            QRectF(rect.left(), rect.bottom() - 16, rect.width(), 14), 
            Qt.AlignmentFlag.AlignCenter, 
            f"{val:.2f} {unit}"
        )

    def _paint_digital_gauge(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        # Bezel frame
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(rect, 4, 4)

        # LED Title & Value display
        val = float(self.properties.get("value", 0.0))
        unit = self.properties.get("unit", "")
        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor('#aaaaaa')))
        painter.drawText(QRectF(rect.left() + 4, rect.top() + 2, rect.width() - 8, 12), Qt.AlignmentFlag.AlignLeft, self.title)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QPen(QColor('#00ff66')))
        painter.drawText(
            QRectF(rect.left() + 4, rect.top() + 14, rect.width() - 8, rect.height() - 16),
            Qt.AlignmentFlag.AlignCenter,
            f"{val:6.2f} {unit}"
        )

    def _paint_linear_gauge(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(rect, 4, 4)

        # Level column
        col_rect = QRectF(rect.center().x() - 5, rect.top() + 6, 10, rect.height() - 24)
        painter.setBrush(QBrush(QColor('#e0e0e0')))
        painter.setPen(QPen(QColor('#888888'), 1))
        painter.drawRoundedRect(col_rect, 3, 3)

        # Filled mercury level
        val = float(self.properties.get("value", 25.0))
        min_v = float(self.properties.get("min_val", 0.0))
        max_v = float(self.properties.get("max_val", 100.0))
        norm = max(0.0, min(1.0, (val - min_v) / (max_v - min_v))) if max_v != min_v else 0.5
        fill_h = col_rect.height() * norm

        fill_rect = QRectF(col_rect.left(), col_rect.bottom() - fill_h, col_rect.width(), fill_h)
        painter.setBrush(QBrush(QColor('#d83b01')))
        painter.drawRoundedRect(fill_rect, 2, 2)

        # Scale tick marks
        painter.setPen(QPen(QColor('#666666'), 1))
        for i in range(5):
            ty = col_rect.top() + i * (col_rect.height() / 4)
            painter.drawLine(QPointF(col_rect.right() + 2, ty), QPointF(col_rect.right() + 7, ty))

        # Bottom label
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor('#222222')))
        painter.drawText(
            QRectF(rect.left(), rect.bottom() - 16, rect.width(), 14), 
            Qt.AlignmentFlag.AlignCenter, 
            f"{val:.1f} {self.properties.get('unit', '')}"
        )

    def _paint_button(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, fill.lighter(110))
        grad.setColorAt(1, fill.darker(110))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, 4, 4)
        self._draw_standard_label(painter, rect, f"[ {self.title} ]")

    def _paint_scrollbar(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(rect, 3, 3)

        # Track line
        y_mid = rect.center().y()
        painter.setPen(QPen(QColor('#999999'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(rect.left() + 8, y_mid), QPointF(rect.right() - 8, y_mid))

        # Slider thumb knob
        thumb_x = rect.left() + rect.width() * 0.4
        thumb_rect = QRectF(thumb_x - 6, y_mid - 9, 12, 18)
        painter.setBrush(QBrush(QColor('#0078d7')))
        painter.setPen(QPen(QColor('#004e8c'), 1.2))
        painter.drawRoundedRect(thumb_rect, 3, 3)

    def _paint_touchpad(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        painter.setBrush(QBrush(fill))
        painter.drawRoundedRect(rect, 4, 4)

        # 2D crosshair axes
        cx = rect.center().x()
        cy = rect.center().y()
        painter.setPen(QPen(QColor('#cccccc'), 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(rect.left() + 4, cy), QPointF(rect.right() - 4, cy))
        painter.drawLine(QPointF(cx, rect.top() + 4), QPointF(cx, rect.bottom() - 4))

        # 2D Joystick puck
        puck_pos = QPointF(cx + rect.width() * 0.15, cy - rect.height() * 0.15)
        painter.setBrush(QBrush(QColor('#0078d7')))
        painter.setPen(QPen(QColor('#ffffff'), 1.5))
        painter.drawEllipse(puck_pos, 5, 5)

        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor('#666666')))
        painter.drawText(QRectF(rect.left() + 4, rect.bottom() - 14, rect.width() - 8, 12), Qt.AlignmentFlag.AlignRight, "2D Pad")

    def _paint_coordinate_graph(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        painter.setBrush(QBrush(QColor('#ffffff')))
        painter.drawRoundedRect(rect, 4, 4)

        # Grid lines
        painter.setPen(QPen(QColor('#eeeeee'), 1))
        for i in range(1, 4):
            x = rect.left() + i * (rect.width() / 4)
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            y = rect.top() + i * (rect.height() / 4)
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        # Axis
        painter.setPen(QPen(QColor('#888888'), 1.5))
        cy = rect.center().y()
        painter.drawLine(QPointF(rect.left() + 4, cy), QPointF(rect.right() - 4, cy))
        painter.drawLine(QPointF(rect.left() + 8, rect.top() + 4), QPointF(rect.left() + 8, rect.bottom() - 4))

        # Sample sine wave
        path = QPainterPath()
        p0 = QPointF(rect.left() + 8, cy)
        path.moveTo(p0)
        steps = 20
        for s in range(steps + 1):
            px = rect.left() + 8 + s * (rect.width() - 16) / steps
            py = cy - math.sin(s * 2 * math.pi / steps) * (rect.height() * 0.35)
            path.lineTo(px, py)
        painter.setPen(QPen(QColor('#0078d7'), 1.5))
        painter.drawPath(path)

    def _paint_bar(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        painter.setBrush(QBrush(QColor('#f0f0f0')))
        painter.drawRoundedRect(rect, 3, 3)

        # Progress fill
        fill_w = rect.width() * 0.65
        fill_rect = QRectF(rect.left(), rect.top(), fill_w, rect.height())
        grad = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
        grad.setColorAt(0, QColor('#0078d7'))
        grad.setColorAt(1, QColor('#0055aa'))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(fill_rect, 3, 3)
        self._draw_standard_label(painter, rect, self.title)

    def _paint_pm_block(self, painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
        # Header banner
        header_rect = QRectF(rect.left(), rect.top(), rect.width(), 16)
        painter.setBrush(QBrush(border))
        painter.drawRoundedRect(rect, 4, 4)

        # Body
        body_rect = QRectF(rect.left() + 1, rect.top() + 16, rect.width() - 2, rect.height() - 17)
        painter.setBrush(QBrush(fill))
        painter.drawRect(body_rect)

        # Header Title
        type_titles = {
            "pm_constant": "CONSTANT",
            "pm_function": "FUNCTION",
            "pm_accumulate": "INTEGRATOR",
            "pm_variation": "VARIATION",
            "pm_measure": "MEASURE",
            "pm_adopt": "ADOPT",
            "pm_steer": "STEER",
            "pm_trigger": "TRIGGER",
        }
        tag = type_titles.get(self.widget_type, "PM BLOCK")
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.setPen(QPen(QColor('#ffffff')))
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignCenter, tag)

        # Body Content
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.setPen(QPen(QColor('#222222')))
        painter.drawText(body_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.title)

        # Ports (Input on Left, Output on Right)
        painter.setBrush(QBrush(QColor('#ffffff')))
        painter.setPen(QPen(border, 1.2))
        painter.drawEllipse(QPointF(rect.left(), rect.center().y()), 3.5, 3.5)
        painter.drawEllipse(QPointF(rect.right(), rect.center().y()), 3.5, 3.5)
