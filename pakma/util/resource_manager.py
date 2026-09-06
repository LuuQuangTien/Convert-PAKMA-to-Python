"""
Resource Manager for loading original JPAKMA icons and assets.
"""

from __future__ import annotations
import os
from PyQt6.QtGui import QIcon, QPixmap


class ResourceManager:
    _base_path = None

    @classmethod
    def get_image_path(cls, relative_path: str) -> str:
        if cls._base_path is None:
            # Find images directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            pypakma_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
            candidate = os.path.join(pypakma_dir, relative_path)
            if os.path.exists(candidate):
                cls._base_path = pypakma_dir
            else:
                # Try parent project root
                parent_dir = os.path.abspath(os.path.join(pypakma_dir, '..'))
                cls._base_path = parent_dir
        
        path = os.path.join(cls._base_path, relative_path)
        if not os.path.exists(path):
            # Try without leading 'images/' or normalized
            norm = relative_path.replace('\\', '/')
            path = os.path.join(cls._base_path, norm)
        return path

    @classmethod
    def get_icon(cls, image_name: str) -> QIcon:
        """Load QIcon from images directory (e.g. 'images/run.gif' or 'run.gif')."""
        if not image_name.startswith("images/"):
            image_name = f"images/{image_name}"
        path = cls.get_image_path(image_name)
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()

    @classmethod
    def get_pixmap(cls, image_name: str) -> QPixmap:
        if not image_name.startswith("images/"):
            image_name = f"images/{image_name}"
        path = cls.get_image_path(image_name)
        if os.path.exists(path):
            return QPixmap(path)
        return QPixmap()
