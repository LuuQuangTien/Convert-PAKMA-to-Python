"""
MainFrame — Main application window.

Ported from: de.uniwuerzburg.physik.pakma.gui.MainFrame
Original: Java JFrame containing the MainView, with title bar,
          close handler, and resize tracking.
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from pakma.model.document import Document
from pakma.gui.main_view import MainView


class MainFrame:
    """
    Main application window.

    Creates a Tk root window containing the MainView.
    Manages the window title, size, and close behavior.

    Ported from: de.uniwuerzburg.physik.pakma.gui.MainFrame
    """

    APP_TITLE = "JPAKMA"

    def __init__(self, doc: Document, presentation: bool = True):
        self._doc = doc

        # Create root window
        self._root = tk.Tk()
        self._root.title(self.APP_TITLE)
        self._root.geometry("900x650")
        self._root.minsize(600, 400)

        # Set icon if available
        self._set_window_icon()

        # Apply modern theme
        self._apply_theme()

        # Create main view
        self._main_view = MainView(self._root, doc, presentation)
        self._main_view.pack(fill=tk.BOTH, expand=True)

        # Window close handler
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Register document observer for title updates
        self._doc.add_observer(self._on_document_changed)

        # Center window on screen
        self._center_window()

    def _set_window_icon(self):
        """Try to set the window icon from jpakma-logo.png."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_paths = [
            os.path.join(base_dir, "images", "jpakma-logo.png"),
            os.path.join(os.path.dirname(base_dir), "images", "jpakma-logo.png"),
        ]
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(path)
                    photo = ImageTk.PhotoImage(img)
                    self._root.iconphoto(True, photo)
                    self._root._icon = photo  # Keep reference
                    break
                except Exception:
                    pass

    def _apply_theme(self):
        """Apply a clean modern theme."""
        style = ttk.Style()

        # Try to use a modern theme
        available = style.theme_names()
        for theme in ['clam', 'alt', 'vista', 'xpnative']:
            if theme in available:
                style.theme_use(theme)
                break

        # Customize styles
        style.configure("TButton", padding=2)
        style.configure("TFrame", background="#F5F5F5")
        style.configure("TNotebook", background="#F5F5F5")
        style.configure("TNotebook.Tab", padding=[8, 4])
        style.configure("Toolbutton", padding=2)

    def _center_window(self):
        """Center the window on screen."""
        self._root.update_idletasks()
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self._root.geometry(f"{w}x{h}+{x}+{y}")

    def _on_close(self):
        """Handle window close — check for unsaved changes."""
        if self._doc.is_modified():
            result = messagebox.askyesnocancel(
                "JPAKMA",
                "Document has been modified. Save before closing?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes — save (placeholder)
                pass
        self._root.destroy()

    def _on_document_changed(self, observable, arg):
        """Update window title when document changes."""
        self.set_title(self._doc.get_title())

    def set_title(self, title: Optional[str]):
        """Set the window title."""
        if title:
            self._root.title(f"{self.APP_TITLE} - {title}")
        else:
            self._root.title(self.APP_TITLE)

    def get_document(self) -> Document:
        return self._doc

    @property
    def root(self) -> tk.Tk:
        return self._root

    @property
    def main_view(self) -> MainView:
        return self._main_view

    def run(self):
        """Start the Tkinter main event loop."""
        self._root.mainloop()
