
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import pandas as pd

from brian2 import *

nsm_path = os.path.join(os.path.dirname(__file__), 'Neuron and Synapse Models')
sys.path.append(nsm_path)
from ringAttractorClassExtended import FaithfulBoundedRingAttractor
from neuronModels import LIF_xi_vel_eq,LIF_synapticDecay_xi_vel_eq

tools_path = os.path.join(os.path.dirname(__file__), 'Tools')
sys.path.append(tools_path)
from utils import computeInstRate, computePVA, computePVATT
from plottingTools import raster_plot
import glob



def main_simple_5s(velInput=1.0):
    total_time = 8*second
    dt = 0.1*ms
    velInput = velInput
    neuron_eq = Equations(LIF_synapticDecay_xi_vel_eq, tau=10*ms, V_rest=-70*mV, sigma_noise=0.0*mV,tau_s=10*ms)
    # ring = FaithfulBoundedRingAttractor(neuron_eq, w_sub=-0.33478*mV, g_cosine=0.33496*mV, limit_neuron=None)
    ring = FaithfulBoundedRingAttractor(neuron_eq, w_sub=-10.14*mV, g_cosine=10.14*mV, limit_neuron=29)
    ring.ring_pool.run_regularly('V = clip(V, -80*mV, inf*volt)', dt=dt)
    defaultclock.dt = dt
    I0 = 80.0 * mV
    I_ext_array = np.ones(ring.numNeurons) * I0
    I_ext_array[10]+=10.0*mV
    
    
    
    ring.ring_pool.I_ext = I_ext_array
    ring.spikeMonitor = SpikeMonitor(ring.ring_pool)
    net = Network(ring.BrianObjects + [ring.spikeMonitor])
    # 1. Initialization: run 50ms with velocity OFF
    ring.ring_pool.I_ext = I_ext_array
    ring.ring_synapses_asym.vel_in = velInput
    ring.ring_synapses_asym.vel_on = False
    net.run(50*ms)
    I_ext_array[10] -= 10*mV
    ring.ring_pool.I_ext = I_ext_array
    
    
    n_steps = int(total_time/(50*ms))
    simTime = 0*ms
    pva_angles = []
    pva_times = []
    for i in range(n_steps):
        # Flip velInput sign every 1s
        sign = 1 if ((i*50*ms)//second)%2 == 0 else -1
        ring.ring_synapses_asym.vel_in = sign * (velInput)
        ring.ring_synapses_asym.vel_on = True
        net.run(50*ms)
        simTime += 50*ms
        firingRates = computeInstRate(ring.spikeMonitor, ring.numNeurons, meanISI=True)
        # pva_angle, _ = computePVA(firingRates, ring.positions)
        pva_times.append(simTime/second)
    pva_angle, time_windows = computePVATT(ring.spikeMonitor, ring.positions,total_time,120, 50*ms,10*ms)
    # pva_angles.append(np.rad2deg(pva_angle))
    
    # Plot finale raster
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    raster_plot(ring.spikeMonitor, ax=ax, stim_periods=(0*second, simTime),
                stim_display_method='highlight', duration=simTime, num_neurons=ring.numNeurons, y_axisFull=True)
    plt.title('Raster plot totale (5s)')
    plt.savefig('simple_network_raster.png')
    plt.show(block=True)
    # Plot PVA angle vs time
    plt.figure(figsize=(8, 4))
    plt.plot(np.array(time_windows)*1000, np.rad2deg(pva_angle), marker='o')
    plt.xlabel('Time (ms)')
    plt.ylabel('PVA angle (deg)')
    plt.title('PVA angle vs time (ogni 50ms)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('pva_angle_vs_time.png')
    plt.show(block=True)






if __name__ == "__main__":
    main_simple_5s(velInput=2*0.998)