from brian2 import *
import numpy as np

import sys
sys.path.append('Neuron and Synapse Models')
from neuronModels import *
from ringAttractorTEMP import *
sys.path.append('Tools')
from utils import *

def opt_ring_attractor(params, stim_center=0, stim_width=0.5):
    """
    Run the ring attractor simulation with the specified parameters.
    
    Parameters:
        params (dict): A dictionary containing parameter values, e.g.,
                       {
                         'tau': value,
                         'sigma_noise': value,
                         'sigma_exc': value,
                         'sigma_inh': value,
                         'g_exc': value,
                         'g_inh': value,
                         ... (others as needed)
                       }
    Returns:
        result: Any outcome from the simulation you wish to optimize (e.g., a cost metric)
    """
    # --- Simulation parameters ---
    defaultclock.dt = 0.1*ms
    num_neurons = 120

    # Use parameters from the dict, with appropriate units:
    tau = params.get('tau', 10)*ms
    sigma_noise = params.get('sigma_noise', 1)*mV
    V_rest = -70*mV

    # External input parameters (could also be passed in or kept fixed)
    stimulus_center = stim_center  
    stimulus_width = stim_width  
    I0 = 30*mV
    positions = linspace(0, 2*pi, num_neurons, endpoint=False)
    d = np.angle(np.exp(1j * (positions - stimulus_center)))
    I_ext_array = I0 * np.exp(-(d**2) / (2 * stimulus_width**2))
        
    # Create the neuron model equations using your custom LIF model
    neuron_eq = Equations(LIF_xi_eq, tau=tau, V_rest=V_rest, sigma_noise=sigma_noise)
    
    # Fixed intrinsic properties for now:
    Vth = -48*mV
    V_reset = -80*mV
    refractory_period = 5*ms

    # Connectivity parameters (use parameters if provided or defaults)
    sigma_exc = params.get('sigma_exc', 0.1)
    sigma_inh = params.get('sigma_inh', 0.164)
    g_exc = params.get('g_exc', 0.7848)*mV
    g_inh = params.get('g_inh', -0.5456)*mV

    # Create the ring attractor network
    ringAttractor = RingAttractor(neuron_eq, 
                     num_neurons, 
                     Vth, V_reset, refractory_period,
                     syn_profile='mexican_hat',
                     autapse=True,
                     sigma_exc=sigma_exc, sigma_inh=sigma_inh, 
                     g_exc=g_exc, g_inh=g_inh)
    ringAttractor.ring_pool.I_ext = I_ext_array

    # Clipping operation: enforce lower bound
    @network_operation(dt=defaultclock.dt)
    def enforce_lower_bound():
        ringAttractor.ring_pool.V[:] = clip(ringAttractor.ring_pool.V[:], V_reset, inf*volt)

    # Set up monitors
    spikemon = SpikeMonitor(ringAttractor.ring_pool)
    statemon = StateMonitor(ringAttractor.ring_pool, 'V', record=True)

    # Build the network and run simulation
    net = Network(ringAttractor.BrianObjects + [enforce_lower_bound, spikemon, statemon])
    input_on = 500*ms
    input_off = 1*second
    sim_duration = input_on + input_off
    
    net.run(input_on)
    ringAttractor.ring_pool.I_ext = I_ext_array * 0  # turn off input in second half
    net.run(input_off)
    
    firing_rates = compute_firing_rate(spikemon, num_neurons, start_time=0.95*sim_duration, end_time=sim_duration)
    pva_angle, pva_magnitude = calculate_PVA(firing_rates, positions)
    
    # Return simulation results
    return stimulus_center, I_ext_array, firing_rates, pva_angle, pva_magnitude

if __name__ == '__main__':
    # Example: run with default parameters when this file is executed directly
    default_params = {'tau': 10, 'sigma_noise': 1.0, 'sigma_exc': 0.125, 'sigma_inh': 0.1, 'g_exc': 1.0, 'g_inh': -1.0}
    GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude = opt_ring_attractor(default_params,  stim_center=0, stim_width=0.5)   
    print("Ground Truth Center:", GT_center)
    print("Ground Truth Input:", GT_input)
    print("Observed Firing Rates:", out_rates)
    print("PVA Angle:", out_pva_angle)
    print("PVA Magnitude:", out_pva_magnitude)
    