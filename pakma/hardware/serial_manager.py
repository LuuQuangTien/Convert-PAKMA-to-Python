"""
PySerial Hardware Communication Manager for PyPAKMA.
Provides asynchronous serial acquisition with QThread and PyQt6 Signals,
supporting telemetry streaming from Arduino, CASSY, Micro:bit, or lab sensors.
"""

from __future__ import annotations
import time
import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class SerialReaderWorker(QObject):
    """Worker object running inside a separate QThread for non-blocking serial I/O."""
    data_received = pyqtSignal(str)
    packet_received = pyqtSignal(list)
    connection_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port: str = "", baudrate: int = 115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: serial.Serial | None = None
        self._running = False

    def start_reading(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self._running = True
            self.connection_changed.emit(True, f"Connected to {self.port} @ {self.baudrate} baud")
            
            while self._running:
                if self.serial_conn and self.serial_conn.is_open:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.data_received.emit(line)
                        # Attempt to parse numeric telemetry packet: e.g. "1.23, 4.56, 7.89"
                        parts = line.replace(';', ',').replace('\t', ',').split(',')
                        numeric_values = []
                        for p in parts:
                            try:
                                numeric_values.append(float(p.strip()))
                            except ValueError:
                                pass
                        if numeric_values:
                            self.packet_received.emit(numeric_values)
                time.sleep(0.005)
        except Exception as ex:
            self.error_occurred.emit(str(ex))
            self.connection_changed.emit(False, str(ex))
        finally:
            self.close()

    def write_data(self, data: str):
        """Send command string to serial device."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(data.encode('utf-8'))
            except Exception as ex:
                self.error_occurred.emit(f"Write error: {ex}")

    def stop(self):
        self._running = False

    def close(self):
        self._running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.connection_changed.emit(False, "Disconnected")


class SerialManager(QObject):
    """Top-level serial communication controller."""
    data_received = pyqtSignal(str)
    packet_received = pyqtSignal(list)
    connection_status = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.thread: QThread | None = None
        self.worker: SerialReaderWorker | None = None
        self.is_connected = False
        self.current_port = ""
        self.current_baudrate = 115200

    @staticmethod
    def get_available_ports() -> list[tuple[str, str]]:
        """Return list of (port_device, description) for all available COM/serial ports."""
        ports = serial.tools.list_ports.comports()
        return [(p.device, f"{p.device} - {p.description}") for p in ports]

    def connect_port(self, port: str, baudrate: int = 115200):
        self.disconnect_port()
        self.current_port = port
        self.current_baudrate = baudrate

        self.thread = QThread()
        self.worker = SerialReaderWorker(port, baudrate)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.start_reading)
        self.worker.data_received.connect(self.data_received.emit)
        self.worker.packet_received.connect(self.packet_received.emit)
        self.worker.connection_changed.connect(self._on_connection_changed)
        self.worker.error_occurred.connect(self.error_occurred.emit)

        self.thread.start()

    def _on_connection_changed(self, connected: bool, msg: str):
        self.is_connected = connected
        self.connection_status.emit(connected, msg)

    def send(self, message: str):
        if self.worker and self.is_connected:
            self.worker.write_data(message)

    def disconnect_port(self):
        if self.worker:
            self.worker.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait(500)
            self.thread = None
        self.worker = None
        self.is_connected = False
        self.connection_status.emit(False, "Disconnected")
