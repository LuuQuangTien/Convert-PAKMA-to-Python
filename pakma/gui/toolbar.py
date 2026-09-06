"""
ToolBar — Toolbar container with icon buttons.

Ported from: de.uniwuerzburg.physik.pakma.gui.ToolBar
Original: Java JToolBar subclass with addButton, addRadioButton, addToggleButton.
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any

from PIL import Image, ImageTk


class ToolBar(ttk.Frame):
    """
    Toolbar that hosts icon buttons in horizontal or vertical orientation.

    Buttons are loaded from GIF icon files in the images/ directory.
    Supports regular buttons, toggle buttons, and radio button groups.
    """

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __init__(self, parent, orientation: str = HORIZONTAL, **kwargs):
        super().__init__(parent, **kwargs)
        self._orientation = orientation
        self._buttons = []
        self._radio_var = tk.StringVar(value="")
        self._icon_cache: dict = {}
        self._base_dir = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))

        # Style
        self.configure(padding=2)

    def _load_icon(self, image_path: str, size: int = 24) -> Optional[ImageTk.PhotoImage]:
        """Load an icon image, trying multiple base paths."""
        if image_path in self._icon_cache:
            return self._icon_cache[image_path]

        # Try paths
        paths_to_try = [
            os.path.join(self._base_dir, image_path),
            os.path.join(os.path.dirname(self._base_dir), image_path),
            image_path,
        ]

        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._icon_cache[image_path] = photo
                    return photo
                except Exception:
                    pass

        return None

    def add_button(self, image: str, command: Optional[Callable] = None,
                   tooltip: Optional[str] = None) -> ttk.Button:
        """Add a regular push button with icon."""
        icon = self._load_icon(image)
        btn = ttk.Button(self, command=command or (lambda: None))

        if icon:
            btn.configure(image=icon)
            btn._icon = icon  # Keep reference to prevent GC
        else:
            # Fallback: use filename as text
            name = os.path.splitext(os.path.basename(image))[0]
            btn.configure(text=name, width=6)

        if tooltip:
            self._create_tooltip(btn, tooltip)

        self._pack_button(btn)
        self._buttons.append(btn)
        return btn

    def add_toggle_button(self, image: str, command: Optional[Callable] = None,
                          tooltip: Optional[str] = None) -> ttk.Checkbutton:
        """Add a toggle (check) button with icon."""
        var = tk.BooleanVar(value=False)
        icon = self._load_icon(image)

        btn = ttk.Checkbutton(self, variable=var,
                              command=command or (lambda: None),
                              style="Toolbutton")
        btn._var = var

        if icon:
            btn.configure(image=icon)
            btn._icon = icon
        else:
            name = os.path.splitext(os.path.basename(image))[0]
            btn.configure(text=name)

        if tooltip:
            self._create_tooltip(btn, tooltip)

        self._pack_button(btn)
        self._buttons.append(btn)
        return btn

    def add_radio_button(self, image: str, command: Optional[Callable] = None,
                         value: str = "", tooltip: Optional[str] = None) -> ttk.Radiobutton:
        """Add a radio button with icon (mutually exclusive)."""
        icon = self._load_icon(image)

        if not value:
            value = os.path.splitext(os.path.basename(image))[0]

        btn = ttk.Radiobutton(self, variable=self._radio_var, value=value,
                              command=command or (lambda: None),
                              style="Toolbutton")

        if icon:
            btn.configure(image=icon)
            btn._icon = icon
        else:
            btn.configure(text=value)

        if tooltip:
            self._create_tooltip(btn, tooltip)

        self._pack_button(btn)
        self._buttons.append(btn)
        return btn

    def add_separator(self):
        """Add a visual separator between button groups."""
        sep = ttk.Separator(self,
                            orient=tk.VERTICAL if self._orientation == self.HORIZONTAL
                            else tk.HORIZONTAL)
        if self._orientation == self.HORIZONTAL:
            sep.pack(side=tk.LEFT, padx=4, fill=tk.Y, pady=2)
        else:
            sep.pack(side=tk.TOP, pady=4, fill=tk.X, padx=2)

    def _pack_button(self, btn):
        """Pack a button according to orientation."""
        if self._orientation == self.HORIZONTAL:
            btn.pack(side=tk.LEFT, padx=1, pady=1)
        else:
            btn.pack(side=tk.TOP, padx=1, pady=1)

    def _create_tooltip(self, widget, text: str):
        """Create a simple tooltip for a widget."""

        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tooltip, text=text, background="#FFFFDD",
                             relief=tk.SOLID, borderwidth=1,
                             font=("Segoe UI", 9))
            label.pack()
            widget._tooltip_window = tooltip

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip_window') and widget._tooltip_window:
                widget._tooltip_window.destroy()
                widget._tooltip_window = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def get_buttons(self):
        return list(self._buttons)
