"""
GraphView — Animation Tab matching original JPAKMA GraphView.
Ported from: de.uniwuerzburg.physik.pakma.gui.GraphView
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QButtonGroup, 
    QToolButton, QSplitter
)
from PyQt6.QtCore import Qt, QSize
from ..widgets.design_panel import DesignPanel
from ..widgets.plot_widget import RealTimePlotWidget
from ...util.resource_manager import ResourceManager
from ...engine.simulation import SimulationEngine


class GraphView(QWidget):
    """
    GraphView (Animation Tab) with original JPAKMA vertical widget tool palette,
    white DesignPanel canvas, bottom canvas toolbar, and real-time pyqtgraph plotting.
    """
    def __init__(self, engine: SimulationEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Center area with Left Vertical Toolbar + Center Canvas / Splitter
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # 1. Left Vertical Tool Palette
        self.tool_palette = QToolBar("Widget Tools", self)
        self.tool_palette.setOrientation(Qt.Orientation.Vertical)
        self.tool_palette.setIconSize(QSize(20, 20))
        self.tool_palette.setStyleSheet("QToolBar { background-color: #f0f0f4; border-right: 1px solid #d0d0d8; padding: 2px; }")

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self._add_tool_btn("images/pointer.gif", "Selection Tool (Pointer)", True)
        self.tool_palette.addSeparator()

        self._add_tool_btn("images/simple.gif", "Point Mass / Simple Body", False, lambda: self.canvas.add_widget_item("Mass (m)", "oval", -100, -50))
        self._add_tool_btn("images/rect.gif", "Rectangle Body", False, lambda: self.canvas.add_widget_item("Block", "rect", 0, 0))
        self._add_tool_btn("images/oval.gif", "Oval / Circle Body", False, lambda: self.canvas.add_widget_item("Circle", "oval", 50, 50))
        self._add_tool_btn("images/spring.gif", "Spring Oscillator", False, lambda: self.canvas.add_widget_item("Spring k=10", "spring", -50, -100))
        self._add_tool_btn("images/simplearrow.gif", "Vector Arrow (v, F)", False, lambda: self.canvas.add_widget_item("Vector F", "arrow", 100, -50))
        self.tool_palette.addSeparator()

        self._add_tool_btn("images/graph.gif", "2D Coordinate Graph", False)
        self._add_tool_btn("images/anagauge.gif", "Analog Gauge", False, lambda: self.canvas.add_widget_item("Gauge (V)", "rect", 150, 50))
        self._add_tool_btn("images/diggauge.gif", "Digital Gauge", False, lambda: self.canvas.add_widget_item("Digital Display", "rect", 150, 120))
        self._add_tool_btn("images/scrollbar.gif", "Scrollbar / Slider Controller", False)
        self._add_tool_btn("images/button.gif", "Button Control", False)
        self._add_tool_btn("images/editfield.gif", "Edit Input Field", False)

        center_layout.addWidget(self.tool_palette)

        # 2. Splitter: Center DesignPanel + Right Real-Time pyqtgraph Plot
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # White Canvas DesignPanel
        self.canvas = DesignPanel("GR", self)
        splitter.addWidget(self.canvas)

        # Real-time pyqtgraph Scope
        self.plot_panel = RealTimePlotWidget("Measurement & Simulation Graph (pyqtgraph)", self)
        self.plot_panel.add_curve("Position x(t)", color="#0078d7")
        self.plot_panel.add_curve("Velocity v(t)", color="#d83b01")
        splitter.addWidget(self.plot_panel)

        splitter.setSizes([600, 400])
        center_layout.addWidget(splitter, stretch=1)
        main_layout.addWidget(center_widget, stretch=1)

        # 3. Bottom Canvas Sub-Toolbar matching original JPAKMA GraphView
        self.bottom_bar = QToolBar("Canvas Operations", self)
        self.bottom_bar.setIconSize(QSize(18, 18))
        self.bottom_bar.setStyleSheet("QToolBar { background-color: #f4f4f8; border-top: 1px solid #d0d0d8; }")

        act_trash = self.bottom_bar.addAction(ResourceManager.get_icon("images/trash.gif"), "Delete All Objects")
        act_trash.triggered.connect(self.canvas.clear_canvas)

        act_grid = self.bottom_bar.addAction(ResourceManager.get_icon("images/grid.gif"), "Toggle Grid")
        act_grid.setCheckable(True)
        act_grid.setChecked(True)
        act_grid.triggered.connect(self.canvas.toggle_grid)

        self.bottom_bar.addAction(ResourceManager.get_icon("images/wccenter.gif"), "Object Control Center")
        self.bottom_bar.addAction(ResourceManager.get_icon("images/groups.gif"), "Edit Groups")
        self.bottom_bar.addAction(ResourceManager.get_icon("images/clearcanvas.gif"), "Clear Canvas Stamp")

        main_layout.addWidget(self.bottom_bar)

        # Default sample harmonic oscillator widgets on canvas
        self._setup_initial_widgets()

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

    def _setup_initial_widgets(self):
        self.canvas.add_widget_item("Spring (k=10 N/m)", "spring", -100, -50)
        self.canvas.add_widget_item("Mass (m=1 kg)", "oval", 50, -50)
        self.engine.reset({"x": 1.0, "v": 0.0})
        self.engine.equations = {
            "x": lambda t, s: s["v"],
            "v": lambda t, s: -10.0 * s["x"] - 0.2 * s["v"]
        }

    def update_plots(self):
        t_arr, x_arr = self.engine.get_numpy_arrays("x")
        _, v_arr = self.engine.get_numpy_arrays("v")
        if len(t_arr) > 0:
            self.plot_panel.update_curve("Position x(t)", t_arr, x_arr)
            self.plot_panel.update_curve("Velocity v(t)", t_arr, v_arr)
