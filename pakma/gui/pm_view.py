"""
PMView — Physical Model Block Diagram Tab matching original JPAKMA PMView.
Ported from: de.uniwuerzburg.physik.pakma.gui.PMView
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QButtonGroup, 
    QToolButton
)
from PyQt6.QtCore import Qt, QSize
from .widget_canvas import DesignPanel
from ..util.resource_manager import ResourceManager


class PMView(QWidget):
    """
    PMView (Physical Model Tab) featuring authentic JPAKMA vertical block palette,
    white DesignPanel canvas for block diagrams, and bottom toolbar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Center area: Left Vertical Palette + Center Canvas
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # 1. Left Vertical Palette
        self.tool_palette = QToolBar("PM Tools", self)
        self.tool_palette.setOrientation(Qt.Orientation.Vertical)
        self.tool_palette.setIconSize(QSize(20, 20))
        self.tool_palette.setStyleSheet("QToolBar { background-color: #f0f0f4; border-right: 1px solid #d0d0d8; padding: 2px; }")

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self._add_tool_btn("images/pointer.gif", "Selection Tool (Pointer)", True)
        self._add_tool_btn("images/pm_effectarrow.gif", "Effect Arrow (Wire Connection)", False)
        self.tool_palette.addSeparator()

        self._add_tool_btn("images/pm_constant.gif", "Constant Widget (k, m, c)", False, lambda: self.canvas.add_widget_item("Constant [k=10]", "pm_constant", -150, -50))
        self._add_tool_btn("images/pm_function.gif", "Function Widget f(x)", False, lambda: self.canvas.add_widget_item("Function [F=-k*x]", "pm_function", 0, 50))
        self._add_tool_btn("images/pm_accumulate.gif", "Cumulate / Integrator Widget (dx/dt)", False, lambda: self.canvas.add_widget_item("∫ a dt -> v", "pm_accumulate", 50, -50))
        self._add_tool_btn("images/pm_variation.gif", "Variation Widget", False)
        self._add_tool_btn("images/pm_measure.gif", "Measure Widget (PySerial Sensor)", False, lambda: self.canvas.add_widget_item("Sensor Input", "pm_measure", -150, 80))
        self._add_tool_btn("images/pm_adopt.gif", "Adopt Widget", False)
        self._add_tool_btn("images/pm_steer.gif", "Steer Widget", False)
        self._add_tool_btn("images/pm_trigger.gif", "Trigger Widget", False)

        center_layout.addWidget(self.tool_palette)

        # 2. White Canvas
        self.canvas = DesignPanel("PM", self)
        center_layout.addWidget(self.canvas, stretch=1)
        main_layout.addWidget(center_widget, stretch=1)

        # 3. Bottom Canvas Sub-Toolbar
        self.bottom_bar = QToolBar("PM Operations", self)
        self.bottom_bar.setIconSize(QSize(18, 18))
        self.bottom_bar.setStyleSheet("QToolBar { background-color: #f4f4f8; border-top: 1px solid #d0d0d8; }")

        act_trash = self.bottom_bar.addAction(ResourceManager.get_icon("images/trash.gif"), "Delete All Objects")
        act_trash.triggered.connect(self.canvas.clear_canvas)

        act_grid = self.bottom_bar.addAction(ResourceManager.get_icon("images/grid.gif"), "Toggle Grid")
        act_grid.setCheckable(True)
        act_grid.setChecked(True)
        act_grid.triggered.connect(self.canvas.toggle_grid)

        main_layout.addWidget(self.bottom_bar)

        self._create_default_model()

    def _add_tool_btn(self, icon_path: str, tooltip: str, checked: bool = False, callback=None):
        btn = QToolButton(self)
        btn.setIcon(ResourceManager.get_icon(icon_path))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setChecked(checked)
        if callback:
            btn.clicked.connect(callback)
        self.btn_group.addButton(btn)
        self.tool_palette.addWidget(btn)

    def _create_default_model(self):
        self.canvas.add_widget_item("Constant [k = 10.0]", "pm_constant", -150, -60)
        self.canvas.add_widget_item("∫ a dt -> v", "pm_accumulate", 0, -60)
        self.canvas.add_widget_item("∫ v dt -> x", "pm_accumulate", 150, -60)
