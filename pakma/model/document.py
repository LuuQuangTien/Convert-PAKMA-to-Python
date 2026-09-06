"""
Document — Container for Model objects with Observer/transaction support.

Ported from: de.uniwuerzburg.physik.pakma.model.Document
Original: Java Observable with Hashtable of Models, notification queue,
          transaction batching, and document metadata (title, author, dates).
"""

from __future__ import annotations
import threading
import time
from typing import Any, Optional, Dict, Set, Iterator, Callable, List


class Document:
    """
    Document is the top-level container that holds all Model instances.
    It supports observer notifications, transaction batching, and
    document metadata.

    Ported from: de.uniwuerzburg.physik.pakma.model.Document
    """

    # Notification keys
    NOTIFY_DOCUMENT_WILL_LOAD = "document:willload"
    NOTIFY_DOCUMENT_LOADED = "document:loaded"
    NOTIFY_DOCUMENT_CLEAR = "document:clear"
    NOTIFY_DOCUMENT_MODEL_ADD = "document:add"
    NOTIFY_DOCUMENT_MODEL_REMOVE = "document:remove"
    DEFAULT_MODEL_PREFIX = "Obj"

    def __init__(self, context=None):
        self._models: Dict[str, Any] = {}
        self._observers: List[Callable] = []
        self._changed = False
        self._modified = False
        self._lock = threading.Lock()

        # Transaction support
        self._queue_level = 0
        self._event_queue: List[tuple] = []

        # Metadata
        self._title: Optional[str] = None
        self._author: Optional[str] = None
        self._creator: Optional[str] = None
        self._context = context

        # Notification subscribers
        self._notification_subscribers: Dict[str, List[Callable]] = {}

    # --- Observer pattern ---

    def add_observer(self, observer: Callable):
        """Register an observer callback. Called with (document, model) on change."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable):
        if observer in self._observers:
            self._observers.remove(observer)

    def delete_observer(self, observer: Callable):
        """Java-compatible alias."""
        self.remove_observer(observer)

    def set_changed(self):
        self._changed = True

    def clear_changed(self):
        self._changed = False

    def notify_observers(self, arg: Any = None):
        if self._changed:
            for obs in list(self._observers):
                try:
                    obs(self, arg)
                except Exception as e:
                    from pakma.util.event_log import EventLog
                    EventLog.instance().put(EventLog.ERROR, self,
                                            f"Document observer failed: {e}")
            self._changed = False

    # --- Transaction support ---

    def is_transaction(self) -> bool:
        return self._queue_level > 0

    def begin_transaction(self) -> int:
        self._queue_level += 1
        return self._queue_level

    def end_transaction(self):
        if self._queue_level > 0:
            self._queue_level -= 1
            if self._queue_level == 0:
                self._fire_queued_events()

    def _fire_queued_events(self):
        """Dispatch all queued events."""
        events = list(self._event_queue)
        self._event_queue.clear()
        for source, arg in events:
            try:
                if source is self:
                    self.set_changed()
                    self.notify_observers(arg)
                else:
                    source.set_changed()
                    source.notify_observers(arg)
            except Exception as e:
                from pakma.util.event_log import EventLog
                EventLog.instance().put(EventLog.ERROR, self,
                                        f"Event dispatch failed: {e}")

    def fire_model_change_event(self, model):
        """Fire or queue a model change event."""
        if self._queue_level > 0:
            self._event_queue.append((model, None))
        else:
            model.notify_observers()

    def fire_change_event(self, model):
        """Fire or queue a document change event."""
        self.set_changed()
        if self._queue_level > 0:
            self._event_queue.append((self, model))
        else:
            self.notify_observers(model)

    # --- Modified flag ---

    @property
    def modified(self) -> bool:
        return self._modified

    def is_modified(self) -> bool:
        return self._modified

    def set_modified(self, value: bool = True):
        self._modified = value

    def clear_modified(self):
        self._modified = False

    # --- Metadata ---

    @property
    def title(self) -> Optional[str]:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def get_title(self) -> Optional[str]:
        return self._title

    def set_title(self, title: str):
        self._title = title

    @property
    def author(self) -> Optional[str]:
        return self._author

    @author.setter
    def author(self, value: str):
        self._author = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    def get_context(self):
        return self._context

    def set_context(self, ctx):
        self._context = ctx

    # --- Model CRUD ---

    def put(self, model) -> bool:
        """Add or replace a Model in the document."""
        if model is None:
            return False

        name = model.get_name()
        if name is None:
            return False

        with self._lock:
            self._models[name] = model

        self.set_modified()
        self.fire_change_event(model)
        return True

    def get(self, name: str):
        """Retrieve a Model by name."""
        if isinstance(name, str):
            return self._models.get(name)
        return self._models.get(str(name))

    def get_keys(self) -> Set[str]:
        return set(self._models.keys())

    def remove(self, name_or_model) -> Any:
        """Remove a Model by name or Model instance."""
        if name_or_model is None:
            return None

        name = name_or_model
        if hasattr(name_or_model, 'get_name'):
            name = name_or_model.get_name()

        with self._lock:
            model = self._models.pop(str(name), None)

        if model is not None:
            self.set_modified()
            self.fire_change_event(model)
        return model

    def clear(self):
        """Remove all models."""
        with self._lock:
            self._models.clear()
        self.set_modified()
        self.fire_change_event(None)

    def contains(self, name_or_model) -> bool:
        if name_or_model is None:
            return False
        if isinstance(name_or_model, str):
            return name_or_model in self._models
        if hasattr(name_or_model, 'get_name'):
            return name_or_model.get_name() in self._models
        return str(name_or_model) in self._models

    def add_model(self, model) -> bool:
        """Alias for put."""
        return self.put(model)

    def get_model(self, name: str):
        """Alias for get."""
        return self.get(name)

    def get_model_count(self) -> int:
        """Alias for get_count."""
        return self.get_count()

    def get_count(self) -> int:
        return len(self._models)

    def is_empty(self) -> bool:
        return self.get_count() == 0

    def get_iterator(self) -> Iterator[str]:
        return iter(list(self._models.keys()))

    def get_default_name(self, prefix: Optional[str] = None) -> Optional[str]:
        """Generate a unique name for a new Model."""
        if prefix is None:
            prefix = self.DEFAULT_MODEL_PREFIX
        else:
            # Extract last part after '.'
            idx = prefix.rfind('.') + 1
            if idx > 0:
                prefix = prefix[idx:]
            if not prefix:
                prefix = self.DEFAULT_MODEL_PREFIX

        for i in range(1, self.get_count() + 2):
            name = f"{prefix}{i}"
            if name not in self._models:
                return name
        return None

    def __repr__(self):
        return f"Document(title={self._title!r}, models={len(self._models)})"
