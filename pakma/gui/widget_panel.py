"""
WidgetPanel — Custom canvas for drawing widgets.

Ported from: de.uniwuerzburg.physik.pakma.gui.widget.WidgetPanel
Original: Java JPanel subclass with custom painting, anti-aliasing,
          grid overlay, and widget rendering.

Phase 1: Basic canvas with background and optional grid.
"""

from __future__ import annotations
import tkinter as tk
from typing import Optional


class WidgetPanel(tk.Canvas):
    """
    Canvas for rendering physics simulation widgets.

    Phase 1 implementation provides:
    - White background
    - Optional grid overlay
    - Basic mouse event hooks (placeholder)

    Future phases will add:
    - Widget rendering
    - Selection management
    - Drag-and-drop
    - Anti-aliased drawing
    """

    GRID_SIZE = 16

    def __init__(self, parent, panel_id: str = "GR", **kwargs):
        kwargs.setdefault("bg", "white")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

        self._panel_id = panel_id
        self._show_grid = False
        self._grid_size = self.GRID_SIZE
        self._anti_aliased = True
        self._widgets = []  # Will hold Widget objects in future phases

        # Bind resize to redraw grid
        self.bind("<Configure>", self._on_configure)

    @property
    def panel_id(self) -> str:
        return self._panel_id

    @property
    def show_grid(self) -> bool:
        return self._show_grid

    @show_grid.setter
    def show_grid(self, value: bool):
        self._show_grid = value
        self._draw_grid()

    def toggle_grid(self):
        self.show_grid = not self.show_grid

    def set_anti_aliased(self, value: bool):
        self._anti_aliased = value

    def _on_configure(self, event):
        """Redraw grid when canvas is resized."""
        if self._show_grid:
            self._draw_grid()

    def _draw_grid(self):
        """Draw or clear the grid overlay."""
        self.delete("grid")

        if not self._show_grid:
            return

        w = self.winfo_width()
        h = self.winfo_height()
        grid_color = "#E8E8E8"

        for x in range(0, w, self._grid_size):
            self.create_line(x, 0, x, h, fill=grid_color, tags="grid")

        for y in range(0, h, self._grid_size):
            self.create_line(0, y, w, y, fill=grid_color, tags="grid")

        # Grid should be behind everything
        self.tag_lower("grid")

    def clear_all(self):
        """Remove all drawn items."""
        self.delete("all")
        self._widgets.clear()
        if self._show_grid:
            self._draw_grid()

    def get_widget_count(self) -> int:
        return len(self._widgets)
