"""
MainView — Main tabbed view containing all sub-views.

Ported from: de.uniwuerzburg.physik.pakma.gui.MainView
Original: Java View subclass with JTabbedPane containing GraphView,
          PMView, ScriptView. Also hosts the main toolbar with
          file/edit/run/mode buttons.
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk
from typing import Optional

from pakma.model.document import Document
from pakma.gui.view import View
from pakma.gui.toolbar import ToolBar
from pakma.gui.graph_view import GraphView
from pakma.gui.pm_view import PMView
from pakma.gui.script_view import ScriptView


class MainView(View):
    """
    Main view with tabbed notebook (Animation, Model, Script)
    and a top toolbar with all application actions.

    Ported from: de.uniwuerzburg.physik.pakma.gui.MainView
    """

    def __init__(self, parent, doc: Document, presentation: bool = True, **kwargs):
        super().__init__(parent, doc, presentation, **kwargs)

        self._views = []
        self._current_view: Optional[View] = None
        self._design_buttons = []

        # Create the tabbed notebook
        self._notebook = ttk.Notebook(self._center_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True)
        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Create sub-views
        self._graph_view = GraphView(self._notebook, doc, presentation, parent_view=self)
        self._pm_view = PMView(self._notebook, doc, presentation, parent_view=self)
        self._script_view = ScriptView(self._notebook, doc, presentation, parent_view=self)

        # Add tabs with icons
        self._add_tab(self._graph_view, self.LT("Animation"), "images/graphview.gif")
        self._add_tab(self._pm_view, self.LT("Model"), "images/modelview.gif")
        self._add_tab(self._script_view, self.LT("Script"), "images/scriptview.gif")

        self._views = [self._graph_view, self._pm_view, self._script_view]
        self._notebook.select(0)
        self._current_view = self._graph_view

        # Store animation panel reference
        canvas = self._graph_view.get_attribute(View.VIEW_ATTR_CANVAS)
        self.set_attribute("animationpanel", canvas)

        # Create the main toolbar
        self._create_button_bar()

        self.set_presentation_mode(presentation)

    def _add_tab(self, view: View, title: str, icon_path: str):
        """Add a tab to the notebook, attempting to load its icon."""
        # Try to load icon
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon = None

        for base in [base_dir, os.path.dirname(base_dir)]:
            full_path = os.path.join(base, icon_path)
            if os.path.exists(full_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(full_path).resize((16, 16), Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(img)
                    break
                except Exception:
                    pass

        if icon:
            self._notebook.add(view, text=f" {title}", image=icon, compound=tk.LEFT)
            # Keep reference to prevent GC
            if not hasattr(self, '_tab_icons'):
                self._tab_icons = []
            self._tab_icons.append(icon)
        else:
            self._notebook.add(view, text=f" {title}")

    def _create_button_bar(self):
        """Create the main application toolbar."""
        toolbar = ToolBar(self._top_frame, ToolBar.HORIZONTAL)

        # --- Exit ---
        btn = toolbar.add_button("images/exit.gif",
                                 command=self._on_exit,
                                 tooltip=self.LT("Closes this application"))
        toolbar.add_separator()

        # --- Mode toggle ---
        self._mode_btn = toolbar.add_toggle_button(
            "images/locked.gif",
            command=self._on_toggle_mode,
            tooltip=self.LT("Toggle presentation/design mode")
        )
        toolbar.add_separator()

        # --- File operations ---
        btn = toolbar.add_button("images/new.gif",
                                 command=self._on_new,
                                 tooltip=self.LT("Create new project"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/load.gif",
                                 command=self._on_open,
                                 tooltip=self.LT("Open existing project"))

        btn = toolbar.add_button("images/save.gif",
                                 command=self._on_save,
                                 tooltip=self.LT("Save current project"))
        self._design_buttons.append(btn)

        toolbar.add_separator()

        # --- Compile & Options ---
        self._compile_btn = toolbar.add_button(
            "images/ed_Compile.gif",
            command=self._on_compile,
            tooltip=self.LT("Compile")
        )
        self._design_buttons.append(self._compile_btn)

        btn = toolbar.add_button("images/prjoptions.gif",
                                 command=self._on_project_options,
                                 tooltip=self.LT("Change project options"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/eventlog.gif",
                                 command=self._on_event_log,
                                 tooltip=self.LT("Open event log"))
        self._design_buttons.append(btn)

        self._font_btn = toolbar.add_button(
            "images/ed_Font.gif",
            command=self._on_font,
            tooltip=self.LT("Choose display font")
        )
        self._design_buttons.append(self._font_btn)

        toolbar.add_separator()

        # --- Run/Pause ---
        self._run_btn = toolbar.add_button(
            "images/run.gif",
            command=self._on_run,
            tooltip=self.LT("Run script")
        )

        self._pause_btn = toolbar.add_button(
            "images/pause.gif",
            command=self._on_pause,
            tooltip=self.LT("Pause script")
        )

        toolbar.add_separator()

        # --- Edit operations ---
        btn = toolbar.add_button("images/ed_Copy.gif",
                                 command=self._on_copy,
                                 tooltip=self.LT("Copy selection to clipboard"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/ed_Cut.gif",
                                 command=self._on_cut,
                                 tooltip=self.LT("Cut selection to clipboard"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/ed_Paste.gif",
                                 command=self._on_paste,
                                 tooltip=self.LT("Paste clipboard content"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/ed_Undo.gif",
                                 command=self._on_undo,
                                 tooltip=self.LT("Undo changes"))
        self._design_buttons.append(btn)

        btn = toolbar.add_button("images/ed_Redo.gif",
                                 command=self._on_redo,
                                 tooltip=self.LT("Redo last undo"))
        self._design_buttons.append(btn)

        toolbar.add_separator()

        # --- Help ---
        toolbar.add_button("images/help.gif",
                           command=self._on_help,
                           tooltip=self.LT("Show help"))

        toolbar.pack(fill=tk.X)
        self._main_toolbar = toolbar

    # --- Tab handling ---

    def _on_tab_changed(self, event):
        """Handle tab selection change."""
        idx = self._notebook.index(self._notebook.select())
        if 0 <= idx < len(self._views):
            self._current_view = self._views[idx]

    def get_current_view(self) -> View:
        return self._current_view if self._current_view else self

    # --- Mode ---

    def set_presentation_mode(self, mode: bool):
        super().set_presentation_mode(mode)
        # Show/hide design-only buttons
        for btn in self._design_buttons:
            if mode:
                btn.pack_forget()
            else:
                btn.pack(side=tk.LEFT, padx=1, pady=1)
        # Propagate to sub-views
        for v in self._views:
            v.set_presentation_mode(mode)

    def _on_toggle_mode(self):
        self.set_presentation_mode(not self.is_presentation_mode)

    # --- Action callbacks (placeholders for future phases) ---

    def _on_exit(self):
        root = self.winfo_toplevel()
        root.destroy()

    def _on_new(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "New project (not implemented yet)")

    def _on_open(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Open project (not implemented yet)")

    def _on_save(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Save project (not implemented yet)")

    def _on_compile(self):
        if isinstance(self._current_view, ScriptView):
            self._current_view.compile_operation()

    def _on_project_options(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Project options (not implemented yet)")

    def _on_event_log(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Event log viewer (not implemented yet)")

    def _on_font(self):
        if isinstance(self._current_view, ScriptView):
            self._current_view.font_operation()

    def _on_run(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Run script (not implemented yet)")

    def _on_pause(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Pause script (not implemented yet)")

    def _on_copy(self):
        if self._current_view:
            self._current_view.copy_to_pasteboard()

    def _on_cut(self):
        if self._current_view:
            self._current_view.cut_to_pasteboard()

    def _on_paste(self):
        if self._current_view:
            self._current_view.paste_from_pasteboard()

    def _on_undo(self):
        if self._current_view:
            self._current_view.undo_operation()

    def _on_redo(self):
        if self._current_view:
            self._current_view.redo_operation()

    def _on_help(self):
        from pakma.util.event_log import EventLog
        EventLog.instance().put(EventLog.MSG, self, "Help viewer (not implemented yet)")
