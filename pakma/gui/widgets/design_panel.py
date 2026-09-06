"""
DesignPanel & Widget Canvas for PyPAKMA matching original JPAKMA DesignPanel.
Supports 8-point resizing, tool placement, grid snap, Z-order, middle-mouse workspace panning,
zoom, and rich context menus.
Ported from:
  - de.uniwuerzburg.physik.pakma.gui.widget.DesignPanel
  - de.uniwuerzburg.physik.pakma.gui.widget.WidgetPanel
  - de.uniwuerzburg.physik.pakma.gui.widget.ContextMenu
"""

from __future__ import annotations
import math
from typing import Optional, List
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu,
    QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QMouseEvent, QContextMenuEvent,
    QKeyEvent, QKeySequence, QAction, QWheelEvent
)

from .component_item import PakmaComponentItem
from ..dialogs.property_dialog import PropertyDialog


class DesignPanel(QGraphicsView):
    """
    DesignPanel — White canvas supporting interactive component creation,
    8-point resizing, grid snapping, Z-ordering, middle-mouse workspace panning,
    zoom, and JPAKMA context menus.
    """
    component_selected = pyqtSignal(object)

    def __init__(self, mode: str = "GR", parent=None):
        super().__init__(parent)
        self.mode = mode  # "GR" (GraphView) or "PM" (PMView)
        self.grid_enabled = True
        self.grid_size = 16

        # Active creation tool ("pointer" means selection/move/resize mode)
        self.active_tool: str = "pointer"

        # Panning state for middle-mouse button or Alt+Left drag
        self._is_panning: bool = False
        self._pan_start_pos: QPoint = QPoint()

        # Clipboard for copy/paste/duplicate
        self._clipboard: List[dict] = []

        # Scene configuration
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.setScene(self.scene)

        # Rendering & Viewport options (FullViewportUpdate prevents trail artifacts)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor('#ffffff')))
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.widgets: List[PakmaComponentItem] = []

    def set_active_tool(self, tool_id: str):
        """Sets active tool from toolbar (e.g., 'pointer', 'spring', 'oval', 'anagauge')."""
        self.active_tool = tool_id
        if tool_id == "pointer":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)

    def toggle_grid(self, enabled: bool | None = None):
        if enabled is None:
            self.grid_enabled = not self.grid_enabled
        else:
            self.grid_enabled = enabled
        self.viewport().update()

    def clear_canvas(self):
        self.scene.clear()
        self.widgets.clear()

    def add_widget_item(
        self, 
        title: str, 
        widget_type: str, 
        x: float = 0, 
        y: float = 0,
        width: float = 100,
        height: float = 60
    ) -> PakmaComponentItem:
        """Adds and tracks a new PakmaComponentItem on the scene."""
        # Provide specialized default dimensions per component type
        if widget_type in ["spring"]:
            width, height = 120, 40
        elif widget_type in ["oval"]:
            width, height = 70, 70
        elif widget_type in ["anagauge", "analog_gauge"]:
            width, height = 90, 80
        elif widget_type in ["diggauge", "digital_gauge"]:
            width, height = 110, 45
        elif widget_type in ["lingauge", "linear_gauge", "thermgauge", "thermometer"]:
            width, height = 50, 100
        elif widget_type in ["touchpad"]:
            width, height = 90, 90
        elif widget_type in ["button"]:
            width, height = 90, 36
        elif widget_type in ["scrollbar"]:
            width, height = 120, 30
        elif widget_type in ["coordinate", "graph"]:
            width, height = 130, 90
        elif widget_type in ["arrow", "fat_arrow", "simple_arrow", "vector"]:
            width, height = 100, 30

        node = PakmaComponentItem(title, widget_type, x, y, width, height)
        self.scene.addItem(node)
        self.widgets.append(node)
        return node

    # --- Mouse & Panning & Creation Handling ---
    def mousePressEvent(self, event: QMouseEvent):
        # 1. Middle mouse button OR Alt+Left click initiates workspace panning
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # 2. Left click with creation tool places a new widget
        if event.button() == Qt.MouseButton.LeftButton and self.active_tool != "pointer":
            scene_pos = self.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()
            if self.grid_enabled:
                x = round(x / self.grid_size) * self.grid_size
                y = round(y / self.grid_size) * self.grid_size

            # Auto-title formatting based on active tool
            tool_titles = {
                "rect": "Block",
                "oval": "Mass (m)",
                "spring": "Spring (k)",
                "arrow": "Force (F)",
                "simplearrow": "Vector (v)",
                "anagauge": "Voltmeter",
                "diggauge": "Digital Readout",
                "lingauge": "Level Meter",
                "thermgauge": "Thermometer",
                "button": "Trigger",
                "scrollbar": "Slider",
                "touchpad": "2D Joystick",
                "coordinate": "Coordinates",
                "graph": "Graph Scope",
                "pm_constant": "Constant [k=10]",
                "pm_function": "Function f(x)",
                "pm_accumulate": "∫ a dt -> v",
                "pm_variation": "Δx / Δt",
                "pm_measure": "Sensor (COM)",
                "pm_adopt": "Adopt Target",
                "pm_steer": "Steer Controller",
                "pm_trigger": "Trigger Pulse",
            }
            title = tool_titles.get(self.active_tool, self.active_tool.replace("_", " ").title())
            new_item = self.add_widget_item(title, self.active_tool, x, y)
            
            # Select new item and reset to pointer tool
            self.scene.clearSelection()
            new_item.setSelected(True)
            self.set_active_tool("pointer")
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Handle active workspace panning
        if self._is_panning:
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            if event.button() in [Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton]:
                self._is_panning = False
                self.set_active_tool(self.active_tool)
                event.accept()
                return

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        # Ctrl + Mouse Wheel for canvas zoom in / out
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
            self.scale(zoom_factor, zoom_factor)
            event.accept()
            return
        super().wheelEvent(event)

    # --- Right-Click Context Menu Engine ---
    def contextMenuEvent(self, event: QContextMenuEvent):
        item = self.itemAt(event.pos())
        # Traverse up to PakmaComponentItem if clicking on child/handle
        while item is not None and not isinstance(item, PakmaComponentItem):
            item = item.parentItem()

        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #fcfcfc; border: 1px solid #c8c8c8; font-family: Segoe UI; font-size: 9pt; } QMenu::item:selected { background-color: #0078d7; color: #ffffff; }")

        if isinstance(item, PakmaComponentItem):
            # 1. Properties Entry (Top item as in JPAKMA)
            act_props = menu.addAction("Properties...")
            act_props.triggered.connect(lambda: self._open_properties(item))
            menu.addSeparator()

            # 2. Copy & Paste Submenu
            sub_edit = menu.addMenu("Copy & Paste")
            act_copy = sub_edit.addAction("Copy")
            act_copy.setShortcut(QKeySequence.StandardKey.Copy)
            act_copy.triggered.connect(lambda: self._copy_selected(item))

            act_cut = sub_edit.addAction("Cut")
            act_cut.setShortcut(QKeySequence.StandardKey.Cut)
            act_cut.triggered.connect(lambda: self._cut_selected(item))

            act_dup = sub_edit.addAction("Duplicate")
            act_dup.setShortcut(QKeySequence("Ctrl+D"))
            act_dup.triggered.connect(lambda: self._duplicate_item(item))

            act_del = sub_edit.addAction("Delete")
            act_del.setShortcut(QKeySequence.StandardKey.Delete)
            act_del.triggered.connect(lambda: self._delete_item(item))

            # 3. Z-Order Submenu
            sub_zorder = menu.addMenu("Z-Order")
            act_front = sub_zorder.addAction("Bring to Foreground")
            act_front.triggered.connect(lambda: item.setZValue(item.zValue() + 1.0))

            act_back = sub_zorder.addAction("Send to Background")
            act_back.triggered.connect(lambda: item.setZValue(item.zValue() - 1.0))

            # 4. Transform Submenu
            sub_trans = menu.addMenu("Transform")
            act_rot_cw = sub_trans.addAction("Rotate 90° CW")
            act_rot_cw.triggered.connect(lambda: item.setRotation(item.rotation() + 90))

            act_rot_ccw = sub_trans.addAction("Rotate 90° CCW")
            act_rot_ccw.triggered.connect(lambda: item.setRotation(item.rotation() - 90))

            act_reset_size = sub_trans.addAction("Reset Default Size")
            act_reset_size.triggered.connect(lambda: item.set_custom_size(100, 60))

            menu.addSeparator()

            # 5. Quick Toggles
            act_lock = menu.addAction("Lock Position")
            act_lock.setCheckable(True)
            act_lock.setChecked(item.properties.get("locked", False))
            act_lock.toggled.connect(lambda checked: self._set_item_lock(item, checked))

            act_grid = menu.addAction("Snap to Grid")
            act_grid.setCheckable(True)
            act_grid.setChecked(item.properties.get("grid_snap", True))
            act_grid.toggled.connect(lambda checked: item.properties.update({"grid_snap": checked}))

            act_color = menu.addAction("Quick Fill Color...")
            act_color.triggered.connect(lambda: self._quick_color_item(item))

        else:
            # Canvas context menu
            act_paste = menu.addAction("Paste")
            act_paste.setShortcut(QKeySequence.StandardKey.Paste)
            act_paste.setEnabled(len(self._clipboard) > 0)
            act_paste.triggered.connect(lambda: self._paste_items(self.mapToScene(event.pos())))

            menu.addSeparator()

            act_toggle_grid = menu.addAction("Toggle Grid")
            act_toggle_grid.setCheckable(True)
            act_toggle_grid.setChecked(self.grid_enabled)
            act_toggle_grid.triggered.connect(self.toggle_grid)

            act_clear = menu.addAction("Clear Canvas")
            act_clear.triggered.connect(self.clear_canvas)

        menu.exec(event.globalPos())

    def _open_properties(self, item: PakmaComponentItem):
        dlg = PropertyDialog(item, self)
        dlg.exec()

    def _copy_selected(self, target_item: Optional[PakmaComponentItem] = None):
        items = self.scene.selectedItems()
        if not items and target_item:
            items = [target_item]
        self._clipboard = [
            {
                "title": i.title,
                "type": i.widget_type,
                "rect": (i.rect().x(), i.rect().y(), i.rect().width(), i.rect().height()),
                "pos": (i.pos().x(), i.pos().y()),
                "properties": dict(i.properties),
                "rotation": i.rotation(),
                "z_value": i.zValue(),
            }
            for i in items if isinstance(i, PakmaComponentItem)
        ]

    def _cut_selected(self, target_item: Optional[PakmaComponentItem] = None):
        self._copy_selected(target_item)
        items = self.scene.selectedItems()
        if not items and target_item:
            items = [target_item]
        for i in items:
            if isinstance(i, PakmaComponentItem):
                self._delete_item(i)

    def _duplicate_item(self, item: PakmaComponentItem):
        new_item = self.add_widget_item(
            item.title,
            item.widget_type,
            item.pos().x() + 20,
            item.pos().y() + 20,
            item.rect().width(),
            item.rect().height()
        )
        new_item.properties = dict(item.properties)
        new_item.setRotation(item.rotation())
        new_item.setZValue(item.zValue())
        self.scene.clearSelection()
        new_item.setSelected(True)

    def _delete_item(self, item: PakmaComponentItem):
        if item in self.widgets:
            self.widgets.remove(item)
        self.scene.removeItem(item)

    def _set_item_lock(self, item: PakmaComponentItem, locked: bool):
        item.properties["locked"] = locked
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not locked)
        for h in item.handles:
            h.setVisible(not locked and item.isSelected())

    def _quick_color_item(self, item: PakmaComponentItem):
        col = QColorDialog.getColor(QColor(item.properties.get("fill_color", "#ffffff")), self, "Select Color")
        if col.isValid():
            item.properties["fill_color"] = col.name()
            item.update()

    def _paste_items(self, target_pos: QPointF):
        if not self._clipboard:
            return
        self.scene.clearSelection()
        offset_x, offset_y = target_pos.x(), target_pos.y()
        for idx, data in enumerate(self._clipboard):
            new_item = self.add_widget_item(
                data["title"],
                data["type"],
                offset_x + idx * 15,
                offset_y + idx * 15,
                data["rect"][2],
                data["rect"][3]
            )
            new_item.properties = dict(data["properties"])
            new_item.setRotation(data["rotation"])
            new_item.setZValue(data["z_value"])
            new_item.setSelected(True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete:
            for item in list(self.scene.selectedItems()):
                if isinstance(item, PakmaComponentItem):
                    self._delete_item(item)
            event.accept()
            return
        elif event.matches(QKeySequence.StandardKey.Copy):
            self._copy_selected()
            event.accept()
            return
        elif event.matches(QKeySequence.StandardKey.Cut):
            self._cut_selected()
            event.accept()
            return
        elif event.matches(QKeySequence.StandardKey.Paste):
            self._paste_items(self.mapToScene(self.viewport().rect().center()))
            event.accept()
            return
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D:
            for item in list(self.scene.selectedItems()):
                if isinstance(item, PakmaComponentItem):
                    self._duplicate_item(item)
            event.accept()
            return
        super().keyPressEvent(event)

    # --- Background Dot-Grid Rendering ---
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
