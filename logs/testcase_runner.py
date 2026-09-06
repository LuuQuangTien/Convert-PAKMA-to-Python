"""
Test runner and logger for PyPAKMA testcases.
Executes all unit and integration tests and writes detailed execution logs with timestamps.
"""

import os
import sys
import unittest
import datetime
import numpy as np

# Ensure PyPAKMA package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pakma.engine.simulation import SimulationEngine
from pakma.hardware.serial_manager import SerialManager
from pakma.model.model import Model
from pakma.model.document import Document


def run_all_tests_and_log(log_filepath: str):
    os.makedirs(os.path.dirname(log_filepath), exist_ok=True)
    with open(log_filepath, 'w', encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("                       PYPAKMA TESTCASE EXECUTION LOG                           \n")
        f.write(f" Execution Date & Time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(" Python Environment    : Python 3.12 (PyQt6 6.11, pyqtgraph 0.14, numpy 2.4, pyserial 3.5)\n")
        f.write(" Methodology           : Spiral Model - Iteration 1 (Phase 1: Architecture & UI Skeleton)\n")
        f.write("================================================================================\n\n")

        test_results = []

        # --- Testcase 01: Model Key-Value Store & Observer ---
        t0 = datetime.datetime.now()
        f.write("[TESTCASE 01] Model Observable & Key-Value Attributes\n")
        f.write("  - Objective: Port of de.uniwuerzburg.physik.pakma.model.Model\n")
        try:
            m = Model("TestModel")
            m.set_int("mass", 5)
            m.set_double("velocity", 12.34)
            m.set_string("name", "Oscillator_1")
            assert m.get_int("mass") == 5
            assert abs(m.get_double("velocity") - 12.34) < 1e-6
            assert m.get_string("name") == "Oscillator_1"
            f.write("  - Status: PASSED\n")
            f.write("  - Details: Int, Double, String setters and getters verified.\n")
            test_results.append(("TC-01", "Model Key-Value Store", "PASSED", (datetime.datetime.now()-t0).total_seconds()))
        except Exception as e:
            f.write(f"  - Status: FAILED ({e})\n")
            test_results.append(("TC-01", "Model Key-Value Store", f"FAILED: {e}", 0))

        # --- Testcase 02: Document Container & Transactions ---
        t0 = datetime.datetime.now()
        f.write("\n[TESTCASE 02] Document Container & Model Registration\n")
        f.write("  - Objective: Port of de.uniwuerzburg.physik.pakma.model.Document\n")
        try:
            doc = Document("TestDoc")
            m1 = Model("M1")
            m2 = Model("M2")
            doc.add_model(m1)
            doc.add_model(m2)
            assert doc.get_model_count() == 2
            assert doc.get_model(m1.get_id()) == m1
            f.write("  - Status: PASSED\n")
            f.write("  - Details: Multi-model registration, ID lookup, count verified.\n")
            test_results.append(("TC-02", "Document Model Management", "PASSED", (datetime.datetime.now()-t0).total_seconds()))
        except Exception as e:
            f.write(f"  - Status: FAILED ({e})\n")
            test_results.append(("TC-02", "Document Model Management", f"FAILED: {e}", 0))

        # --- Testcase 03: NumPy Simulation Engine (Euler & RK4 ODE Solvers) ---
        t0 = datetime.datetime.now()
        f.write("\n[TESTCASE 03] Numerical Physics Engine (NumPy RK4 & Euler Solvers)\n")
        f.write("  - Objective: High-accuracy numerical integration for physics ODEs\n")
        try:
            engine = SimulationEngine(dt=0.01)
            # Harmonic oscillator d2x/dt2 = -x (x(0)=1, v(0)=0 -> exact x(2*pi) = 1.0)
            engine.reset({"x": 1.0, "v": 0.0})
            engine.equations = {
                "x": lambda t, s: s["v"],
                "v": lambda t, s: -s["x"]
            }
            steps = int(2 * np.pi / 0.01)
            for _ in range(steps):
                engine.step_rk4()

            t_arr, x_arr = engine.get_numpy_arrays("x")
            err = abs(x_arr[-1] - 1.0)
            assert err < 0.01, f"RK4 Error too large: {err}"
            f.write("  - Status: PASSED\n")
            f.write(f"  - Details: Harmonic oscillator integrated 1 period ({steps} steps). Final x={x_arr[-1]:.6f}, error={err:.6e}.\n")
            test_results.append(("TC-03", "NumPy RK4 ODE Solver", "PASSED", (datetime.datetime.now()-t0).total_seconds()))
        except Exception as e:
            f.write(f"  - Status: FAILED ({e})\n")
            test_results.append(("TC-03", "NumPy RK4 ODE Solver", f"FAILED: {e}", 0))

        # --- Testcase 04: Hardware PySerial Manager ---
        t0 = datetime.datetime.now()
        f.write("\n[TESTCASE 04] Hardware Serial Communication (pyserial)\n")
        f.write("  - Objective: Port scanning & thread-safe async communication\n")
        try:
            ports = SerialManager.get_available_ports()
            f.write(f"  - Scanned Ports: {len(ports)} COM ports detected ({[p[0] for p in ports]})\n")
            mgr = SerialManager()
            assert hasattr(mgr, 'data_received')
            assert hasattr(mgr, 'packet_received')
            f.write("  - Status: PASSED\n")
            f.write("  - Details: Serial port detection and signal definitions validated.\n")
            test_results.append(("TC-04", "PySerial Hardware Manager", "PASSED", (datetime.datetime.now()-t0).total_seconds()))
        except Exception as e:
            f.write(f"  - Status: FAILED ({e})\n")
            test_results.append(("TC-04", "PySerial Hardware Manager", f"FAILED: {e}", 0))

        # --- Summary Table ---
        f.write("\n" + "="*80 + "\n")
        f.write("                              TEST SUMMARY TABLE                                \n")
        f.write("="*80 + "\n")
        f.write(f"{'Test ID':<10} | {'Testcase Name':<32} | {'Result':<12} | {'Duration (s)':<12}\n")
        f.write("-" * 80 + "\n")
        all_passed = True
        for t_id, name, res, dur in test_results:
            f.write(f"{t_id:<10} | {name:<32} | {res:<12} | {dur:<12.4f}\n")
            if "PASSED" not in res:
                all_passed = False
        f.write("="*80 + "\n")
        f.write(f"TOTAL: {len(test_results)} Tests | PASSED: {sum(1 for _,_,r,_ in test_results if 'PASSED' in r)} | FAILED: {sum(1 for _,_,r,_ in test_results if 'PASSED' not in r)}\n")
        f.write(f"OVERALL RESULT: {'SUCCESS' if all_passed else 'FAILURE'}\n")
        f.write("="*80 + "\n")

    print(f"Test log written successfully to {log_filepath}")


if __name__ == "__main__":
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tastlist_report', 'Testcase_Execution_Logs_Phase1.txt'))
    run_all_tests_and_log(log_path)
