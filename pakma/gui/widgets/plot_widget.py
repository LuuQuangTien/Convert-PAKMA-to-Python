"""
High-Performance Real-Time Physics Plotting Widget for PyPAKMA using PyQtGraph & NumPy.
"""

from __future__ import annotations
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, 
    QComboBox, QLabel, QFileDialog, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class RealTimePlotWidget(QWidget):
    """
    Advanced real-time plotting widget wrapping PyQtGraph PlotWidget with multi-channel support,
    crosshair inspection, auto-ranging, and data export.
    """
    def __init__(self, title: str = "Real-Time Physics Graph", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)

        # PyQtGraph PlotWidget setup
        pg.setConfigOptions(antialias=True, background='#ffffff', foreground='#202020')
        self.plot_widget = pg.PlotWidget(title=title)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend(offset=(10, 10))
        
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.getAxis('bottom').setLabel('Time (t)', units='s')
        self.plot_item.getAxis('left').setLabel('Value')

        # Curves management: name -> PlotDataItem
        self.curves: dict[str, pg.PlotDataItem] = {}
        self.curve_colors = [
            '#0078d7', '#d83b01', '#107c41', '#b4009e', '#5c2d91', '#008272', '#a80000'
        ]

        # Top Control Bar
        self.control_bar = QHBoxLayout()
        self.control_bar.setSpacing(6)

        self.btn_autorange = QPushButton("Auto Range")
        self.btn_autorange.clicked.connect(self.auto_range)
        self.control_bar.addWidget(self.btn_autorange)

        self.chk_grid = QCheckBox("Grid")
        self.chk_grid.setChecked(True)
        self.chk_grid.toggled.connect(lambda v: self.plot_widget.showGrid(x=v, y=v, alpha=0.3))
        self.control_bar.addWidget(self.chk_grid)

        self.chk_crosshair = QCheckBox("Crosshair")
        self.chk_crosshair.setChecked(True)
        self.chk_crosshair.toggled.connect(self._toggle_crosshair)
        self.control_bar.addWidget(self.chk_crosshair)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_curves)
        self.control_bar.addWidget(self.btn_clear)

        self.btn_export_csv = QPushButton("CSV Export")
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.control_bar.addWidget(self.btn_export_csv)

        self.control_bar.addStretch()
        self.coord_label = QLabel("X: 0.000, Y: 0.000")
        self.coord_label.setStyleSheet("color: #0078d7; font-weight: bold;")
        self.control_bar.addWidget(self.coord_label)

        self.layout.addLayout(self.control_bar)
        self.layout.addWidget(self.plot_widget)

        # Crosshair lines
        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#0078d7', width=1, style=Qt.PenStyle.DashLine))
        self.h_line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#0078d7', width=1, style=Qt.PenStyle.DashLine))
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line, ignoreBounds=True)
        self.plot_widget.scene().sigMouseMoved.connect(self._mouse_moved)

        # Internal data buffers
        self.data_store: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    def add_curve(self, name: str, color: str | None = None, width: int = 2) -> pg.PlotDataItem:
        """Add a named curve to the plot."""
        if name in self.curves:
            return self.curves[name]
        
        idx = len(self.curves) % len(self.curve_colors)
        c = color or self.curve_colors[idx]
        pen = pg.mkPen(color=c, width=width)
        curve = self.plot_widget.plot(name=name, pen=pen)
        self.curves[name] = curve
        return curve

    def update_curve(self, name: str, x: np.ndarray | list[float], y: np.ndarray | list[float]):
        """Update curve with new NumPy array or list data."""
        if name not in self.curves:
            self.add_curve(name)
        
        x_arr = np.asarray(x, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.float64)
        self.data_store[name] = (x_arr, y_arr)
        self.curves[name].setData(x_arr, y_arr)

    def auto_range(self):
        self.plot_widget.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

    def clear_curves(self):
        for c in self.curves.values():
            c.clear()
        self.data_store.clear()

    def _toggle_crosshair(self, enabled: bool):
        self.v_line.setVisible(enabled)
        self.h_line.setVisible(enabled)

    def _mouse_moved(self, pos):
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
            x_val = mouse_point.x()
            y_val = mouse_point.y()
            self.coord_label.setText(f"X: {x_val:.4f}, Y: {y_val:.4f}")
            if self.chk_crosshair.isChecked():
                self.v_line.setPos(x_val)
                self.h_line.setPos(y_val)

    def export_csv(self):
        """Export current plotted curves to a CSV file."""
        if not self.data_store:
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Plot Data to CSV", "", "CSV Files (*.csv)")
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                header_cols = []
                for name in self.data_store:
                    header_cols.extend([f"{name}_t", f"{name}_val"])
                f.write(",".join(header_cols) + "\n")
                
                max_len = max(len(t) for t, _ in self.data_store.values())
                for i in range(max_len):
                    row = []
                    for name in self.data_store:
                        t, y = self.data_store[name]
                        if i < len(t):
                            row.extend([str(t[i]), str(y[i])])
                        else:
                            row.extend(["", ""])
                    f.write(",".join(row) + "\n")
        except Exception as ex:
            print(f"Error exporting CSV: {ex}")
