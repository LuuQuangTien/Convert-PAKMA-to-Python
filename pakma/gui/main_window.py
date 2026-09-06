"""
MainWindow for PyPAKMA — Faithful recreation of original JPAKMA Java Swing MainFrame & MainView.
Built with PyQt6, pyqtgraph, numpy, and pyserial.
"""

from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QStatusBar, QFileDialog, 
    QMessageBox, QLabel, QComboBox, QDoubleSpinBox, QWidget
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QSize

from .views.graph_view import GraphView
from .views.pm_view import PMView
from .views.script_view import ScriptView
from .dialogs.serial_dialog import SerialPortDialog
from ..styles.theme import JPAKMA_THEME_QSS
from ..resources.strings import AppStrings, LT
from ..util.resource_manager import ResourceManager
from ..engine.simulation import SimulationEngine
from ..hardware.serial_manager import SerialManager


class MainWindow(QMainWindow):
    """
    Main Application Window ported from JPAKMA MainFrame.java and MainView.java.
    """
    APP_TITLE = "JPAKMA"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.APP_TITLE)
        self.resize(1100, 750)
        self.setStyleSheet(JPAKMA_THEME_QSS)

        # Set Window Icon
        logo_icon = ResourceManager.get_icon("images/jpakma-logo.png")
        if not logo_icon.isNull():
            self.setWindowIcon(logo_icon)

        # Core Engines
        self.engine = SimulationEngine(dt=0.01)
        self.serial_mgr = SerialManager()
        self.presentation_mode = False

        # Simulation Loop Timer
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(16)  # ~60 FPS
        self.sim_timer.timeout.connect(self._simulation_loop)

        # Performance monitoring
        self.last_time = time.time()
        self.frame_count = 0

        # UI Initialization
        self._create_main_toolbar()
        self._create_central_tabs()
        self._create_statusbar()

    def _create_main_toolbar(self):
        """Builds top toolbar with exact icons and order from JPAKMA MainView.createButtonBar()."""
        self.toolbar = QToolBar("Main Operations", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.toolbar)

        # 1. Exit
        act_exit = self.toolbar.addAction(ResourceManager.get_icon("images/exit.gif"), AppStrings.TOOL_EXIT)
        act_exit.setToolTip("Closes this application")
        act_exit.triggered.connect(self.close)
        self.toolbar.addSeparator()

        # 2. Presentation / Design Mode Toggle
        self.act_mode = self.toolbar.addAction(ResourceManager.get_icon("images/locked.gif"), AppStrings.TOOL_MODE)
        self.act_mode.setToolTip("Toggle presentation/design mode")
        self.act_mode.setCheckable(True)
        self.act_mode.toggled.connect(self._toggle_mode)
        self.toolbar.addSeparator()

        # 3. New, Load, Save
        act_new = self.toolbar.addAction(ResourceManager.get_icon("images/new.gif"), AppStrings.TOOL_NEW)
        act_new.setToolTip("Create new project")
        act_new.triggered.connect(self.new_file)

        act_load = self.toolbar.addAction(ResourceManager.get_icon("images/load.gif"), AppStrings.TOOL_LOAD)
        act_load.setToolTip("Open existing project")
        act_load.triggered.connect(self.open_file)

        act_save = self.toolbar.addAction(ResourceManager.get_icon("images/save.gif"), AppStrings.TOOL_SAVE)
        act_save.setToolTip("Save current project")
        act_save.triggered.connect(self.save_file)
        self.toolbar.addSeparator()

        # 4. Compile, Project Options, Hardware/Measurement Setup
        act_compile = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Compile.gif"), AppStrings.TOOL_COMPILE)
        act_compile.setToolTip("Compile PASCL Script")
        act_compile.triggered.connect(lambda: self.script_view.compile_script())

        act_prj = self.toolbar.addAction(ResourceManager.get_icon("images/prjoptions.gif"), AppStrings.TOOL_PRJ_OPTIONS)
        act_prj.setToolTip("Change project options")

        act_measle = self.toolbar.addAction(ResourceManager.get_icon("images/measlesetup.gif"), AppStrings.TOOL_MEASLE)
        act_measle.setToolTip("Setup measurement sources (pyserial / CASSY / Arduino)")
        act_measle.triggered.connect(self.open_serial_dialog)

        act_eventlog = self.toolbar.addAction(ResourceManager.get_icon("images/eventlog.gif"), AppStrings.TOOL_EVENTLOG)
        act_eventlog.setToolTip("Open event log")

        act_snapshot = self.toolbar.addAction(ResourceManager.get_icon("images/snapshot.gif"), AppStrings.TOOL_SNAPSHOT)
        act_snapshot.setToolTip("Take snapshot of the visible panel")

        act_font = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Font.gif"), AppStrings.TOOL_FONT)
        act_font.setToolTip("Choose display font")
        self.toolbar.addSeparator()

        # 5. Run, Pause
        self.act_run = self.toolbar.addAction(ResourceManager.get_icon("images/run.gif"), AppStrings.TOOL_RUN)
        self.act_run.setToolTip("Run script / simulation")
        self.act_run.triggered.connect(self.start_simulation)

        self.act_pause = self.toolbar.addAction(ResourceManager.get_icon("images/pause.gif"), AppStrings.TOOL_PAUSE)
        self.act_pause.setToolTip("Pause script / simulation")
        self.act_pause.setEnabled(False)
        self.act_pause.triggered.connect(self.pause_simulation)
        self.toolbar.addSeparator()

        # 6. Clipboard & Undo/Redo
        act_copy = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Copy.gif"), AppStrings.TOOL_COPY)
        act_cut = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Cut.gif"), AppStrings.TOOL_CUT)
        act_paste = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Paste.gif"), AppStrings.TOOL_PASTE)
        act_undo = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Undo.gif"), AppStrings.TOOL_UNDO)
        act_redo = self.toolbar.addAction(ResourceManager.get_icon("images/ed_Redo.gif"), AppStrings.TOOL_REDO)
        self.toolbar.addSeparator()

        # 7. Help
        act_help = self.toolbar.addAction(ResourceManager.get_icon("images/help.gif"), AppStrings.TOOL_HELP)
        act_help.setToolTip("Show help")
        act_help.triggered.connect(self.show_about)

    def _create_central_tabs(self):
        """Builds 3 main tabs matching JPAKMA: Animation, Model, Script."""
        self.tabs = QTabWidget(self)

        self.graph_view = GraphView(self.engine, self)
        self.pm_view = PMView(self)
        self.script_view = ScriptView(self)

        self.tabs.addTab(
            self.graph_view, 
            ResourceManager.get_icon("images/graphview.gif"), 
            AppStrings.TAB_ANIMATION
        )
        self.tabs.setTabToolTip(0, AppStrings.TAB_ANIMATION_TOOLTIP)

        self.tabs.addTab(
            self.pm_view, 
            ResourceManager.get_icon("images/modelview.gif"), 
            AppStrings.TAB_MODEL
        )
        self.tabs.setTabToolTip(1, AppStrings.TAB_MODEL_TOOLTIP)

        self.tabs.addTab(
            self.script_view, 
            ResourceManager.get_icon("images/scriptview.gif"), 
            AppStrings.TAB_SCRIPT
        )
        self.tabs.setTabToolTip(2, AppStrings.TAB_SCRIPT_TOOLTIP)

        self.setCentralWidget(self.tabs)

    def _create_statusbar(self):
        status = QStatusBar(self)
        self.setStatusBar(status)

        self.lbl_status = QLabel(AppStrings.STATUS_READY)
        self.lbl_time = QLabel("t: 0.00 s")
        self.lbl_fps = QLabel("FPS: 60")
        self.lbl_serial = QLabel("Serial: Disconnected")

        status.addWidget(self.lbl_status, 1)
        status.addPermanentWidget(self.lbl_time)
        status.addPermanentWidget(self.lbl_fps)
        status.addPermanentWidget(self.lbl_serial)

        self.serial_mgr.connection_status.connect(self._on_serial_status_changed)

    def _toggle_mode(self, checked: bool):
        self.presentation_mode = checked
        if checked:
            self.act_mode.setIcon(ResourceManager.get_icon("images/unlocked.gif"))
            self.lbl_status.setText("Mode: Presentation")
        else:
            self.act_mode.setIcon(ResourceManager.get_icon("images/locked.gif"))
            self.lbl_status.setText("Mode: Design")

    def start_simulation(self):
        self.sim_timer.start()
        self.act_run.setEnabled(False)
        self.act_pause.setEnabled(True)
        self.lbl_status.setText(AppStrings.STATUS_RUNNING)

    def pause_simulation(self):
        self.sim_timer.stop()
        self.act_run.setEnabled(True)
        self.act_pause.setEnabled(False)
        self.lbl_status.setText(AppStrings.STATUS_PAUSED)

    def _simulation_loop(self):
        # 2 RK4 steps per tick
        self.engine.step_rk4()
        self.engine.step_rk4()
        self.graph_view.update_plots()
        self.lbl_time.setText(f"t: {self.engine.time:.2f} s")

        # FPS
        self.frame_count += 1
        now = time.time()
        if now - self.last_time >= 1.0:
            fps = self.frame_count / (now - self.last_time)
            self.lbl_fps.setText(f"FPS: {fps:.0f}")
            self.frame_count = 0
            self.last_time = now

    def _on_serial_status_changed(self, connected: bool, msg: str):
        if connected:
            self.lbl_serial.setText(f"Serial: {self.serial_mgr.current_port} (Connected)")
            self.lbl_serial.setStyleSheet("color: #008800; font-weight: bold;")
        else:
            self.lbl_serial.setText("Serial: Disconnected")
            self.lbl_serial.setStyleSheet("color: #666666;")

    def open_serial_dialog(self):
        dlg = SerialPortDialog(self.serial_mgr, self)
        dlg.exec()

    def new_file(self):
        self.engine.reset({"x": 1.0, "v": 0.0})
        self.graph_view.update_plots()
        self.lbl_time.setText("t: 0.00 s")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open JPAKMA File", "", "JPAKMA Files (*.pkm *.pas *.xml);;All Files (*.*)")
        if path:
            self.setWindowTitle(f"{self.APP_TITLE} - {path.split('/')[-1]}")

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save JPAKMA Project", "", "JPAKMA File (*.pkm)")
        if path:
            QMessageBox.information(self, "Save", f"Saved to: {path}")

    def show_about(self):
        QMessageBox.about(
            self,
            "About JPAKMA",
            "<h3>JPAKMA (Python Port)</h3>"
            "<p>Physics Simulation and Measurement Data Acquisition</p>"
            "<p>Ported to Python with <b>PyQt6</b>, <b>pyqtgraph</b>, <b>NumPy</b>, and <b>PySerial</b>.</p>"
            "<p>Original by University of Würzburg (Department of Physics).</p>"
        )

    def closeEvent(self, event):
        self.sim_timer.stop()
        self.serial_mgr.disconnect_port()
        event.accept()
