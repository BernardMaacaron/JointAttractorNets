from brian2 import *
import numpy as np

import os # Print current working directory
import sys
sys.path.append('Neuron and Synapse Models')
from neuronModels import *
from ringAttractorClass import *
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
    set_device('cpp_standalone', build_on_run=False)  # Use C++ standalone mode for performance
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
    neuron_eq = Equations(LIF_xi_vel_eq, tau=tau, V_rest=V_rest, sigma_noise=sigma_noise)
    
    # Fixed intrinsic properties for now:
    Vth = -48*mV
    V_reset = -80*mV
    refractory_period = 5*ms

    # Create the ring attractor with prepared parameters
    ringAttractor = RingAttractor(neuron_eq, 
                     num_neurons, 
                     Vth, V_reset, refractory_period,
                     **params)
    ringAttractor.ring_pool.I_ext = I_ext_array

    # Clipping operation: enforce lower bound
    @network_operation(dt=defaultclock.dt)
    def enforce_lower_bound():
        ringAttractor.ring_pool.V[:] = clip(ringAttractor.ring_pool.V[:], V_reset, inf*volt)

    # Set up monitors
    spikemon = SpikeMonitor(ringAttractor.ring_pool)
    statemon = StateMonitor(ringAttractor.ring_pool, 'V', record=True)
    
    # Additional monitor for global inhibitory neuron if it exists
    if params.get('syn_profile', 'mexican_hat') == 'cosine' and params.get('glob_inh', False):
        spikemon_inh = SpikeMonitor(ringAttractor.glob_inh_neuron)
        statemon_inh = StateMonitor(ringAttractor.glob_inh_neuron, 'V', record=True)
        monitors = [enforce_lower_bound, spikemon, statemon, spikemon_inh, statemon_inh]
    else:
        monitors = [enforce_lower_bound, spikemon, statemon]

    # Build the network and run simulation
    net = Network(ringAttractor.BrianObjects + monitors)
    input_on = 0.5*second
    input_off = 0.2*second
    sim_duration = input_on + input_off
    
    net.run(input_on)
    ringAttractor.ring_pool.I_ext = I_ext_array * 0  # turn off input in second half
    net.run(input_off)
    
    build_directory = os.path.join(os.getcwd(), 'Optimization Models', 'optimizationModel_build')
    device.build(directory=build_directory, compile=True, run=True, debug=False)
    
    firing_rates = compute_firing_rate(spikemon, num_neurons,
                                       start_time=input_on, end_time=sim_duration)
                                    #    start_time=0.95*sim_duration, end_time=sim_duration)
                                    
    pva_angle, pva_magnitude = calculate_PVA(firing_rates, positions)
    
    # Return simulation results
    return stimulus_center, I_ext_array, firing_rates, pva_angle, pva_magnitude

if __name__ == '__main__':
    # Example: run with default parameters when this file is executed directly
    default_params = {'tau': 10, 'sigma_noise': 1.0, 'sigma_exc': 0.125, 'sigma_inh': 0.1, 'g_exc': 1.0*mV, 'g_inh': -1.0*mV, 'syn_profile': 'mexican_hat', 'autapse': True, 'glob_inh': False}
    GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude = opt_ring_attractor(default_params,  stim_center=0, stim_width=0.5)   
    print("Ground Truth Center:", GT_center)
    print("Ground Truth Input:", GT_input)
    print("Observed Firing Rates:", out_rates)
    print("PVA Angle:", out_pva_angle)
    print("PVA Magnitude:", out_pva_magnitude)