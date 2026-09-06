"""
PropertyDialog — Comprehensive customization dialog for PyPAKMA components.
Provides tabs for General Geometry, Physics & Variables, and Appearance Styling.
Ported from JPAKMA:
  - de.uniwuerzburg.physik.pakma.gui.dlg.PropertyDialog
  - de.uniwuerzburg.physik.pakma.gui.widget.ContextMenu
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, 
    QCheckBox, QPushButton, QColorDialog, QDialogButtonBox,
    QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

if TYPE_CHECKING:
    from ..widgets.component_item import PakmaComponentItem


class PropertyDialog(QDialog):
    """
    Multi-tab Property Configuration Dialog for PyPAKMA components.
    """
    def __init__(self, item: PakmaComponentItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle(f"Properties — {item.title} ({item.widget_type})")
        self.resize(460, 420)

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.tab_general = QWidget()
        self.tab_physics = QWidget()
        self.tab_style = QWidget()

        self._build_general_tab()
        self._build_physics_tab()
        self._build_style_tab()

        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_physics, "Physics & Variables")
        self.tabs.addTab(self.tab_style, "Appearance")

        main_layout.addWidget(self.tabs)

        # OK / Cancel Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        self.button_box.accepted.connect(self._apply_and_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _build_general_tab(self):
        layout = QFormLayout(self.tab_general)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self.txt_title = QLineEdit(self.item.title)
        layout.addRow("Display Title / Label:", self.txt_title)

        self.txt_type = QLineEdit(self.item.widget_type)
        self.txt_type.setReadOnly(True)
        self.txt_type.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        layout.addRow("Component Type:", self.txt_type)

        # Position X, Y
        pos_layout = QHBoxLayout()
        self.spn_x = QDoubleSpinBox()
        self.spn_x.setRange(-5000, 5000)
        self.spn_x.setValue(self.item.pos().x())
        self.spn_y = QDoubleSpinBox()
        self.spn_y.setRange(-5000, 5000)
        self.spn_y.setValue(self.item.pos().y())
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.spn_x)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.spn_y)
        layout.addRow("Position (px):", pos_layout)

        # Dimensions W x H
        dim_layout = QHBoxLayout()
        self.spn_w = QDoubleSpinBox()
        self.spn_w.setRange(20, 2000)
        self.spn_w.setValue(self.item.rect().width())
        self.spn_h = QDoubleSpinBox()
        self.spn_h.setRange(15, 2000)
        self.spn_h.setValue(self.item.rect().height())
        dim_layout.addWidget(QLabel("W:"))
        dim_layout.addWidget(self.spn_w)
        dim_layout.addWidget(QLabel("H:"))
        dim_layout.addWidget(self.spn_h)
        layout.addRow("Dimensions (px):", dim_layout)

        # Rotation
        self.spn_rot = QDoubleSpinBox()
        self.spn_rot.setRange(-360, 360)
        self.spn_rot.setValue(self.item.rotation())
        layout.addRow("Rotation (°):", self.spn_rot)

        # Options
        self.chk_locked = QCheckBox("Lock position & prevent moving")
        self.chk_locked.setChecked(self.item.properties.get("locked", False))
        layout.addRow("", self.chk_locked)

        self.chk_grid = QCheckBox("Snap to Grid (8px)")
        self.chk_grid.setChecked(self.item.properties.get("grid_snap", True))
        layout.addRow("", self.chk_grid)

    def _build_physics_tab(self):
        layout = QFormLayout(self.tab_physics)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        props = self.item.properties

        self.txt_var = QLineEdit(str(props.get("variable_name", "")))
        layout.addRow("Variable Name:", self.txt_var)

        self.txt_expr = QLineEdit(str(props.get("expression", "")))
        layout.addRow("Formula / Expression:", self.txt_expr)

        self.spn_val = QDoubleSpinBox()
        self.spn_val.setRange(-1e9, 1e9)
        self.spn_val.setDecimals(4)
        self.spn_val.setValue(float(props.get("value", 0.0)))
        layout.addRow("Initial / Current Value:", self.spn_val)

        # Min / Max / Step Range
        range_layout = QHBoxLayout()
        self.spn_min = QDoubleSpinBox()
        self.spn_min.setRange(-1e9, 1e9)
        self.spn_min.setValue(float(props.get("min_val", 0.0)))
        self.spn_max = QDoubleSpinBox()
        self.spn_max.setRange(-1e9, 1e9)
        self.spn_max.setValue(float(props.get("max_val", 100.0)))
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.spn_min)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.spn_max)
        layout.addRow("Scale Range:", range_layout)

        self.txt_unit = QLineEdit(str(props.get("unit", "")))
        layout.addRow("Physical Unit:", self.txt_unit)

    def _build_style_tab(self):
        layout = QFormLayout(self.tab_style)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        props = self.item.properties

        # Fill Color
        fill_layout = QHBoxLayout()
        self.fill_color = props.get("fill_color", "#ffffff")
        self.btn_fill = QPushButton()
        self.btn_fill.setFixedHeight(26)
        self._update_color_btn(self.btn_fill, self.fill_color)
        self.btn_fill.clicked.connect(self._pick_fill_color)
        fill_layout.addWidget(self.btn_fill)
        layout.addRow("Fill Color:", fill_layout)

        # Border Color
        border_layout = QHBoxLayout()
        self.border_color = props.get("border_color", "#333333")
        self.btn_border = QPushButton()
        self.btn_border.setFixedHeight(26)
        self._update_color_btn(self.btn_border, self.border_color)
        self.btn_border.clicked.connect(self._pick_border_color)
        border_layout.addWidget(self.btn_border)
        layout.addRow("Border Color:", border_layout)

        # Border Width
        self.spn_border_w = QDoubleSpinBox()
        self.spn_border_w.setRange(0.5, 10.0)
        self.spn_border_w.setSingleStep(0.5)
        self.spn_border_w.setValue(float(props.get("border_width", 1.5)))
        layout.addRow("Border Width (px):", self.spn_border_w)

        # Font Size
        self.spn_font_size = QSpinBox()
        self.spn_font_size.setRange(6, 32)
        self.spn_font_size.setValue(int(props.get("font_size", 9)))
        layout.addRow("Label Font Size:", self.spn_font_size)

    def _update_color_btn(self, btn: QPushButton, hex_color: str):
        btn.setText(hex_color)
        btn.setStyleSheet(f"background-color: {hex_color}; color: {'#ffffff' if QColor(hex_color).lightness() < 128 else '#000000'}; font-weight: bold; border-radius: 3px; border: 1px solid #999999;")

    def _pick_fill_color(self):
        col = QColorDialog.getColor(QColor(self.fill_color), self, "Select Fill Color")
        if col.isValid():
            self.fill_color = col.name()
            self._update_color_btn(self.btn_fill, self.fill_color)

    def _pick_border_color(self):
        col = QColorDialog.getColor(QColor(self.border_color), self, "Select Border Color")
        if col.isValid():
            self.border_color = col.name()
            self._update_color_btn(self.btn_border, self.border_color)

    def _apply_and_accept(self):
        # Apply Geometry
        self.item.title = self.txt_title.text()
        self.item.setPos(self.spn_x.value(), self.spn_y.value())
        self.item.set_custom_size(self.spn_w.value(), self.spn_h.value())
        self.item.setRotation(self.spn_rot.value())

        # Apply Properties
        props = self.item.properties
        props["name"] = self.txt_title.text()
        props["locked"] = self.chk_locked.isChecked()
        props["grid_snap"] = self.chk_grid.isChecked()

        props["variable_name"] = self.txt_var.text()
        props["expression"] = self.txt_expr.text()
        props["value"] = self.spn_val.value()
        props["min_val"] = self.spn_min.value()
        props["max_val"] = self.spn_max.value()
        props["unit"] = self.txt_unit.text()

        props["fill_color"] = self.fill_color
        props["border_color"] = self.border_color
        props["border_width"] = self.spn_border_w.value()
        props["font_size"] = self.spn_font_size.value()

        self.item.update()
        self.accept()
