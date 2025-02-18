from NeuronModels import *
from brian2 import *

def neuron_distance(i ,j, N=120):
    # Use np.minimum which is vectorized over arrays.
    return np.minimum(np.abs(i - j), N - np.abs(i - j))

# NOTE: There is a numpy function np.deg2rad which converts degrees to radians.
def return_radians_angle(i, N=120):
    return 2*pi*i/N * radian

class RingAttractor():
    def __init__(self, N =120, Vth=-48 * mV, V_rest=-70 *mV, V_reset=-80 *mV, wee = 1000*mV, wei = 5*mV, wie = 500 *mV, wii = 4 *mV, sigma=0.4, mode_weights="gaussian"):
        #self.Vthr = Vth * mV
        #self.V_reset = V_reset * mV
        #self.V_rest = V_rest * mV
        self.N = N
        self.sigma = sigma

        self.inhibit_neuron = NeuronGroup(1, LIF_eq, threshold = "V > Vth", reset = "V = V_reset", method="euler", name="inhibitory_neurons")
        self.excitatory_neurons = NeuronGroup(self.N, LIF_eq, threshold = "V > Vth", reset = "V = V_reset", method="euler", name="excitatory_neurons")
        self.inhibit_neuron.V = V_rest
        self.excitatory_neurons.V = V_rest

        rows, cols = np.indices((self.N, self.N))
        distance_matrix = neuron_distance(rows, cols, self.N)

        if mode_weights == "gaussian":
            self.weights_matrix = wee * np.exp(-np.power(distance_matrix,2)/(2*self.sigma**2))
        elif mode_weights == "cosine":
            self.weights_matrix = "wee * cos(return_radians_angle(i) - return_radians_angle(j))"
 
        self.Ring2Inh = Synapses(self.excitatory_neurons, self.inhibit_neuron, "W_ring2inh : volt", name="ring2inh_synapses", on_pre="V_post += W_ring2inh")

        self.Inh2Ring = Synapses(self.inhibit_neuron, self.excitatory_neurons, model="W_inh2ring : volt", name="inh2ring_synapses", on_post="V_post -= W_inh2ring ") #in this case I want the inhibitory neuron (presynaptic) to inhibit the neuron only if the post synaptic (excitatory) is firing too much
 
        self.Inh2Inh = Synapses(self.inhibit_neuron, self.inhibit_neuron, model = "W_inh2inh : volt", name="inh2inh_synapses", on_post="V_post -= W_inh2inh")
        
        self.Ring2Ring = Synapses(self.excitatory_neurons, self.excitatory_neurons, model="W_ring2ring : volt", name="ring2rings_synapses", on_pre="V_post += W_ring2ring")

        self.Ring2Inh.connect()
        self.Inh2Ring.connect()
        self.Inh2Inh.connect()
        self.Ring2Ring.connect()
        self.Ring2Inh.W_ring2inh = wei
        self.Inh2Ring.W_inh2ring = wie
        self.Inh2Inh.W_inh2inh = wii
        self.Ring2Ring.W_ring2ring[:] = self.weights_matrix.flatten()
        #visualise_connectivity(self.Ring2Inh, self.Inh2Ring, self.Inh2Inh, self.Ring2Ring)

        #Plotting the connectivity between neurons
        visualise_connectivity(self.Ring2Inh)
        visualise_connectivity(self.Inh2Ring)
        visualise_connectivity(self.Inh2Inh)
        visualise_connectivity(self.Ring2Ring)
        

        self.net = Network(collect()) #level=1, [self.excitatory_neurons, self.inhibit_neuron, self.Ring2Inh, self.Ring2Ring, self.Inh2Inh, self.Inh2Ring])) #it`s not collecting anything
        self.net.add([self.excitatory_neurons, self.inhibit_neuron, self.Ring2Inh, self.Ring2Ring, self.Inh2Inh, self.Inh2Ring])

        
        self.state_monitors = StateMonitor(self.excitatory_neurons, "V", record=True, name="state_excitatory")
        self.spike_monitors = SpikeMonitor(self.excitatory_neurons, name="spike_excitatory")
        self.inhibitory_state_monitors = StateMonitor(self.inhibit_neuron, "V", record=True, name="state_inhibitory")
        self.inhibitory_spike_monitors = SpikeMonitor(self.inhibit_neuron, name="spike_inhibitory")
        monitors = [self.state_monitors, self.inhibitory_state_monitors, self.spike_monitors, self.inhibitory_spike_monitors]

        self.net.add(monitors)
        
