from __future__ import annotations

import time
from collections import deque
from typing import Deque, Sequence, Tuple, Optional, List, Union

import numpy as np
import matplotlib.pyplot as plt

try:
    from brian2 import second, ms, mV  # type: ignore
    _HAVE_BRIAN2 = True
except Exception:  # pragma: no cover
    _HAVE_BRIAN2 = False
    class _Unit(float):
        pass
    second = _Unit(1.0)
    ms = _Unit(1e-3)
    mV = _Unit(1.0)


def _is_brian_quantity(x) -> bool:
    return _HAVE_BRIAN2 and hasattr(x, "dimensionality")


def _to_seconds(x, factor: float = 1.0) -> np.ndarray:
    if _is_brian_quantity(x):
        return np.asarray(x / second, dtype=float)
    return np.asarray(x, dtype=float) * float(factor)


def _to_mV(x, factor: float = 1.0) -> np.ndarray:
    if _is_brian_quantity(x):
        return np.asarray(x / mV, dtype=float)
    return np.asarray(x, dtype=float) * float(factor)


def _scalar_seconds(x, factor: float = 1.0) -> float:
    if _is_brian_quantity(x):
        return float(x / second)
    return float(x) * float(factor)


def _scalar_mV(x, factor: float = 1.0) -> float:
    if _is_brian_quantity(x):
        return float(x / mV)
    return float(x) * float(factor)


class DynamicPlotION:
    def __init__(self, fig=None, ax=None, update_interval: int = 100, time_unit: float = 1.0):
        self.fig = fig
        self.ax = ax
        self.update_interval = int(update_interval)
        self.time_unit = float(time_unit)
        self._setup_done = False

    def setup(self):
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self._setup_impl()
        self._setup_done = True
        return self

    def update_once(self):
        if not self._setup_done:
            self.setup()
        return self._update_impl()

    def _setup_impl(self):
        raise NotImplementedError

    def _update_impl(self):
        raise NotImplementedError


class DynamicRasterPlotION(DynamicPlotION):
    def __init__(self,
                 data_buffer: Deque[Tuple[Sequence[int], Sequence[float]]],
                 positions=None,
                 num_neurons: int = 10,
                 max_points: int = 5000,
                 duration_window: Optional[float] = None,
                 time_unit: float = 1.0,
                 **kwargs):
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.positions = positions
        self.num_neurons = int(num_neurons)
        self.max_points = int(max_points)
        self.duration_window = duration_window
        self.scatter = None

    def _setup_impl(self):
        self.scatter = self.ax.scatter([], [], s=2, color="k")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Neuron index")
        self.ax.set_title("Raster Plot (Real-time)")
        self.ax.set_ylim(-1, self.num_neurons)

    def _update_impl(self):
        spike_times_all: List[float] = []
        spike_ids_all: List[int] = []
        for spikes in self.data_buffer:
            if len(spikes) != 2:
                continue
            ids, times = spikes
            t = _to_seconds(times, self.time_unit)
            spike_ids_all.extend(np.asarray(ids, dtype=int))
            spike_times_all.extend(t)
        if spike_times_all:
            spike_times_all_arr = np.asarray(spike_times_all, dtype=float)
            spike_ids_all_arr = np.asarray(spike_ids_all, dtype=float)
            order = np.argsort(spike_times_all_arr)
            spike_times_all_arr = spike_times_all_arr[order]
            spike_ids_all_arr = spike_ids_all_arr[order]
            if spike_times_all_arr.size > self.max_points:
                spike_times_all_arr = spike_times_all_arr[-self.max_points:]
                spike_ids_all_arr = spike_ids_all_arr[-self.max_points:]
            current_time = spike_times_all_arr[-1]
            if self.duration_window is not None:
                t0 = max(0.0, current_time - self.duration_window)
            else:
                t0 = 0.0
            self.ax.set_xlim(t0, current_time + 0.05)
            self.scatter.set_offsets(np.column_stack((spike_times_all_arr, spike_ids_all_arr)))
        return [self.scatter]


class DynamicMembraneTracesION(DynamicPlotION):
    def __init__(self,
                 data_buffer: Deque[Tuple[Sequence[float], Sequence[Sequence[float]]]],
                 neurons_to_plot: Optional[Sequence[int]] = None,
                 time_window: float = 1.0,
                 Vth=None,
                 time_unit: float = 1.0,
                 volt_unit: float = 1.0,
                 **kwargs):
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.neurons_to_plot = list(neurons_to_plot) if neurons_to_plot is not None else list(range(5))
        self.time_window = float(time_window)
        self.Vth = Vth
        self.volt_unit = float(volt_unit)
        self.lines: List[plt.Line2D] = []

    def _setup_impl(self):
        self.lines = []
        for i in self.neurons_to_plot:
            line, = self.ax.plot([], [], label=f"Neuron {i}")
            self.lines.append(line)
        if self.Vth is not None:
            vth_val = _scalar_mV(self.Vth, self.volt_unit)
            self.ax.axhline(vth_val, color="red", linestyle="--", label="Threshold")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Membrane potential (mV)")
        self.ax.set_title("Membrane Potentials (Real-time)")
        self.ax.legend(loc="best")

    def _update_impl(self):
        if not self.data_buffer:
            return self.lines
        times, voltages = self.data_buffer[-1]
        times = _to_seconds(times, self.time_unit)
        voltages = _to_mV(voltages, self.volt_unit)
        voltages = np.asarray(voltages)
        if voltages.ndim == 1:
            voltages = voltages[None, :]
        if voltages.shape[0] != len(times) and voltages.shape[1] == len(times):
            voltages = voltages.T
        current_time = times[-1]
        self.ax.set_xlim(max(0.0, current_time - self.time_window), current_time + 0.05)
        if voltages.size:
            min_v = float(np.min(voltages))
            max_v = float(np.max(voltages))
            margin = (max_v - min_v) * 0.1 if max_v > min_v else 5.0
            self.ax.set_ylim(min_v - margin, max_v + margin)
        for i, line in enumerate(self.lines):
            if i < len(self.neurons_to_plot):
                neuron_idx = self.neurons_to_plot[i]
                if 0 <= neuron_idx < voltages.shape[0]:
                    line.set_data(times, voltages[neuron_idx])
                else:
                    line.set_data([], [])
        return self.lines


try:
    from utils import calculate_PVA  # type: ignore
except Exception:  # pragma: no cover
    def calculate_PVA(counts, angles):
        counts = np.asarray(counts, dtype=float)
        angles = np.asarray(angles, dtype=float)
        if counts.sum() == 0:
            return 0.0, 0.0
        vx = np.sum(counts * np.cos(angles))
        vy = np.sum(counts * np.sin(angles))
        angle = np.arctan2(vy, vx)
        mag = np.hypot(vx, vy) / counts.sum()
        return angle, mag


class DynamicPVAPlotION(DynamicPlotION):
    def __init__(self,
                 data_buffer: Deque[Tuple[Sequence[int], Sequence[float]]],
                 positions: Sequence[float],
                 num_neurons: int,
                 window_size: Union[float, object] = 0.05,
                 step_size: Union[float, object] = 0.01,
                 time_window: float = 2.0,
                 color_trail: bool = True,
                 time_unit: float = 1.0,
                 **kwargs):
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.positions = np.asarray(positions, dtype=float)
        self.num_neurons = int(num_neurons)
        self.window_size = _scalar_seconds(window_size)
        self.step_size = _scalar_seconds(step_size)
        self.time_window = float(time_window)
        self.color_trail = bool(color_trail)
        self.scatter = None
        self.times: List[float] = []
        self.pva_angles: List[float] = []
        self._last_processed_time: float = 0.0

    def _setup_impl(self):
        self.scatter = self.ax.scatter([], [], s=5, c=[], cmap="viridis")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Decoded angle (rad)")
        self.ax.set_ylim(0, 2 * np.pi)
        self.ax.set_title("Time-Resolved PVA (Real-time)")
        if self.color_trail:
            self.cbar = plt.colorbar(self.scatter, ax=self.ax, label="Time (s)")

    def _update_impl(self):
        all_ids: List[int] = []
        all_times: List[float] = []
        for spikes in self.data_buffer:
            if len(spikes) != 2:
                continue
            ids, t = spikes
            t_s = _to_seconds(t, self.time_unit)
            all_ids.extend(np.asarray(ids, dtype=int))
            all_times.extend(t_s)
        if not all_times:
            return [self.scatter]
        all_ids_arr = np.asarray(all_ids, dtype=int)
        all_times_arr = np.asarray(all_times, dtype=float)
        order = np.argsort(all_times_arr)
        all_times_arr = all_times_arr[order]
        all_ids_arr = all_ids_arr[order]
        all_ids_arr = np.clip(all_ids_arr, 0, self.num_neurons - 1)
        current_time = all_times_arr[-1]
        t_start = self._last_processed_time
        t_bins = np.arange(t_start, current_time, self.step_size)
        for tb in t_bins:
            win_start = tb
            win_end = tb + self.window_size
            mask = (all_times_arr >= win_start) & (all_times_arr < win_end)
            if not np.any(mask):
                continue
            window_ids = all_ids_arr[mask]
            counts = np.zeros(self.num_neurons, dtype=float)
            np.add.at(counts, window_ids, 1.0)
            angle, _ = calculate_PVA(counts, self.positions)
            if angle < 0:
                angle += 2 * np.pi
            self.times.append(tb)
            self.pva_angles.append(angle)
        self._last_processed_time = current_time
        if self.times:
            offs = np.column_stack((self.times, self.pva_angles))
            self.scatter.set_offsets(offs)
            if self.color_trail:
                arr = np.asarray(self.times, dtype=float)
                self.scatter.set_array(arr)
                norm_min = max(0.0, self.times[-1] - self.time_window)
                norm_max = self.times[-1]
                self.scatter.set_norm(plt.Normalize(vmin=norm_min, vmax=norm_max))
            self.ax.set_xlim(max(0.0, self.times[-1] - self.time_window), self.times[-1] + 0.05)
        return [self.scatter]


class DynamicPlotManagerION:
    def __init__(self, update_interval: int = 100):
        self.update_interval = int(update_interval)
        self.plots_specs: List[Tuple[type, dict]] = []
        self.fig = None
        self.axes = None
        self.plots: List[DynamicPlotION] = []
        self._timer = None
        self._running_block = False

    def add_plot(self, plot_class, **kwargs):
        self.plots_specs.append((plot_class, kwargs))
        return self

    def setup(self):
        plt.ion()
        n = len(self.plots_specs)
        self.fig, self.axes = plt.subplots(n, 1, figsize=(10, 5 * n))
        if n == 1:
            self.axes = [self.axes]
        self.plots = []
        for ax, (cls, kwargs) in zip(self.axes, self.plots_specs):
            kw = dict(kwargs)
            kw["fig"] = self.fig
            kw["ax"] = ax
            kw["update_interval"] = self.update_interval
            plot = cls(**kw).setup()
            self.plots.append(plot)
        self.fig.canvas.mpl_connect("close_event", self._on_close)
        self.fig.tight_layout()
        return self

    def update_once(self):
        for plot in self.plots:
            plot.update_once()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def run(self, block: bool = True):
        if self.fig is None:
            self.setup()
        dt = self.update_interval / 1000.0
        if block:
            self._running_block = True
            try:
                while self._running_block and plt.fignum_exists(self.fig.number):
                    self.update_once()
                    plt.pause(dt)
            finally:
                self._running_block = False
        else:
            self.update_once()
            plt.pause(0.001)
        return self

    def start_background(self):
        if self.fig is None:
            self.setup()
        if self._timer is not None:
            return self
        self._timer = self.fig.canvas.new_timer(interval=self.update_interval)
        self._timer.add_callback(self.update_once)
        self._timer.start()
        return self

    def stop_background(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        return self

    def _on_close(self, event):
        self.stop_background()
        self._running_block = False


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    N = 50
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    raster_buffer = deque(maxlen=100)
    vmem_buffer = deque(maxlen=50)
    pva_buffer = deque(maxlen=100)
    mgr = (DynamicPlotManagerION(update_interval=50)
           .add_plot(DynamicRasterPlotION, data_buffer=raster_buffer, num_neurons=N, duration_window=1.0)
           .add_plot(DynamicMembraneTracesION, data_buffer=vmem_buffer, neurons_to_plot=[0, 1, 2], time_window=0.5, Vth=-50)
           .add_plot(DynamicPVAPlotION, data_buffer=pva_buffer, positions=angles, num_neurons=N, window_size=0.05, step_size=0.01, time_window=1.0))
    mgr.setup()
    t = 0.0
    dt = 0.02
    while plt.fignum_exists(mgr.fig.number) and t < 10.0:
        nspk = rng.poisson(2)
        ids = rng.integers(0, N, size=nspk)
        times = np.full(nspk, t)
        raster_buffer.append((ids, times))
        pva_buffer.append((ids, times))
        if vmem_buffer:
            prev_t, prev_v = vmem_buffer[-1]
            times_v = np.append(prev_t, t)
            prev_v = np.asarray(prev_v)
            if prev_v.shape[0] == N:
                new_v = np.column_stack((prev_v, rng.normal(-60, 5, size=N)))
            else:
                new_v = np.vstack((prev_v, rng.normal(-60, 5, size=N)))
        else:
            times_v = np.array([t])
            new_v = rng.normal(-60, 5, size=(N, 1))
        if times_v.size > 1000:
            times_v = times_v[-1000:]
            new_v = new_v[:, -1000:]
        vmem_buffer.append((times_v, new_v))
        mgr.run(block=False)
        t += dt
        time.sleep(dt)
    mgr.run(block=False)
