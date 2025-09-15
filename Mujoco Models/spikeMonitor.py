#!/usr/bin/env python3
"""Tail a spikes.txt file in (almost) real time and render a scrolling raster plot
using the *ION-based* dynamic plotting classes.

This version replaces the FuncAnimation-driven usage with the new
`DynamicRasterPlotION` + `DynamicPlotManagerION` API. The manager handles
interactive mode, timed redraws, and clean shutdown when the figure closes.
"""

import os
import sys
import threading
import time
from collections import deque
from typing import Deque, Tuple, Sequence

import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
#  Import dynamic plotting tools (ION version)
# -----------------------------------------------------------------------------
# Ensure the Tools directory (sibling to this script) is importable.
SCRIPT_DIR = os.getcwd()
TOOLS_DIR = os.path.join(SCRIPT_DIR, 'Tools')
if TOOLS_DIR not in sys.path:
    print(f"Adding Tools directory to sys.path: {TOOLS_DIR}")
    sys.path.append(TOOLS_DIR)

# Import the ION-based plotter classes. Adjust module name if you saved them differently.
from dynamicPlottingToolsCopy import DynamicRasterPlotION, DynamicPlotManagerION  # type: ignore

# -----------------------------------------------------------------------------
#  Paths and plot parameters
# -----------------------------------------------------------------------------
PROJECT_DIR = os.getcwd()  # current working dir (adjust as needed)
SPIKE_DIR = os.path.join(PROJECT_DIR, 'Mujoco Models')
SPIKE_FILE = os.path.join(SPIKE_DIR, 'spikes.txt')
print(f"Using spike file: {SPIKE_FILE}")

N_NEURONS   = 120
UPDATE_MS   = 50                 # redraw interval for the plot manager (ms)
TAIL_SLEEP  = 0.005              # polling delay for file tail (s)
MAX_POINTS  = 1000               # max points displayed in raster
WINDOW_S    = 0.5                # seconds visible in raster window

# Ensure the spikes directory exists and the file is present.
os.makedirs(SPIKE_DIR, exist_ok=True)
open(SPIKE_FILE, 'a').close()

# -----------------------------------------------------------------------------
#  Shared data buffer read by the plotter
# -----------------------------------------------------------------------------
# Each entry: (ids_array, times_array). Times already in seconds.
data_buffer: Deque[Tuple[Sequence[int], Sequence[float]]] = deque(maxlen=100)

# -----------------------------------------------------------------------------
#  Background tail-thread: read new lines, batch, push into buffer
# -----------------------------------------------------------------------------

def tail_spikes(fpath: str, buf: Deque[Tuple[np.ndarray, np.ndarray]], stop_evt: threading.Event) -> None:
    with open(fpath, 'r') as f:
        # f.seek(0, os.SEEK_END)  # live view – skip old data
        bucket_ids = []
        bucket_times = []
        last_flush = time.perf_counter()
        flush_interval = UPDATE_MS / 1000.0
        while not stop_evt.is_set():
            line = f.readline()
            if not line:
                time.sleep(TAIL_SLEEP)
                continue
            try:
                nid_str, ts_str = line.split(maxsplit=1)
                bucket_ids.append(int(nid_str))
                bucket_times.append(float(ts_str))
            except ValueError:
                continue
            if (time.perf_counter() - last_flush) >= flush_interval:
                if bucket_ids:
                    buf.append((
                        np.asarray(bucket_ids, dtype=np.int32),
                        np.asarray(bucket_times, dtype=np.float64),
                    ))
                    bucket_ids.clear()
                    bucket_times.clear()
                last_flush = time.perf_counter()
        # flush on shutdown
        if bucket_ids:
            buf.append((
                np.asarray(bucket_ids, dtype=np.int32),
                np.asarray(bucket_times, dtype=np.float64),
            ))


# -----------------------------------------------------------------------------
#  Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    stop_evt = threading.Event()
    tail_thread = threading.Thread(
        target=tail_spikes,
        args=(SPIKE_FILE, data_buffer, stop_evt),
        daemon=True,
    )
    tail_thread.start()
    
    # Build a manager with a single raster plot.
    mgr = (DynamicPlotManagerION(update_interval=UPDATE_MS)
           .add_plot(DynamicRasterPlotION,
                     data_buffer=data_buffer,
                     num_neurons=N_NEURONS,
                     max_points=MAX_POINTS,
                     duration_window=WINDOW_S,
                     time_unit=1.0))
    mgr.setup()

    try:
        # Run a blocking interactive loop; window closes when user closes figure.
        mgr.run(block=True)
    finally:
        stop_evt.set()
        tail_thread.join(timeout=1.0)
        mgr.stop_background()  # no-op if not started
        print('Plot closed; live_plot_ion.py exiting.')
