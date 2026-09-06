"""
GraphView — Animation Tab matching original JPAKMA GraphView.java.
Provides complete left tool palette with Controls, Geometry/Springs/Vectors, Gauges/Instruments,
and Physical Model tools, plus 8-point interactive resize and context menus.
Ported from: de.uniwuerzburg.physik.pakma.gui.GraphView
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QButtonGroup, 
    QToolButton, QSplitter, QScrollArea
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

        # 1. Left Vertical Tool Palette (Wrapped in ScrollArea for compact display)
        self._create_left_palette(center_layout)

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
        self._create_bottom_bar(main_layout)

        # Default sample harmonic oscillator widgets on canvas
        self._setup_initial_widgets()

    def _create_left_palette(self, parent_layout: QHBoxLayout):
        """Builds full vertical tool palette matching JPAKMA GraphView."""
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

        # 1. Selection pointer
        self._add_tool_btn(palette_layout, "images/pointer.gif", "Selection Tool (Pointer / Move / Resize)", "pointer", True)
        self._add_palette_separator(palette_layout)

        # 2. Interactive Controls Group
        self._add_tool_btn(palette_layout, "images/button.gif", "Button Control", "button")
        self._add_tool_btn(palette_layout, "images/choice.gif", "Choice / Radiobuttons", "choice")
        self._add_tool_btn(palette_layout, "images/option.gif", "Option / Checkboxes", "option")
        self._add_tool_btn(palette_layout, "images/scrollbar.gif", "Scrollbar / Slider Control", "scrollbar")
        self._add_tool_btn(palette_layout, "images/touchpad.gif", "Touchpad 2D Joystick", "touchpad")
        self._add_tool_btn(palette_layout, "images/editfield.gif", "Edit Input Field", "editfield")
        self._add_palette_separator(palette_layout)

        # 3. Geometric & Physical Bodies
        self._add_tool_btn(palette_layout, "images/rect.gif", "Rectangle Body", "rect")
        self._add_tool_btn(palette_layout, "images/oval.gif", "Oval / Circular Mass", "oval")
        self._add_tool_btn(palette_layout, "images/labelrect.gif", "Rectangle with Labels", "labelrect")
        self._add_tool_btn(palette_layout, "images/bar.gif", "Level Bar Indicator", "bar")
        self._add_tool_btn(palette_layout, "images/spring.gif", "Harmonic Spring Oscillator", "spring")
        self._add_tool_btn(palette_layout, "images/fatarrow.gif", "Fat Arrow Vector", "arrow")
        self._add_tool_btn(palette_layout, "images/simplearrow.gif", "Vector Arrow (Velocity / Force)", "simplearrow")
        self._add_tool_btn(palette_layout, "images/chainarrow.gif", "Chain Vector", "chain_vector")
        self._add_tool_btn(palette_layout, "images/multiarrow.gif", "Multi Vector", "multi_vector")
        self._add_tool_btn(palette_layout, "images/poly.gif", "Polygon Shape", "poly")
        self._add_tool_btn(palette_layout, "images/text.gif", "Text Label", "text")
        self._add_tool_btn(palette_layout, "images/textarea.gif", "Formatted Text Area", "textarea")
        self._add_palette_separator(palette_layout)

        # 4. Gauges & Instruments
        self._add_tool_btn(palette_layout, "images/pinpoint.gif", "Pinpoint Coordinate Marker", "pinpoint")
        self._add_tool_btn(palette_layout, "images/graph.gif", "2D Scope Graph", "graph")
        self._add_tool_btn(palette_layout, "images/anagauge.gif", "Analog Dial Gauge (Voltmeter)", "anagauge")
        self._add_tool_btn(palette_layout, "images/lingauge.gif", "Linear Level Gauge", "lingauge")
        self._add_tool_btn(palette_layout, "images/diggauge.gif", "Digital LED Readout Display", "diggauge")
        self._add_tool_btn(palette_layout, "images/thermgauge.gif", "Mercury Thermometer", "thermgauge")
        self._add_tool_btn(palette_layout, "images/coordinate.gif", "Coordinate Axis System", "coordinate")
        self._add_tool_btn(palette_layout, "images/plotter3d.gif", "3D Plotter Graph", "plotter3d")
        self._add_tool_btn(palette_layout, "images/imagematrix.gif", "Image Matrix / Texture", "imagematrix")
        self._add_palette_separator(palette_layout)

        # 5. Physical Model (PM) Blocks inside Animation view
        self._add_tool_btn(palette_layout, "images/pm_constant.gif", "PM Constant Block [k, m, c]", "pm_constant")
        self._add_tool_btn(palette_layout, "images/pm_function.gif", "PM Function Block f(x)", "pm_function")
        self._add_tool_btn(palette_layout, "images/pm_accumulate.gif", "PM Cumulate / Integrator Block", "pm_accumulate")
        self._add_tool_btn(palette_layout, "images/pm_measure.gif", "PM Sensor Measure Block", "pm_measure")

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

        parent_layout.addWidget(self.bottom_bar)

    def _setup_initial_widgets(self):
        self.canvas.add_widget_item("Spring (k = 10 N/m)", "spring", -100, -50)
        self.canvas.add_widget_item("Mass (m = 1 kg)", "oval", 50, -50)
        self.canvas.add_widget_item("Position Scope", "graph", -100, 70)
        self.canvas.add_widget_item("Digital Readout", "diggauge", 70, 70)

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
