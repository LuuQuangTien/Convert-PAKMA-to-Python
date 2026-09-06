"""
Application — Singleton application controller.

Ported from: de.uniwuerzburg.physik.pakma.gui.Application
Original: Abstract Java class managing document, frame, resources, and params.
"""

from __future__ import annotations
import os
import sys
from typing import Any, Optional, Dict, List, Callable

from pakma.model.document import Document
from pakma.util.event_log import EventLog
from pakma.util.localized_strings import LocalizedStrings


class Application:
    """
    Singleton application controller.

    Manages the Document, application parameters, global attributes,
    and resource loading. This is the Python equivalent of the Java
    Application abstract class.
    """

    _instance: Optional['Application'] = None
    _frame = None

    def __init__(self, args: Optional[List[str]] = None):
        if Application._instance is not None:
            return
        Application._instance = self

        self._args = args or []
        self._params: Dict[str, str] = {}
        self._attributes: Dict[str, Any] = {}
        self._attribute_listeners: List[Callable] = []
        self._doc: Optional[Document] = None

        # Base directory for resources
        self._base_dir = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))

        # Initialize event log
        EventLog.instance().set_priority_threshold(EventLog.MSG)

        # Log startup
        try:
            user = os.environ.get("USERNAME", os.environ.get("USER", "User"))
            EventLog.instance().put(EventLog.MSG, self,
                                    f"Hello {user}, hope you're doing fine")
        except Exception:
            EventLog.instance().put(EventLog.MSG, self, "Application started")

    @classmethod
    def get_application(cls) -> Optional['Application']:
        return cls._instance

    @classmethod
    def is_applet(cls) -> bool:
        """Always False — we're a desktop application."""
        return False

    # --- Document ---

    def get_document(self) -> Document:
        if self._doc is None:
            self._doc = self.create_document()
        return self._doc

    def create_document(self) -> Document:
        return Document()

    # --- Parameters ---

    def get_params(self) -> Dict[str, str]:
        return self._params

    def get_param(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._params.get(key, default)

    def set_param(self, key: str, value: str):
        self._params[key] = value

    def get_args(self) -> List[str]:
        return self._args

    # --- Global attributes ---

    @classmethod
    def set_attribute(cls, key: str, value: Any):
        app = cls.get_application()
        if app is None:
            return
        if value is None:
            app._attributes.pop(key, None)
        else:
            app._attributes[key] = value
        app._notify_attribute_listeners(key)

    @classmethod
    def get_attribute(cls, key: str, default: Any = None) -> Any:
        app = cls.get_application()
        if app is None:
            return default
        return app._attributes.get(key, default)

    def add_attribute_listener(self, listener: Callable):
        if listener not in self._attribute_listeners:
            self._attribute_listeners.append(listener)

    def remove_attribute_listener(self, listener: Callable):
        if listener in self._attribute_listeners:
            self._attribute_listeners.remove(listener)

    def _notify_attribute_listeners(self, key: str):
        for listener in self._attribute_listeners:
            try:
                listener(key)
            except Exception:
                pass

    # --- Resources ---

    @classmethod
    def get_resource(cls, name: str) -> Optional[str]:
        """Get absolute path to a resource file."""
        app = cls.get_application()
        if app is None:
            return None

        # Try relative to base dir
        path = os.path.join(app._base_dir, name)
        if os.path.exists(path):
            return path

        # Try relative to CWD
        if os.path.exists(name):
            return os.path.abspath(name)

        return None

    # --- Frame ---

    @classmethod
    def get_frame(cls):
        return cls._frame

    @classmethod
    def set_frame(cls, frame):
        cls._frame = frame

    def set_frame_title(self, title: Optional[str]):
        if self._frame and hasattr(self._frame, 'set_title'):
            self._frame.set_title(title)

    def set_title(self, title: str):
        """Override in subclass."""
        pass

    # --- Localization shortcut ---

    @staticmethod
    def LT(text: str) -> str:
        """Localized text shortcut."""
        return LocalizedStrings.get(text)

    # --- Version ---

    _version = "1.38.9"

    @classmethod
    def get_version(cls) -> str:
        return cls._version

    def __repr__(self):
        return f"Application(version={self._version})"
