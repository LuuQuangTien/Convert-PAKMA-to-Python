"""
EventLog — Singleton logger for the application.

Ported from: de.uniwuerzburg.physik.pakma.util.EventLog
Original: Java singleton with priority-based logging (DEBUG..ERROR).
"""

from __future__ import annotations
import datetime
from typing import Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class EventEntry:
    """Single log entry."""
    priority: int
    source: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))


class EventLog:
    """
    Singleton event logger with priority filtering.

    Priority levels (matching Java):
        DEBUG = 0, INFO = 1, MSG = 2, WARN = 3, ERROR = 4
    """

    # Priority levels
    DEBUG = 0
    INFO = 1
    MSG = 2
    WARN = 3
    ERROR = 4

    _LEVEL_NAMES = {0: "DEBUG", 1: "INFO", 2: "MSG", 3: "WARN", 4: "ERROR"}

    _instance: Optional[EventLog] = None

    def __init__(self):
        self._threshold = self.MSG
        self._entries: List[EventEntry] = []
        self._listeners: list = []
        self._max_entries = 1000

    @classmethod
    def instance(cls) -> 'EventLog':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = EventLog()
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'EventLog':
        """Java-compatible alias."""
        return cls.instance()

    def set_priority_threshold(self, level: int):
        """Set minimum priority level for logging."""
        self._threshold = level

    def get_priority_threshold(self) -> int:
        return self._threshold

    def put(self, priority: int, source: Any, message: Any):
        """Log a message if priority >= threshold."""
        if priority < self._threshold:
            return

        source_str = source.__class__.__name__ if not isinstance(source, str) else source
        msg_str = str(message)

        entry = EventEntry(
            priority=priority,
            source=source_str,
            message=msg_str
        )

        self._entries.append(entry)

        # Trim if too many entries
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        # Print to console
        level_name = self._LEVEL_NAMES.get(priority, "???")
        print(f"[{entry.timestamp}] [{level_name}] {source_str}: {msg_str}")

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(entry)
            except Exception:
                pass

    def add_listener(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def get_entries(self) -> List[EventEntry]:
        return list(self._entries)

    def clear(self):
        self._entries.clear()


# Module-level shortcut (matching Java's EventLog.out static field)
EventLog.out = EventLog.instance()
