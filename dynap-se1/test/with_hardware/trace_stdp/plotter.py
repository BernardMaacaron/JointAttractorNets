import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import os
import time
import sys
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
from dynapse1utils import get_selected_timestamps, get_selected_traces

def plot_w(w_plast, figpath="./w"):
    isExists=os.path.exists(figpath)
    if not isExists:
        os.makedirs(figpath)
        
    fig = plt.figure(figsize=(14,12))
    sns.heatmap(w_plast)
    plt.title("w_plast")
    plt.xlabel("post")
    plt.ylabel("pre")
    fig.savefig(figpath+"/w"+str(int(round(time.time() * 1000))))
    del fig

def plot_raster(spikes, neuron_ids, t_start=None, t_end=None, axvline_spikes=False):
    """
    plot the raster of neuron_ids from collected spikes.
    spikes: spike
    """
    if len(set(neuron_ids)) != len(neuron_ids):
        raise Exception("Duplicate neuron ids exist!")
    
    timestamps = get_selected_timestamps(spikes, neuron_ids)

    ax = plt.subplot()
    for i in range(len(neuron_ids)):
        print(i, timestamps[i])
        ax.plot(timestamps[i], np.ones(len(timestamps[i]))*i, '.', label=str(i)+': '+str(neuron_ids[i]))

        if axvline_spikes:
            for time in timestamps[i]:
                plt.axvline(time)
    
    if t_start != None and t_end != None:
        ax.set_xlim(t_start, t_end)
    
    ax.legend()

def plot_trace(timed_traces, neuron_ids, t_start=None, t_end=None):
    """
    plot the raster of neuron_ids from collected spikes.
    spikes: spike
    """
    if len(set(neuron_ids)) != len(neuron_ids):
        raise Exception("Duplicate neuron ids exist!")
    
    timestamps, trace_values = get_selected_traces(timed_traces, neuron_ids)

    ax = plt.subplot()
    for i in range(len(neuron_ids)):
        print(timestamps[i], trace_values[i])
        ax.plot(timestamps[i], trace_values[i], '.-', label=str(i)+': '+str(neuron_ids[i]))
    
    if t_start != None and t_end != None:
        ax.set_xlim(t_start, t_end)
    
    ax.legend()