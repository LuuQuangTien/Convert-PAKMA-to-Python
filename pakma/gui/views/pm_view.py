"""
PMView — Physical Model Block Diagram Tab matching original JPAKMA PMView.java.
Ported from: de.uniwuerzburg.physik.pakma.gui.PMView
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QButtonGroup, 
    QToolButton, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from ..widgets.design_panel import DesignPanel
from ...util.resource_manager import ResourceManager


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
        self._create_left_palette(center_layout)

        # 2. White Canvas
        self.canvas = DesignPanel("PM", self)
        center_layout.addWidget(self.canvas, stretch=1)
        main_layout.addWidget(center_widget, stretch=1)

        # 3. Bottom Canvas Sub-Toolbar
        self._create_bottom_bar(main_layout)

        # Default model setup
        self._create_default_model()

    def _create_left_palette(self, parent_layout: QHBoxLayout):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(38)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f0f0f4; border-right: 1px solid #d0d0d8; }")

        palette_widget = QWidget()
        palette_layout = QVBoxLayout(palette_widget)
        palette_layout.setContentsMargins(2, 4, 2, 4)
        palette_layout.setSpacing(2)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        # Pointer & Wire
        self._add_tool_btn(palette_layout, "images/pointer.gif", "Selection Tool (Pointer / Move / Resize)", "pointer", True)
        self._add_tool_btn(palette_layout, "images/pm_effectarrow.gif", "Effect Arrow (Wire Connection)", "pm_effectarrow")
        self._add_palette_separator(palette_layout)

        # PM Core Calculation & Integration Nodes
        self._add_tool_btn(palette_layout, "images/pm_constant.gif", "Constant Parameter [k, m, c, g]", "pm_constant")
        self._add_tool_btn(palette_layout, "images/pm_function.gif", "Math Function Block f(x, v)", "pm_function")
        self._add_tool_btn(palette_layout, "images/pm_accumulate.gif", "Cumulate / Integrator Block (∫ ... dt)", "pm_accumulate")
        self._add_tool_btn(palette_layout, "images/pm_variation.gif", "Variation Block (Rate of Change Δx)", "pm_variation")
        self._add_palette_separator(palette_layout)

        # PM Hardware & Control Nodes
        self._add_tool_btn(palette_layout, "images/pm_measure.gif", "Measure Input (Sensor COM Port)", "pm_measure")
        self._add_tool_btn(palette_layout, "images/pm_adopt.gif", "Adopt Target Value", "pm_adopt")
        self._add_tool_btn(palette_layout, "images/pm_steer.gif", "Steer Feedback Controller", "pm_steer")
        self._add_tool_btn(palette_layout, "images/pm_trigger.gif", "Trigger Pulse Generator", "pm_trigger")
        self._add_palette_separator(palette_layout)

        # Screenshot / Preview
        self._add_tool_btn(palette_layout, "images/pm_graphview.gif", "Animation View Snapshot", "pm_graphview")

        palette_layout.addStretch(1)
        scroll.setWidget(palette_widget)
        parent_layout.addWidget(scroll)

    def _add_palette_separator(self, layout: QVBoxLayout):
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #d0d0d8; margin: 2px 4px;")
        layout.addWidget(sep)

    def _add_tool_btn(self, layout: QVBoxLayout, icon_path: str, tooltip: str, tool_id: str, checked: bool = False):
        btn = QToolButton(self)
        btn.setIcon(ResourceManager.get_icon(icon_path))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedSize(26, 26)
        btn.setStyleSheet("QToolButton { border: 1px solid transparent; border-radius: 3px; } QToolButton:hover { background-color: #e0e6f0; border-color: #a0b0d0; } QToolButton:checked { background-color: #cfe0fc; border-color: #0078d7; }")
        btn.clicked.connect(lambda: self.canvas.set_active_tool(tool_id))
        self.btn_group.addButton(btn)
        layout.addWidget(btn)

    def _create_bottom_bar(self, parent_layout: QVBoxLayout):
        self.bottom_bar = QToolBar("PM Operations", self)
        self.bottom_bar.setIconSize(QSize(18, 18))
        self.bottom_bar.setStyleSheet("QToolBar { background-color: #f4f4f8; border-top: 1px solid #d0d0d8; }")

        act_trash = self.bottom_bar.addAction(ResourceManager.get_icon("images/trash.gif"), "Delete All Objects")
        act_trash.triggered.connect(self.canvas.clear_canvas)

        act_grid = self.bottom_bar.addAction(ResourceManager.get_icon("images/grid.gif"), "Toggle Grid")
        act_grid.setCheckable(True)
        act_grid.setChecked(True)
        act_grid.triggered.connect(self.canvas.toggle_grid)

        main_layout = parent_layout
        main_layout.addWidget(self.bottom_bar)

    def _create_default_model(self):
        self.canvas.add_widget_item("Constant [k = 10.0]", "pm_constant", -160, -60)
        self.canvas.add_widget_item("Function [F = -k*x]", "pm_function", -160, 40)
        self.canvas.add_widget_item("∫ a dt -> v", "pm_accumulate", 0, -60)
        self.canvas.add_widget_item("∫ v dt -> x", "pm_accumulate", 160, -60)
        self.canvas.add_widget_item("Sensor [COM3]", "pm_measure", 160, 40)
