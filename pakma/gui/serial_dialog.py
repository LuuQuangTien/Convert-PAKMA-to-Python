"""
Serial Port Connection & Terminal Dialog for PyPAKMA.
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTextEdit, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from ..hardware.serial_manager import SerialManager


class SerialPortDialog(QDialog):
    """Configuration dialog for selecting serial port, baudrate, and viewing terminal traffic."""
    def __init__(self, serial_mgr: SerialManager, parent=None):
        super().__init__(parent)
        self.serial_mgr = serial_mgr
        self.setWindowTitle("Serial Hardware Interface (pyserial)")
        self.resize(600, 450)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Connection Settings Group
        grp_conn = QGroupBox("Port Configuration")
        conn_layout = QHBoxLayout(grp_conn)

        self.cb_ports = QComboBox()
        self.btn_refresh = QPushButton("Refresh Ports")
        self.btn_refresh.clicked.connect(self.refresh_ports)

        self.cb_baud = QComboBox()
        self.cb_baud.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "921600"])
        self.cb_baud.setCurrentText("115200")

        self.btn_toggle_connect = QPushButton("Connect")
        self.btn_toggle_connect.clicked.connect(self.toggle_connection)

        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.cb_ports, stretch=2)
        conn_layout.addWidget(self.btn_refresh)
        conn_layout.addWidget(QLabel("Baud:"))
        conn_layout.addWidget(self.cb_baud)
        conn_layout.addWidget(self.btn_toggle_connect)
        layout.addWidget(grp_conn)

        # Terminal Log Group
        grp_term = QGroupBox("Live Serial Terminal")
        term_layout = QVBoxLayout(grp_term)
        self.txt_terminal = QTextEdit()
        self.txt_terminal.setReadOnly(True)
        self.txt_terminal.setStyleSheet("background-color: #0e0e12; color: #00ff88; font-family: 'Consolas', monospace;")
        term_layout.addWidget(self.txt_terminal)

        # Send command bar
        send_bar = QHBoxLayout()
        self.txt_send = QLineEdit()
        self.txt_send.setPlaceholderText("Enter command to send...")
        self.txt_send.returnPressed.connect(self.send_data)
        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.send_data)
        send_bar.addWidget(self.txt_send)
        send_bar.addWidget(self.btn_send)
        term_layout.addLayout(send_bar)
        layout.addWidget(grp_term)

        # Connect signals
        self.serial_mgr.data_received.connect(self._on_data)
        self.serial_mgr.connection_status.connect(self._on_conn_status)

        self.refresh_ports()
        self._update_ui_state()

    def refresh_ports(self):
        self.cb_ports.clear()
        ports = self.serial_mgr.get_available_ports()
        if not ports:
            self.cb_ports.addItem("No COM ports found", "")
        else:
            for dev, desc in ports:
                self.cb_ports.addItem(desc, dev)

    def toggle_connection(self):
        if self.serial_mgr.is_connected:
            self.serial_mgr.disconnect_port()
        else:
            port = self.cb_ports.currentData()
            if port:
                baud = int(self.cb_baud.currentText())
                self.serial_mgr.connect_port(port, baud)

    def send_data(self):
        text = self.txt_send.text()
        if text:
            self.serial_mgr.send(text + "\n")
            self.txt_terminal.append(f"<span style='color: #00d2ff;'>&gt; {text}</span>")
            self.txt_send.clear()

    def _on_data(self, data: str):
        self.txt_terminal.append(data)

    def _on_conn_status(self, connected: bool, msg: str):
        self._update_ui_state()
        color = "#00ff88" if connected else "#ff5252"
        self.txt_terminal.append(f"<span style='color: {color};'>=== {msg} ===</span>")

    def _update_ui_state(self):
        if self.serial_mgr.is_connected:
            self.btn_toggle_connect.setText("Disconnect")
            self.btn_toggle_connect.setStyleSheet("background-color: #d32f2f;")
            self.cb_ports.setEnabled(False)
            self.cb_baud.setEnabled(False)
        else:
            self.btn_toggle_connect.setText("Connect")
            self.btn_toggle_connect.setStyleSheet("background-color: #007acc;")
            self.cb_ports.setEnabled(True)
            self.cb_baud.setEnabled(True)
