# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: JointAttractorNets-Brian2
#     language: python
#     name: python3
# ---

# +
from brian2 import *
import sys
# sys.path = [p for p in sys.path if 'Neuron and Synapse Models' not in p and 'Tools' not in p]
sys.path.append('Neuron and Synapse Models')
sys.path.append('Tools')

from neuronModels import *
from ringAttractorTEMP import *
from plottingTools import *
from utils import *

import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

from multiprocessing import Pool
import itertools
from tqdm import tqdm
import pandas as pd

# Simulation parameters
defaultclock.dt = 0.1*ms


# +
def fit_result(rate):
        positions = linspace(0, 360, 120, endpoint=False)
        spike = gaussian_filter1d(rate, sigma=3)
        psi=positions[np.argmax(spike)]
        width= np.argwhere(spike>2)
        return psi,len(width)

def bump_orientation(rate):
    # Check if the rates are all zero
    activity= np.any(rate>0.0)
    if activity:
        not_avalanche = np.any(rate==0.0)
        if not_avalanche:
            psi,width= fit_result(rate)
        else:
            psi,width= nan,nan
    else:
        psi,width=nan,nan
    return psi,width
 


# -

def run_simulator(sigma_exc_val, sigma_inh_val, g_exc_val, g_inh_val):
    # Convert slider values to Brian units
    tau = 10 * ms
    sigma_noise = 1 * mV
    V_rest = -70 * mV
    I0 = 30 * mV
    num_neurons = 120

    stimulus_center=0 #rad
    stimulus_width=0.5


    # Define neuron positions
    positions = linspace(0, 2*pi, num_neurons, endpoint=False)

    # Calculate external input
    d = np.angle(np.exp(1j * (positions - stimulus_center)))
    I_ext_array = I0 * np.exp(-(d**2) / (2 * stimulus_width**2))


    # Set up neuron model
    neuron_eq = Equations(LIF_xi_eq, tau=tau, V_rest=V_rest, sigma_noise=sigma_noise)

    # Set up ring attractor
    Vth = -48 * mV
    V_reset = -80 * mV
    refractory_period = 5 * ms

    syn_profile = 'mexican_hat'
    # Create the ring attractor network
    ringAttractor = RingAttractor(neuron_eq, 
                            num_neurons, 
                            Vth, V_reset, refractory_period,
                            syn_profile=syn_profile,
                            autapse=True,
                            sigma_exc=sigma_exc_val,
                            sigma_inh=sigma_inh_val,
                            g_exc=g_exc_val,
                            g_inh=g_inh_val) 

    # Set external input
    ringAttractor.ring_pool.I_ext = I_ext_array

    # Setup monitors
    spikemon = SpikeMonitor(ringAttractor.ring_pool)
    statemon = StateMonitor(ringAttractor.ring_pool, 'V', record=True)
    inputmon = StateMonitor(ringAttractor.ring_pool, 'I_ext', record=True)

    net = Network(ringAttractor.BrianObjects + [spikemon, statemon, inputmon])

    input_on = 500*ms
    input_off = 1*second
    sim_duration=input_on+input_off

    # Run simulation
    net.run(input_on)
    # Turn off input for the second half
    ringAttractor.ring_pool.I_ext = I_ext_array * 0
    net.run(input_off)
    
    start_time, end_time = sim_duration-20*ms, sim_duration
    rate = compute_firing_rate(spikemon, num_neurons, start_time, end_time)
    psi, width = bump_orientation(rate)

    mu2 = np.rad2deg(stimulus_center)
    if not np.isnan(psi) :
        accuracy_pos = 1-np.abs((min(np.abs(psi-mu2), 360 - np.abs(psi-mu2))/180))
    else:
        accuracy_pos = 0
    if not np.isnan(width):
        if width<10 and width!=0:
            width=10
        if width==0:
            accuracy_spread =0
        else:
            accuracy_spread =(120-width)/110
    else:
        accuracy_spread =0
    accuracy = (accuracy_pos + accuracy_spread)/2
    
    return accuracy_pos, accuracy_spread, accuracy


def tuning_parameters():
    # Create search space for these parameters:
    sigma_exc_val = np.round(np.geomspace(0.1, 10, num=20),4)
    sigma_inh_val = np.round(np.geomspace(0.1, 10, num=20),4)
    g_exc_val = np.round(np.geomspace(0.01, 10, num=20),4)*mV
    g_inh_val = np.round(np.geomspace(0.01, 10, num=20),4)*mV
    g_inh_val = -g_inh_val  

    combinations = list(itertools.product(sigma_exc_val, sigma_inh_val, g_exc_val, g_inh_val))

    weights=pd.DataFrame(combinations,columns=["sigma_exc_val", "sigma_inh_val", "g_exc_val", "g_inh_val"])
    weights_shuffled = weights.apply(lambda x: x.sample(frac=1).values)
    weights_subset = weights_shuffled.iloc[:int(len(weights_shuffled) * 0.02)]
    
    with Pool(48) as pool:
        res = pool.starmap(run_simulator,tqdm(weights_subset.values, total=len(weights_subset)))
    res = np.array(res)
    acc_bumpPos=list(res[:, 0])
    acc_bumpWidth=list(res[:, 1])
    acc_tot=list(res[:, 2])
    results=weights_subset.copy()
    results["Accuracy psi"],results["Accuracy width"],results["Total Accuracy"]=acc_bumpPos,acc_bumpWidth,acc_tot
    results = results.sort_values(by="Total Accuracy", ascending=False).reset_index(drop=True)

    results.to_csv(f"accuracy_Mexican_hat.csv", index=False)


if __name__ == '__main__':
    tuning_parameters()