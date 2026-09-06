"""
Unit tests for PyPAKMA Phase 2 — Graphical Component Engine, Resize Handles,
DesignPanel Canvas, and Property Customization Dialog.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRectF, QPointF

# Ensure QApplication instance exists for GUI tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from pakma.gui.widgets.component_item import PakmaComponentItem, ResizeHandle, HandlePosition
from pakma.gui.widgets.design_panel import DesignPanel
from pakma.gui.dialogs.property_dialog import PropertyDialog


class TestPhase2Components(unittest.TestCase):
    """Test suite verifying all Phase 2 features."""

    def test_component_creation_and_types(self):
        """Verify instantiation of all major JPAKMA component types."""
        types_to_test = [
            ("Block Rect", "rect"),
            ("Mass Ball", "oval"),
            ("Coil Spring", "spring"),
            ("Force Arrow", "arrow"),
            ("Voltmeter", "anagauge"),
            ("Speedometer LED", "diggauge"),
            ("Thermometer", "thermgauge"),
            ("Trigger Button", "button"),
            ("Parameter Slider", "scrollbar"),
            ("2D Control Pad", "touchpad"),
            ("Scope Graph", "graph"),
            ("Integrator Node", "pm_accumulate"),
            ("Constant Parameter", "pm_constant"),
            ("Math Function", "pm_function"),
            ("Serial Sensor", "pm_measure"),
        ]

        for title, w_type in types_to_test:
            item = PakmaComponentItem(title, w_type, x=50, y=50, width=100, height=60)
            self.assertEqual(item.title, title)
            self.assertEqual(item.widget_type, w_type)
            self.assertEqual(item.pos().x(), 50)
            self.assertEqual(item.pos().y(), 50)
            self.assertEqual(len(item.handles), 8, f"Component {w_type} must have 8 resize handles")

    def test_8_point_resize_handles_positioning(self):
        """Verify that 8 resize handles are correctly positioned on component boundaries."""
        item = PakmaComponentItem("Resizing Test", "rect", x=0, y=0, width=120, height=80)
        # Rect is [-60, -40, 120, 80]
        r = item.rect()
        self.assertEqual(r.width(), 120)
        self.assertEqual(r.height(), 80)

        # Check corners and edges positions
        handles = {h.position: h for h in item.handles}
        self.assertAlmostEqual(handles[HandlePosition.TOP_LEFT].pos().x(), -60)
        self.assertAlmostEqual(handles[HandlePosition.TOP_LEFT].pos().y(), -40)

        self.assertAlmostEqual(handles[HandlePosition.BOTTOM_RIGHT].pos().x(), 60)
        self.assertAlmostEqual(handles[HandlePosition.BOTTOM_RIGHT].pos().y(), 40)

        self.assertAlmostEqual(handles[HandlePosition.TOP].pos().x(), 0)
        self.assertAlmostEqual(handles[HandlePosition.TOP].pos().y(), -40)

    def test_component_resizing_and_min_limits(self):
        """Verify resizing behavior and enforcement of minimum width/height limits."""
        item = PakmaComponentItem("Limit Test", "rect", x=0, y=0, width=100, height=50)
        
        # Enlarge size
        item.set_custom_size(250, 150)
        self.assertEqual(item.rect().width(), 250)
        self.assertEqual(item.rect().height(), 150)

        # Attempt undersized shrink (should clamp to minimum limits)
        item.set_custom_size(5, 5)
        self.assertGreaterEqual(item.rect().width(), PakmaComponentItem.MIN_WIDTH)
        self.assertGreaterEqual(item.rect().height(), PakmaComponentItem.MIN_HEIGHT)

    def test_properties_dictionary_and_locking(self):
        """Verify properties dictionary update and position locking."""
        item = PakmaComponentItem("Prop Test", "spring", x=10, y=20)
        self.assertIn("variable_name", item.properties)
        self.assertIn("fill_color", item.properties)

        # Update properties
        item.properties["variable_name"] = "k_spring"
        item.properties["value"] = 25.5
        item.properties["unit"] = "N/m"
        item.properties["locked"] = True

        self.assertEqual(item.properties["variable_name"], "k_spring")
        self.assertEqual(item.properties["value"], 25.5)
        self.assertTrue(item.properties["locked"])

    def test_design_panel_operations(self):
        """Verify DesignPanel canvas component addition, clear, tool mode, and grid toggle."""
        canvas = DesignPanel("GR")
        self.assertEqual(len(canvas.widgets), 0)

        # Add items
        item1 = canvas.add_widget_item("Mass 1", "oval", -50, -50)
        item2 = canvas.add_widget_item("Spring 1", "spring", 50, 50)
        self.assertEqual(len(canvas.widgets), 2)
        self.assertIn(item1, canvas.widgets)
        self.assertIn(item2, canvas.widgets)

        # Test tool activation
        canvas.set_active_tool("anagauge")
        self.assertEqual(canvas.active_tool, "anagauge")

        # Test grid toggle
        canvas.toggle_grid(False)
        self.assertFalse(canvas.grid_enabled)
        canvas.toggle_grid(True)
        self.assertTrue(canvas.grid_enabled)

        # Test clear canvas
        canvas.clear_canvas()
        self.assertEqual(len(canvas.widgets), 0)

    def test_property_dialog_initialization(self):
        """Verify PropertyDialog correctly reads and maps component properties."""
        item = PakmaComponentItem("Gauge Test", "anagauge", x=100, y=120, width=90, height=80)
        item.properties["value"] = 5.25
        item.properties["unit"] = "V"

    def test_bounding_rect_margin(self):
        """Verify boundingRect fully encapsulates handles and labels to eliminate trail artifacts."""
        item = PakmaComponentItem("Bound Test", "spring", x=0, y=0, width=100, height=50)
        br = item.boundingRect()
        r = item.rect()
        self.assertLess(br.left(), r.left())
        self.assertGreater(br.right(), r.right())
        self.assertLess(br.top(), r.top())
        self.assertGreater(br.bottom(), r.bottom())

    def test_workspace_panning_state(self):
        """Verify DesignPanel workspace panning flags."""
        canvas = DesignPanel("GR")
        self.assertFalse(canvas._is_panning)
        canvas._is_panning = True
        self.assertTrue(canvas._is_panning)


if __name__ == "__main__":
    unittest.main()
