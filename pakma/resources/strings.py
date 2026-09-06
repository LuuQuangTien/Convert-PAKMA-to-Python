"""
Internationalization and String Constants for PyPAKMA.
Ported from: de.uniwuerzburg.physik.pakma.util.LocalizedStrings & lang/default.res
"""

from __future__ import annotations
from typing import Dict


class AppStrings:
    # App Info
    APP_TITLE = "JPAKMA"
    APP_SUBTITLE = "Physics Simulation & Data Acquisition Studio"
    
    # Tabs
    TAB_ANIMATION = "Animation"
    TAB_ANIMATION_TOOLTIP = "Graphical representation"
    TAB_MODEL = "Model"
    TAB_MODEL_TOOLTIP = "Physical model"
    TAB_SCRIPT = "Script"
    TAB_SCRIPT_TOOLTIP = "PASCL script"
    TAB_EXTENSIONS = "Extensions"

    # Toolbars
    TOOL_EXIT = "Exit Application"
    TOOL_MODE = "Toggle presentation/design mode"
    TOOL_NEW = "Create new project"
    TOOL_LOAD = "Open existing project"
    TOOL_SAVE = "Save current project"
    TOOL_COMPILE = "Compile PASCL script"
    TOOL_PRJ_OPTIONS = "Change project options"
    TOOL_MEASLE = "Setup measurement sources (pyserial / CASSY)"
    TOOL_EVENTLOG = "Open event log"
    TOOL_SNAPSHOT = "Take a snapshot of the visible panel"
    TOOL_FONT = "Choose display font"
    TOOL_RUN = "Run script / simulation"
    TOOL_PAUSE = "Pause script / simulation"
    TOOL_COPY = "Copy selection to clipboard"
    TOOL_CUT = "Cut selection to clipboard"
    TOOL_PASTE = "Paste clipboard content"
    TOOL_UNDO = "Undo changes"
    TOOL_REDO = "Redo last undo"
    TOOL_HELP = "Show help"

    # Canvas
    CANVAS_DELETE_ALL = "Delete all objects on this panel"
    CANVAS_TOGGLE_GRID = "Toggle grid"
    CANVAS_CONTROL_CENTER = "Object Control Center"
    CANVAS_EDIT_GROUPS = "Edit groups"
    CANVAS_CLEAR = "Clear canvas from stamped objects"

    # Status
    STATUS_READY = "Ready"
    STATUS_RUNNING = "Simulation Running"
    STATUS_PAUSED = "Simulation Paused"
    STATUS_RESET = "Simulation Reset"


def LT(key: str, default: str | None = None) -> str:
    """Localized Text lookup helper."""
    return getattr(AppStrings, key, default or key)
