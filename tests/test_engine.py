"""
Unit tests for PyPAKMA numerical simulation engine and serial manager.
"""

import unittest
import numpy as np
from pakma.engine.simulation import SimulationEngine
from pakma.hardware.serial_manager import SerialManager


class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine(dt=0.01)

    def test_harmonic_oscillator_rk4(self):
        """Test simple harmonic oscillator: d2x/dt2 = -x (analytic solution: x(t) = cos(t))"""
        self.engine.reset({"x": 1.0, "v": 0.0})
        self.engine.equations = {
            "x": lambda t, s: s["v"],
            "v": lambda t, s: -s["x"]
        }

        # Step forward for 2 * pi seconds (~1 period)
        steps = int(2 * np.pi / 0.01)
        for _ in range(steps):
            self.engine.step_rk4()

        t_arr, x_arr = self.engine.get_numpy_arrays("x")
        # At t = 2*pi, x should be ~1.0
        self.assertAlmostEqual(x_arr[-1], 1.0, places=2)

    def test_euler_step(self):
        self.engine.reset({"x": 0.0})
        self.engine.equations = {"x": lambda t, s: 2.0}  # dx/dt = 2 -> x(t) = 2*t
        for _ in range(100):
            self.engine.step_euler()
        t_arr, x_arr = self.engine.get_numpy_arrays("x")
        self.assertAlmostEqual(x_arr[-1], 2.0, places=1)


class TestSerialManager(unittest.TestCase):
    def test_port_discovery(self):
        ports = SerialManager.get_available_ports()
        self.assertIsInstance(ports, list)


if __name__ == "__main__":
    unittest.main()
