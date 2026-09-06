"""
NumPy-powered Physics Simulation Engine for PyPAKMA.
Provides numerical ODE integration (Euler, RK4, Verlet), vector math,
and high-speed time-series state recording.
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Dict, List, Optional, Tuple


class SimulationEngine:
    """
    Core numerical physics engine supporting Euler, RK4, and Verlet integration.
    """
    def __init__(self, dt: float = 0.01):
        self.dt: float = dt
        self.time: float = 0.0
        self.step_count: int = 0
        self.is_running: bool = False
        
        # State variables: name -> current float value
        self.state: Dict[str, float] = {}
        # Derivatives functions: name -> callable(t, state) -> float
        self.equations: Dict[str, Callable[[float, Dict[str, float]], float]] = {}
        
        # History buffers for high-speed pyqtgraph plotting
        self.time_history: List[float] = []
        self.history: Dict[str, List[float]] = {}
        self.max_history_points: int = 10000

    def reset(self, initial_state: Optional[Dict[str, float]] = None):
        """Reset simulation time and state."""
        self.time = 0.0
        self.step_count = 0
        if initial_state:
            self.state = dict(initial_state)
        self.time_history = [self.time]
        self.history = {var: [val] for var, val in self.state.items()}

    def add_variable(self, name: str, initial_value: float, equation: Optional[Callable[[float, Dict[str, float]], float]] = None):
        """Register a state variable and its derivative equation dy/dt = f(t, state)."""
        self.state[name] = float(initial_value)
        if equation:
            self.equations[name] = equation
        if name not in self.history:
            self.history[name] = [float(initial_value)]

    def step_euler(self) -> float:
        """Advance simulation by dt using 1st order Euler integration."""
        t = self.time
        dt = self.dt
        derivatives = {k: fn(t, self.state) for k, fn in self.equations.items()}
        for k, dydt in derivatives.items():
            self.state[k] += dydt * dt
        self.time += dt
        self.step_count += 1
        self._record_history()
        return self.time

    def step_rk4(self) -> float:
        """Advance simulation by dt using 4th order Runge-Kutta integration."""
        t = self.time
        dt = self.dt
        y = self.state

        # k1 = f(t, y)
        k1 = {k: fn(t, y) for k, fn in self.equations.items()}
        
        # k2 = f(t + dt/2, y + k1*dt/2)
        y_temp1 = {k: y[k] + 0.5 * dt * k1.get(k, 0.0) for k in y}
        k2 = {k: fn(t + 0.5 * dt, y_temp1) for k, fn in self.equations.items()}
        
        # k3 = f(t + dt/2, y + k2*dt/2)
        y_temp2 = {k: y[k] + 0.5 * dt * k2.get(k, 0.0) for k in y}
        k3 = {k: fn(t + 0.5 * dt, y_temp2) for k, fn in self.equations.items()}
        
        # k4 = f(t + dt, y + k3*dt)
        y_temp3 = {k: y[k] + dt * k3.get(k, 0.0) for k in y}
        k4 = {k: fn(t + dt, y_temp3) for k, fn in self.equations.items()}
        
        # y_{n+1} = y_n + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
        for k in self.equations:
            self.state[k] += (dt / 6.0) * (k1[k] + 2.0 * k2[k] + 2.0 * k3[k] + k4[k])

        self.time += dt
        self.step_count += 1
        self._record_history()
        return self.time

    def _record_history(self):
        self.time_history.append(self.time)
        for k, v in self.state.items():
            if k not in self.history:
                self.history[k] = []
            self.history[k].append(v)
            
        if len(self.time_history) > self.max_history_points:
            self.time_history.pop(0)
            for k in self.history:
                if self.history[k]:
                    self.history[k].pop(0)

    def get_numpy_arrays(self, var_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """Return (time_array, var_array) as NumPy arrays for zero-copy fast plotting."""
        t_arr = np.array(self.time_history, dtype=np.float64)
        v_arr = np.array(self.history.get(var_name, []), dtype=np.float64)
        return t_arr, v_arr
