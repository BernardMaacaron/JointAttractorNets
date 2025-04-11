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
sys.path.append('Neuron and Synapse Models')
from neuronModels import *
from ringAttractorTEMP import *

sys.path.append('Tools')
from plottingTools import *
# -

# Simulation parameters
defaultclock.dt = 0.1*ms

# Setting network parameters
num_neurons = 120
tau=10*ms
sigma_noise=1*mV
V_rest=-70*mV

# +
# External input: a spatially modulated current.

# For example, we define a Gaussian input centered at a particular position (stimulus_center)
stimulus_center = 0  # center of the bump on the ring
stimulus_width = 0.5  # width in radians
I0 = 30*mV         # amplitude of the external input

# Define the external input as a function of neuron position
positions = linspace(0, 2*pi, num_neurons, endpoint=False)
# I_ext_array = I0 * exp(-((positions - stimulus_center)**2) / (2 * stimulus_width**2))
d = np.angle(np.exp(1j * (positions - stimulus_center)))
I_ext_array = I0 * np.exp(-(d**2) / (2 * stimulus_width**2))
# -

# Creating the equation object
neuron_eq = Equations(LIF_xi_eq, tau=tau, V_rest=V_rest, sigma_noise=sigma_noise)

# +
# Create neuron group
Vth=-48*mV
V_reset=-80*mV
refractory_period=5*ms

# Connectivity parameters - Mexican hat
sigma_exc = 0.1
sigma_inh = 0.164
g_exc = 0.7848*mV
g_inh = -0.5456*mV
            
            
ringAttractor = RingAttractor(neuron_eq, 
                 num_neurons, 
                 Vth, V_reset, refractory_period,
                 # Choose connectivity profile: 'mexican_hat', 'gaussian', or 'cosine'
                 syn_profile='mexican_hat',
                 autapse=True,
                 sigma_exc=sigma_exc, sigma_inh=sigma_inh, g_exc=g_exc, g_inh=g_inh) # Connectivity parameters for Mexican hat
ringAttractor.ring_pool.I_ext = I_ext_array

# Network Operations:
# Clipping - Reverse Potential Behaviour
# Define a network operation to enforce the lower bound
@network_operation(dt=defaultclock.dt)
def enforce_lower_bound():
    # Using the built-in clip function (from numpy)
    ringAttractor.ring_pool.V[:] = clip(ringAttractor.ring_pool.V[:], V_reset, inf*volt)
    


# +
# Setup monitors: spike monitor and state monitor for membrane potential and external input
spikemon = SpikeMonitor(ringAttractor.ring_pool)
statemon = StateMonitor(ringAttractor.ring_pool, 'V', record=True)
inputmon = StateMonitor(ringAttractor.ring_pool, 'I_ext', record=True)  # if you want to check the input

net = Network(ringAttractor.BrianObjects + [enforce_lower_bound, spikemon, statemon, inputmon])

input_on = 500*ms
input_off = 1*second
sim_duration=input_on+input_off

# Run simulation
net.run(input_on)
# Turn off input for the second half
ringAttractor.ring_pool.I_ext = I_ext_array * 0
net.run(input_off)

# #+---------------------------------------------------------------------------+
#|                           Plotting the Results                            |
# #+---------------------------------------------------------------------------+

# Create a figure with multiple subplots using the modified plottingTools functions
fig = plt.figure(figsize=(15, 15))

# 1. Input Current Plot
ax1 = fig.add_subplot(4, 2, 1)
ax1.plot(positions/(2*pi), I_ext_array/mV)
ax1.set_title('Input Current')
ax1.set_xlabel('Position (rad)')
ax1.set_ylabel('Current (mV)')

# 2. TBD
ax2 = fig.add_subplot(4, 2, 2)
ax2.plot(positions/(2*pi), I_ext_array/mV)
ax2.set_title('Input Current')
ax2.set_xlabel('Time (ms)')
ax2.set_ylabel('Current (mV)')

# 3. Raster Plot
ax3 = fig.add_subplot(4, 2, 3)
raster_plot(spikemon, ax=ax3, stim_periods=(0,input_on/second), stim_display_method='highlight', duration=sim_duration)

# 3. Raster Plot
ax4 = fig.add_subplot(4, 2, 4)
raster_plot(spikemon, ax=ax4, stim_periods=(0,input_on/second), stim_display_method='highlight', duration=sim_duration)

# 4. Firing Rate Profile Plot
ax4 = fig.add_subplot(4, 2, 5)
firing_rate, _ = firing_rate_profile(spikemon, positions/(2*pi), sim_duration, ax=ax4)

# 5. Polar Plot of the Population Vector Average (PVA)
ax5 = fig.add_subplot(4, 2, 6, projection='polar')
polar_plot_PVA(firing_rate, positions, scale=1.2, ax=ax5)

# TODO:  Modify the function to highlight the sdcreen not the neurons
# 6. Time-Resolved PVA Plot
ax6 = fig.add_subplot(4, 2, 7)
_, _ = time_resolved_PVA(spikemon, positions, sim_duration, num_neurons, ax=ax6, color_windows=True)

# 7. Membrane potential traces
ax7 = fig.add_subplot(4, 2, 8)
membrane_potential_traces(statemon, sim_duration, ax=ax7)

plt.tight_layout()
plt.show()
