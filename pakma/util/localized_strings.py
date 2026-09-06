"""
LocalizedStrings — Internationalization support.

Ported from: de.uniwuerzburg.physik.pakma.util.LocalizedStrings
Original: Reads key=value pairs from .res files for UI text localization.
"""

from __future__ import annotations
import os
from typing import Optional, Dict


class LocalizedStrings:
    """
    Simple i18n string resolver. Loads key=value pairs from a resource file
    (e.g., lang/default.res) and provides lookup via get().

    If no translation is found, the key itself is returned.
    """

    _strings: Dict[str, str] = {}
    _loaded = False

    @classmethod
    def load(cls, resource_path: Optional[str] = None, country: Optional[str] = None):
        """
        Load localized strings from a resource file.

        Args:
            resource_path: Path to the .res file. If None, uses default path.
            country: Country code for locale-specific file (unused for now).
        """
        if resource_path is None:
            # Try to find lang/default.res relative to the package
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
            resource_path = os.path.join(base_dir, "lang", "default.res")

        if not os.path.exists(resource_path):
            return

        try:
            with open(resource_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("//"):
                        continue
                    eq_pos = line.find("=")
                    if eq_pos > 0:
                        key = line[:eq_pos].strip()
                        value = line[eq_pos + 1:].strip()
                        cls._strings[key] = value
            cls._loaded = True
        except Exception as e:
            print(f"Warning: Could not load localized strings from {resource_path}: {e}")

    @classmethod
    def get(cls, key: str) -> str:
        """
        Get localized string for key.
        Returns the key itself if no translation found.
        """
        if not cls._loaded:
            cls.load()
        return cls._strings.get(key, key)

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def get_all(cls) -> Dict[str, str]:
        return dict(cls._strings)
