"""
View — Base class for all view panels.

Ported from: de.uniwuerzburg.physik.pakma.gui.View
Original: Java JPanel subclass with Observer, Command pattern, toolbar/buttonbar,
          presentation/design mode toggle, and clipboard operations.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Dict, List

from pakma.model.document import Document
from pakma.util.localized_strings import LocalizedStrings


class CommandProcessor:
    """
    Simple undo/redo command processor.
    Phase 1: placeholder implementation.
    """

    def __init__(self):
        self._undo_stack: list = []
        self._redo_stack: list = []

    def execute(self, command):
        self._undo_stack.append(command)
        self._redo_stack.clear()
        if hasattr(command, 'execute'):
            command.execute(None)

    def undo(self):
        if self._undo_stack:
            cmd = self._undo_stack.pop()
            self._redo_stack.append(cmd)
            if hasattr(cmd, 'undo'):
                cmd.undo()

    def redo(self):
        if self._redo_stack:
            cmd = self._redo_stack.pop()
            self._undo_stack.append(cmd)
            if hasattr(cmd, 'redo'):
                cmd.redo()

    def undo_count(self) -> int:
        return len(self._undo_stack)

    def redo_count(self) -> int:
        return len(self._redo_stack)


class View(ttk.Frame):
    """
    Base class for all view panels in the application.

    Provides:
    - Document binding with observer pattern
    - Toolbar and button bar management
    - Presentation/design mode toggle
    - Command processor for undo/redo
    - Clipboard operations (placeholder)
    - Localization shortcut LT()

    Layout (matching Java BorderLayout):
        [ButtonBar - TOP]
        [ToolBar - LEFT] [Content - CENTER]

    Ported from: de.uniwuerzburg.physik.pakma.gui.View
    """

    VIEW_ATTR_TOOL = "tool"
    VIEW_ATTR_CANVAS = "canvas"
    VIEW_ATTR_CLIPBOARD = "clipboard"
    VIEW_ATTR_SELECTION = "selection"

    def __init__(self, parent, doc: Document, presentation: bool = True,
                 parent_view: Optional['View'] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self._parent_view = parent_view
        self._presentation = presentation
        self._attributes: Dict[str, Any] = {}
        self._cmd_proc = CommandProcessor()
        self._doc = doc
        self._toolbar: Optional[ttk.Frame] = None
        self._buttonbar: Optional[ttk.Frame] = None
        self._content_pane: Optional[tk.Widget] = None

        # Layout frames
        self._top_frame = ttk.Frame(self)
        self._left_frame = ttk.Frame(self)
        self._center_frame = ttk.Frame(self)

        self._top_frame.pack(side=tk.TOP, fill=tk.X)
        self._left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self._center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Register as document observer
        if self._doc:
            self._doc.add_observer(self._on_document_changed)

    # --- Localization shortcut ---

    @staticmethod
    def LT(text: str) -> str:
        return LocalizedStrings.get(text)

    # --- Document ---

    @property
    def doc(self) -> Document:
        return self._doc

    def get_document(self) -> Document:
        return self._doc

    def set_document(self, doc: Document):
        if self._doc:
            self._doc.remove_observer(self._on_document_changed)
        self._doc = doc
        if self._doc:
            self._doc.add_observer(self._on_document_changed)

    def _on_document_changed(self, observable, arg):
        """Called when document changes. Override in subclasses."""
        self.update_view(observable, arg)

    def update_view(self, observable, arg):
        """Override in subclasses to respond to document changes."""
        pass

    # --- Attributes ---

    def set_attribute(self, key: str, value: Any):
        if value is None:
            self._attributes.pop(key, None)
        else:
            self._attributes[key] = value

    def get_attribute(self, key: str) -> Any:
        return self._attributes.get(key)

    # --- Command processor ---

    def execute(self, command):
        self._cmd_proc.execute(command)

    def get_command_processor(self) -> CommandProcessor:
        return self._cmd_proc

    # --- Toolbar management ---

    def set_button_bar(self, buttonbar):
        """Set the top button bar."""
        if self._buttonbar:
            self._buttonbar.pack_forget()
        if buttonbar:
            buttonbar.pack(in_=self._top_frame, fill=tk.X)
        self._buttonbar = buttonbar

    def set_toolbar(self, toolbar):
        """Set the left-side toolbar."""
        if self._toolbar:
            self._toolbar.pack_forget()
        if toolbar:
            toolbar.pack(in_=self._left_frame, fill=tk.Y, expand=True)
        self._toolbar = toolbar

    def set_content_pane(self, pane):
        """Set the central content area."""
        if self._content_pane:
            self._content_pane.pack_forget()
        if pane:
            pane.pack(in_=self._center_frame, fill=tk.BOTH, expand=True)
        self._content_pane = pane

    def get_content_pane(self):
        return self._content_pane

    # --- Mode ---

    @property
    def is_presentation_mode(self) -> bool:
        return self._presentation

    def set_presentation_mode(self, mode: bool):
        self._presentation = mode

    def get_current_view(self) -> 'View':
        return self

    # --- Clipboard operations (placeholder) ---

    def copy_to_pasteboard(self):
        pass

    def cut_to_pasteboard(self):
        pass

    def paste_from_pasteboard(self):
        pass

    def undo_operation(self):
        self._cmd_proc.undo()

    def redo_operation(self):
        self._cmd_proc.redo()

    def is_copy_enabled(self) -> bool:
        return False

    def is_cut_enabled(self) -> bool:
        return False

    def is_paste_enabled(self) -> bool:
        clipboard = self.get_attribute(self.VIEW_ATTR_CLIPBOARD)
        return clipboard is not None

    def is_undo_enabled(self) -> bool:
        return self._cmd_proc.undo_count() > 0

    def is_redo_enabled(self) -> bool:
        return self._cmd_proc.redo_count() > 0
