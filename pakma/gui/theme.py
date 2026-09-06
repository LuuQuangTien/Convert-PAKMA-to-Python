"""
JPAKMA Authentic Desktop Theme Stylesheet for PyQt6.
Matches original JPAKMA look & feel with modern crisp rendering.
"""

JPAKMA_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #f0f0f4;
    color: #202020;
    font-family: 'Segoe UI', Arial, Tahoma, sans-serif;
    font-size: 12px;
}

QMenuBar {
    background-color: #f8f8fa;
    color: #202020;
    border-bottom: 1px solid #d0d0d8;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    border-radius: 3px;
}

QMenuBar::item:selected {
    background-color: #e0e4ec;
}

QMenu {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #c0c0c8;
    padding: 3px;
}

QMenu::item {
    padding: 5px 25px 5px 20px;
    border-radius: 2px;
}

QMenu::item:selected {
    background-color: #0078d7;
    color: #ffffff;
}

QToolBar {
    background-color: #f4f4f8;
    border-top: 1px solid #ffffff;
    border-bottom: 1px solid #d0d0d8;
    padding: 3px 4px;
    spacing: 3px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 3px;
    margin: 1px;
}

QToolButton:hover {
    background-color: #e6ebf5;
    border: 1px solid #b8cbe8;
}

QToolButton:pressed {
    background-color: #d2e0f4;
    border: 1px solid #7ea5d9;
}

QToolButton:checked {
    background-color: #d6e2f7;
    border: 1px solid #7ea5d9;
}

QTabWidget::pane {
    border: 1px solid #c0c0c8;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #e4e4ec;
    color: #404040;
    padding: 6px 14px;
    border: 1px solid #c0c0c8;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #000000;
    font-weight: bold;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #ececf4;
}

QStatusBar {
    background-color: #f0f0f4;
    border-top: 1px solid #d0d0d8;
    color: #404040;
    font-size: 11px;
}

QSplitter::handle {
    background-color: #dcdce4;
}

QSplitter::handle:hover {
    background-color: #0078d7;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #d0d0d8;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 10px;
    background-color: #fafafa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #fafafa;
    color: #333344;
}

QScrollBar:vertical {
    background: #f0f0f4;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c8c8d0;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #a0a0aa;
}
"""
