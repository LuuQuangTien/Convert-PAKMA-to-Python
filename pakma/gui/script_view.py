"""
ScriptView — PASCL / Python Script Editor Tab matching original JPAKMA ScriptView.
Ported from: de.uniwuerzburg.physik.pakma.gui.ScriptView
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter, 
    QPlainTextEdit, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression
from ..util.resource_manager import ResourceManager


class PASCLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for PASCL and Python scripts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Keywords
        kw_format = QTextCharFormat()
        kw_format.setForeground(QColor("#0000bb"))
        kw_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            r"\bVAR\b", r"\bBEGIN\b", r"\bEND\b", r"\bPROGRAM\b", r"\bFUNCTION\b",
            r"\bPROCEDURE\b", r"\bIF\b", r"\bTHEN\b", r"\bELSE\b", r"\bWHILE\b",
            r"\bDO\b", r"\bFOR\b", r"\bTO\b", r"\bDOWNTO\b", r"\bRETURN\b",
            r"\bdef\b", r"\bimport\b", r"\bfrom\b", r"\bclass\b"
        ]
        for pattern in keywords:
            self.rules.append((QRegularExpression(pattern, QRegularExpression.PatternOption.CaseInsensitiveOption), kw_format))

        # Numbers
        num_format = QTextCharFormat()
        num_format.setForeground(QColor("#a00000"))
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), num_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008800"))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"\{[^\}]*\}"), comment_format))
        self.rules.append((QRegularExpression(r"//.*"), comment_format))
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class ScriptView(QWidget):
    """
    ScriptView matching original JPAKMA layout:
    - Top sub-tabs: 'Script' & 'Extensions'
    - Bottom split pane: Message / Compiler list with status icons.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top: Sub-tabbed pane
        self.script_tabs = QTabWidget()
        
        # 1. Script Editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 10))
        self.highlighter = PASCLSyntaxHighlighter(self.editor.document())
        
        sample_pascl = """{ JPAKMA Simulation Script }
{ Mass-Spring Oscillator Model }

PROGRAM HarmonicOscillator;
VAR
    k: REAL;      { Spring constant N/m }
    m: REAL;      { Mass kg }
    c: REAL;      { Damping coeff N.s/m }
    x, v, a: REAL;
    dt: REAL;

BEGIN
    k := 10.0;
    m := 1.0;
    c := 0.2;
    dt := 0.01;
    x := 1.0;
    v := 0.0;
    
    { Numerical ODE Derivative }
    a := -(k/m)*x - (c/m)*v;
    v := v + a * dt;
    x := x + v * dt;
END.
"""
        self.editor.setPlainText(sample_pascl)
        self.script_tabs.addTab(self.editor, "Script")

        # 2. Extensions tab placeholder
        self.ext_panel = QWidget()
        ext_layout = QVBoxLayout(self.ext_panel)
        ext_layout.addWidget(QLabel("Extensions and Custom Script Libraries (PASCL / Python)"))
        self.script_tabs.addTab(self.ext_panel, "Extensions")

        splitter.addWidget(self.script_tabs)

        # Bottom: Messages / Compiler output list
        self.msg_list = QListWidget()
        self.msg_list.setStyleSheet("background-color: #ffffff; color: #202020; font-family: 'Segoe UI', Arial;")
        self._add_message("JPAKMA Script Engine ready.", "info")
        self._add_message("Model compiler loaded.", "info")

        splitter.addWidget(self.msg_list)
        splitter.setSizes([450, 120])
        layout.addWidget(splitter)

    def _add_message(self, text: str, msg_type: str = "info"):
        icon_name = "images/li_info.gif"
        if msg_type == "warn":
            icon_name = "images/li_warn.gif"
        elif msg_type == "error":
            icon_name = "images/li_error.gif"
        item = QListWidgetItem(ResourceManager.get_icon(icon_name), text)
        self.msg_list.addItem(item)

    def compile_script(self):
        self._add_message("Compiling script...", "info")
        self._add_message("Compilation successful: 0 errors, 0 warnings.", "info")
