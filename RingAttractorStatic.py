from brian2 import *
import sys
import matplotlib.pyplot as plt
import numpy as np
#import scipy as sp
#from scipy import stats

sys.path.append("Neuron and Synapse Models")
sys.path.append("Tools")
from neuronModels import *
from ring_attractor import RingAttractor, Gaussian_Input_Generator
from plottingTools import *

##### INITIALIZATION
#Parameters 
Vth = -48*mV #Threshold value for the neurons
V_reset = -80*mV #Reset Potential for the neurons
duration = 100*ms #Duration of the simulation

#Network Static Weights
wee = 735*10*mV
wei = 3*10*mV
wie = 30*10*mV
wii = 4000*10*mV

num_neurons = 120 #number of neurons in the ring attractor

#Input Parameters
mean_direction = 60
bump_amp = 800
sigma = 0.4
add_noise = False

########################################################################################

#Network Initialization

obj_network = RingAttractor(N=num_neurons,wee = wee, wei = wei, wie = wie, wii = wii)
network = obj_network.net

#Input Setup
gaussian_gen = Gaussian_Input_Generator(n=num_neurons, amp=bump_amp, mu=mean_direction, sigma=sigma, noise=add_noise)
input_gen = gaussian_gen.to_brian2_neuron_group()
input_weights = gaussian_gen.generate_cue()
spike_monitor_input = SpikeMonitor(input_gen, name="spike_input")

#Visualizing the input
gaussian_gen.plot_gaussians_polar()

#Creating the gaussians between input and network
connecting_input = Synapses(input_gen, obj_network.excitatory_neurons, model='W_input : volt', name="input_synapses", on_pre="V_post += W_input")
connecting_input.connect(j="i")
connecting_input.W_input[:] = input_weights.flatten() * volt
network.add(input_gen)
network.add(connecting_input)
network.add(spike_monitor_input)
        

#Running the Static Network
network.run(duration) 

#Visualizing what is happening in simulation (this can be skipped if plot_states is set equal to False)
plot_states = True
if plot_states:
    fig, ax = plt.subplots(5,1, figsize=(15,10))
    ax[0].plot(spike_monitor_input.t/ms, spike_monitor_input.i, '.r', ms=3)
    ax[0].set_xlim(0, duration/ms)
    ax[0].set_ylim(0, obj_network.N)
    ax[0].set_xlabel('Time (ms)')
    ax[0].set_ylabel('Neuron idx')
    ax[0].set_title("Input Pattern")

    ax[1].plot(obj_network.spike_monitors.t/ms, obj_network.spike_monitors.i, '.k', ms=3)
    ax[1].set_xlim(0, duration/ms)
    ax[1].set_ylim(0, obj_network.N)
    ax[1].set_xlabel('Time (ms)')
    ax[1].set_ylabel('Neuron idx')
    ax[1].set_title("Excitatory neurons spiking activity")

    for n in range(num_neurons):
        ax[2].plot(obj_network.state_monitors.t/ms, obj_network.state_monitors.V[n]/mV, label="%s" %n)
                
    ax[2].set_xlabel('Time (ms)')
    ax[2].set_ylabel('mV')
    ax[2].set_xlim([0, duration/ms])
    ax[2].set_ylim([-90, 800])
    ax[2].set_title('Excitatory Neuron Membrane Potentials')
    #ax[2].legend()

    ax[3].plot(obj_network.inhibitory_spike_monitors.t/ms, obj_network.inhibitory_spike_monitors.i, '.k', ms=3)
    ax[3].set_xlabel('Time (ms)')
    ax[3].set_ylabel('mV')
    ax[3].set_xlim([0, duration/ms])
    ax[3].set_title('Inhibitory Neuron spiking activity')

    ax[4].plot(obj_network.inhibitory_state_monitors.t/ms, obj_network.inhibitory_state_monitors.V[0]/mV)
    ax[4].set_xlabel('Time (ms)')
    ax[4].set_ylabel('mV')
    ax[4].set_xlim([0, duration/ms])
    ax[4].set_title('Inhibitory Neuron Membrane Potential')

    plt.tight_layout()
    plt.show()

#TODO : Here I need a way to visualize the output of the network (which is inferred from the spiking of the excitatory neurons)

_, ax = plt.subplots(2,1,figsize=(20,15))
#lim_time = 50 ms
FR_neurons = [np.sum(obj_network.spike_monitors.i ==  neuron_idx)/(1e-3*(duration/ms)) for neuron_idx in range(num_neurons)]
peak = np.argmax(FR_neurons) #this is in neurons (i want to get it into degrees)
print("Correct direction %d" %(peak*3))
ax[0].plot(np.linspace(0,360,num_neurons), FR_neurons, "-r")
ax[0].set_xlabel("Neuron Idx")
ax[0].set_ylabel("FR [Hz]")
ax[0].set_title("Output Gaussian")
ax[0].set_xlim([0,360])

#I can also compute an histogram actually
output_spikes_hist = ax[1].hist(obj_network.spike_monitors.i, bins=num_neurons, range=(0, num_neurons), density=True) #/ (duration/ms)
mean_outputspikes = np.mean(obj_network.spike_monitors.i)
std_outputspikes = np.std(obj_network.spike_monitors.i)
x = np.arange(0,num_neurons)
fitted_gaussian = (1/(std_outputspikes * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean_outputspikes) / std_outputspikes)**2)
ax[1].plot(np.arange(0,num_neurons), fitted_gaussian, label='Fitted Gaussian')
ax[1].set_title("Histogram and Fitted Gaussian")
ax[1].set_xlabel("Neuron Idx")
ax[1].set_ylabel("Density")
ax[1].set_xlim([0,num_neurons])
ax[1].set_xticks(np.linspace(0,num_neurons, 8), labels=["%.1f" %i for i in np.linspace(0,360,8)])
print("Fitted gaussian centered in %d, with a std equal to %.2f" %(np.argmax(fitted_gaussian)*3, std_outputspikes))

plt.show()

#Idea: to fit it with a gaussian and also extract the sigma (certainty of our observation)
