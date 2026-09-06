"""
Model — Observable key-value attribute store.

Ported from: de.uniwuerzburg.physik.pakma.model.Model
Original: Java Observable pattern with Hashtable-based attributes.

Python equivalent uses a custom observer pattern with dict-based attributes
and typed accessors (get_int, get_double, get_string, get_color, get_boolean).
"""

from __future__ import annotations
import threading
from typing import Any, Optional, Set, Dict, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .document import Document


class AttrGroup:
    """
    Attribute group — allows grouping related attributes so that
    change notifications can be checked per-group.
    (Ported from Model.AttrGroup inner class)
    """

    def __init__(self, name: Optional[str] = None):
        self._name = name
        self._changed = False

    @property
    def name(self) -> Optional[str]:
        return self._name

    def has_changed(self) -> bool:
        return self._changed

    def set_changed(self):
        self._changed = True

    def clear_changed(self):
        self._changed = False


class ModelAttr:
    """
    Single attribute entry with key, data, and group membership.
    (Ported from Model.ModelAttr inner class)
    """

    def __init__(self, key: Any, data: Any = None):
        self._key = key
        self._data = data
        self._group: Optional[AttrGroup] = None

    @property
    def key(self) -> Any:
        return self._key

    @property
    def data(self) -> Any:
        return self._data

    @data.setter
    def data(self, value: Any):
        self._data = value

    @property
    def group(self) -> Optional[AttrGroup]:
        return self._group

    @group.setter
    def group(self, g: Optional[AttrGroup]):
        self._group = g

    @property
    def group_name(self) -> Optional[str]:
        return self._group.name if self._group else None

    def has_changed(self) -> bool:
        return self._group.has_changed() if self._group else True

    def set_changed(self):
        if self._group:
            self._group.set_changed()

    def clear_changed(self):
        if self._group:
            self._group.clear_changed()


class Model:
    """
    Observable key-value attribute store.

    This is the core data model class that stores widget/component properties
    as key-value pairs. Observers are notified when attributes change.

    Ported from: de.uniwuerzburg.physik.pakma.model.Model
    """

    def __init__(self, doc_or_name: Any = None, name: Optional[str] = None):
        if isinstance(doc_or_name, str) and name is None:
            self._doc = None
            self._name = doc_or_name
        else:
            self._doc = doc_or_name
            self._name = name
        self._flags = 0
        self._attributes: Dict[str, ModelAttr] = {}
        self._observers: list = []
        self._lock = threading.Lock()
        self._changed = False
        self._default_group = AttrGroup(None)
        self._groups: Dict[str, AttrGroup] = {}
        self._access_listeners: list = []

    # --- Observer pattern ---

    def add_observer(self, observer: Callable):
        """Register an observer callback. Called with (model, arg) on change."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable):
        """Unregister an observer callback."""
        if observer in self._observers:
            self._observers.remove(observer)

    def delete_observer(self, observer: Callable):
        """Alias for remove_observer (Java compatibility)."""
        self.remove_observer(observer)

    def set_changed(self):
        self._changed = True

    def clear_changed(self):
        self._changed = False

    def has_changed(self) -> bool:
        return self._changed

    def notify_observers(self, arg: Any = None):
        """Notify all observers and clear group changed flags."""
        if self._changed:
            for obs in list(self._observers):
                try:
                    obs(self, arg)
                except Exception as e:
                    from pakma.util.event_log import EventLog
                    EventLog.instance().put(EventLog.ERROR, self,
                                            f"Observer notification failed: {e}")
            self._changed = False

        # Clear group changed flags
        self._default_group.clear_changed()
        for group in self._groups.values():
            group.clear_changed()

    # --- Properties ---

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def doc(self) -> 'Document':
        return self._doc

    @property
    def flags(self) -> int:
        return self._flags

    @flags.setter
    def flags(self, value: int):
        self._flags = value

    def get_count(self) -> int:
        return len(self._attributes)

    def get_name(self) -> Optional[str]:
        """Java-compatible getter."""
        return self._name

    def get_id(self) -> Optional[str]:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_document(self) -> 'Document':
        """Java-compatible getter."""
        return self._doc

    # --- Attribute group management ---

    def assign_group(self, key: str, group_name: str) -> bool:
        """Assign an attribute to a named group."""
        if key not in self._attributes or group_name is None:
            return False
        attr = self._attributes[key]
        if group_name not in self._groups:
            self._groups[group_name] = AttrGroup(group_name)
        attr.group = self._groups[group_name]
        return True

    def get_group_name(self, key: str) -> Optional[str]:
        attr = self._attributes.get(key)
        return attr.group_name if attr else None

    def has_group_changed(self, group: Optional[str]) -> bool:
        if group is None:
            return self._default_group.has_changed()
        g = self._groups.get(group)
        return g.has_changed() if g else False

    def has_attr_changed(self, key: str) -> bool:
        attr = self._attributes.get(key)
        return attr.has_changed() if attr else False

    # --- Transaction support ---

    def begin_transaction(self):
        self._doc.begin_transaction()

    def end_transaction(self):
        self._doc.end_transaction()

    # --- Change event ---

    def fire_change_event(self):
        """Notify document and observers of a change."""
        self.set_changed()
        if self._doc and hasattr(self._doc, 'fire_model_change_event'):
            self._doc.fire_model_change_event(self)
        else:
            self.notify_observers()

    # --- Core CRUD ---

    def _put_value(self, key: str, value: Any, notify: bool = True) -> Any:
        """Internal put with optional notification."""
        with self._lock:
            attr = self._attributes.get(key)
            if attr is None:
                old = None
                attr = ModelAttr(key, value)
                attr.group = self._default_group
                self._attributes[key] = attr
            else:
                old = attr.data
                attr.data = value
            attr.set_changed()

        if self._doc and hasattr(self._doc, 'set_modified'):
            self._doc.set_modified()
        return old

    def put(self, key: str, value: Any) -> Any:
        """Set an attribute and fire change event."""
        old = self._put_value(key, value, True)
        self.fire_change_event()
        return old

    def put_silent(self, key: str, value: Any) -> Any:
        """Set an attribute without firing change event."""
        return self._put_value(key, value, False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get an attribute value."""
        if key is None:
            return default
        attr = self._attributes.get(key)
        return attr.data if attr else default

    def get_silent(self, key: str, default: Any = None) -> Any:
        """Get without triggering access listeners."""
        if key is None:
            return default
        attr = self._attributes.get(key)
        return attr.data if attr else default

    def contains(self, key: str) -> bool:
        return key is not None and key in self._attributes

    def remove(self, key: str) -> Any:
        """Remove an attribute and fire change event."""
        if key is None:
            return None
        attr = self._attributes.pop(key, None)
        if attr is not None:
            self._doc.set_modified()
            attr.set_changed()
            self.fire_change_event()
            return attr.data
        return None

    def remove_silent(self, key: str) -> Any:
        """Remove without firing change event."""
        if key is None:
            return None
        attr = self._attributes.pop(key, None)
        if attr is not None:
            self._doc.set_modified()
            attr.set_changed()
            return attr.data
        return None

    def iterator(self):
        """Return iterator over attribute keys."""
        return iter(list(self._attributes.keys()))

    def get_attribute_keys(self) -> Set[str]:
        return set(self._attributes.keys())

    # --- Typed accessors ---

    def get_int(self, key: str, default: int = 0) -> int:
        o = self.get(key)
        if o is None:
            return default
        try:
            return int(o)
        except (ValueError, TypeError):
            return default

    def set_int(self, key: str, value: int):
        self.put(key, value)

    def get_double(self, key: str, default: float = 0.0) -> float:
        o = self.get(key)
        if o is None:
            return default
        try:
            return float(o)
        except (ValueError, TypeError):
            return default

    def set_double(self, key: str, value: float):
        self.put(key, value)

    def get_string(self, key: str, default: str = "") -> str:
        o = self.get(key)
        return str(o) if o is not None else default

    def set_string(self, key: str, value: str):
        self.put(key, value)

    def get_color(self, key: str, default: str = "#000000") -> str:
        """Get color as hex string (e.g. '#FF0000')."""
        o = self.get(key)
        if o is None:
            return default
        if isinstance(o, str):
            return o
        return default

    def set_color(self, key: str, color: str):
        self.put(key, color)

    def get_boolean(self, key: str, default: bool = False) -> bool:
        o = self.get(key)
        if o is None:
            return default
        try:
            if isinstance(o, bool):
                return o
            return int(o) == 1
        except (ValueError, TypeError):
            return default

    def set_boolean(self, key: str, value: bool):
        self.put(key, 1 if value else 0)

    def get_point(self, key: str, default=None):
        """Get a (x, y) tuple."""
        o = self.get(key)
        if o is None:
            return default
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            return (float(o[0]), float(o[1]))
        return default

    def set_point(self, key: str, x: float, y: float):
        self.put(key, (x, y))

    def __repr__(self):
        return f"Model(name={self._name!r}, attrs={len(self._attributes)})"
