#!/usr/bin/env python3
"""
Tail standalone/spikes.txt in (almost) real time and feed the batches
into Tools.dynamicPlottingTools.DynamicRasterPlot
"""

import os
import threading
import time
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from Tools.dynamicPlottingTools import DynamicRasterPlot   # your helper

# ------------------------------------------------------------
#  Paths and plot parameters
# ------------------------------------------------------------
# Get the absolute path to the project root using the notebook's working directory
PROJECT_DIR = os.getcwd()

# Create absolute paths
SPIKE_FILE = os.path.join(PROJECT_DIR, 'spikes.txt')
N_NEURONS     = 120
UPDATE_MS     = 50                # must match raster_plot.update_interval
TAIL_SLEEP    = 0.005             # polling delay (s)

# make sure the spike file exists, even before the writer starts
os.makedirs(PROJECT_DIR, exist_ok=True)
open(SPIKE_FILE, "a").close()



# ------------------------------------------------------------
#  Data buffer and raster plot
# ------------------------------------------------------------
data_buffer = deque(maxlen=100)   # keeps last 100 batches

raster_plot = DynamicRasterPlot(
    data_buffer=data_buffer,
    num_neurons=N_NEURONS,
    max_points=1000,
    duration_window=0.5,          # seconds visible
    time_unit=1.0,                # times already in seconds
    update_interval=UPDATE_MS
)
animation = raster_plot.start()

# ------------------------------------------------------------
#  Background tail-thread: read new lines, batch, push
# ------------------------------------------------------------
def tail_spikes(fpath, buf, stop_evt):
    with open(fpath, "r") as f:
        f.seek(0, os.SEEK_END)           # live view – skip old data
        bucket_ids, bucket_times = [], []
        last_flush = time.perf_counter()

        while not stop_evt.is_set():
            line = f.readline()
            if not line:
                time.sleep(TAIL_SLEEP)
                continue

            try:
                nid, ts = line.split(maxsplit=1)
                bucket_ids.append(int(nid))
                bucket_times.append(float(ts))
            except ValueError:
                continue

            if (time.perf_counter() - last_flush) >= UPDATE_MS / 1000.0:
                if bucket_ids:
                    buf.append((
                        np.asarray(bucket_ids,   dtype=np.int32),
                        np.asarray(bucket_times, dtype=np.float64)
                    ))
                    bucket_ids.clear()
                    bucket_times.clear()
                    last_flush = time.perf_counter()

        # flush leftovers on shutdown
        if bucket_ids:
            buf.append((
                np.asarray(bucket_ids,   dtype=np.int32),
                np.asarray(bucket_times, dtype=np.float64)
            ))

stop_evt = threading.Event()
tail_thread = threading.Thread(
    target=tail_spikes,
    args=(SPIKE_FILE, data_buffer, stop_evt),
    daemon=True
)
tail_thread.start()

# ------------------------------------------------------------
#  Show the plot window
# ------------------------------------------------------------
try:
    plt.show(block=True)      # blocks until user closes the window
finally:
    stop_evt.set()
    tail_thread.join(timeout=1.0)

print("Plot closed; live_plot.py exiting.")
