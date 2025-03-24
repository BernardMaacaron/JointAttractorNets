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

# Plot the external input
figure()
plot(positions/(2*pi), I_ext_array/mV)
xlabel('Position (radians)')
ylabel('External input (mV)')
show()

# Creating the equation object
neuron_eq = Equations(LIF_xi_eq, tau=tau, V_rest=V_rest, sigma_noise=sigma_noise)

# +
# Create neuron group
Vth=-48*mV
V_reset=-80*mV
refractory_period=5*ms

# Connectivity parameters - Mexican hat
sigma_exc = 1.0 
sigma_inh = 3.0
g_exc = 0.1*mV
g_inh = -0.15*mV
            
            
ringAttractor = RingAttractor(LIF_xi_eq, 
                 num_neurons, 
                 Vth, V_reset, refractory_period,
                 # Choose connectivity profile: 'mexican_hat', 'gaussian', or 'cosine'
                 syn_profile='mexican_hat',
                 autapse=True,
                 sigma_exc=sigma_exc, sigma_inh=sigma_inh, g_exc=g_exc, g_inh=g_inh) # Connectivity parameters for Mexican hat
ringAttractor.ring_pool.I_ext = I_ext_array

# +
# Setup monitors: spike monitor and state monitor for membrane potential and external input
spikemon = SpikeMonitor(ringAttractor.ring_pool)
statemon = StateMonitor(ringAttractor.ring_pool, 'V', record=True)
inputmon = StateMonitor(ringAttractor.ring_pool, 'I_ext', record=True)  # if you want to check the input

net = Network(ringAttractor.BrianObjects + [spikemon, statemon, inputmon])
print("List of network objects: ", net.objects)
# Run the simulation
duration = 10*second
net.run(duration/2)
ringAttractor.ring_pool.I_ext = I_ext_array*0
net.run(duration/2)


# +
# 1. Basic Raster Plot
raster_plot(spikemon)

# 2. Raster Plot with Stimulus Highlighted
raster_plot_with_stimulus(spikemon, duration)

# 3. Firing Rate Profile Plot (returns spike rates for further use)
spike_rates = firing_rate_profile(spikemon, positions, duration)

# 4. Polar Plot of the Population Vector Average (PVA)
polar_plot_PVA(spike_rates, positions)

# 5. Time-Resolved PVA Plot
time_resolved_PVA(spikemon, positions, duration, num_neurons, window_size=50*ms, step_size=10*ms)
plt.show()
