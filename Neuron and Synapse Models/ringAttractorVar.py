from neuronModels import *
from brian2 import *

def neuron_distance(i ,j, N=120):
    # Use np.minimum which is vectorized over arrays.
    return np.minimum(np.abs(i - j), N - np.abs(i - j))

class RingAttractor():
    def __init__(self, N, neuron_eq, tauVal, Je_Val, Ji_Val, Jei_Val, Vth=-48 * mV, V_rest=-70 *mV, V_reset=-80 *mV):
        """
        Initialize the ring attractor network model.
        Parameters:
        N (int): Number of excitatory neurons in the network.
        neuron_eq (str): Differential equations defining the neuron model.
        Je (float): Synaptic weight for excitatory to excitatory connections.
        Ji (float): Synaptic weight for inhibitory to excitatory connections.
        Jei (float): Synaptic weight for excitatory to inhibitory connections.
        Vth (Quantity, optional): Threshold potential for spiking. Default is -48 mV.
        V_rest (Quantity, optional): Resting potential of the neurons. Default is -70 mV.
        V_reset (Quantity, optional): Reset potential after a spike. Default is -80 mV.
        
        Attributes:
        N (int): Number of excitatory neurons.
        Je (float): Synaptic weight for excitatory to excitatory connections.
        Ji (float): Synaptic weight for inhibitory to excitatory connections.
        Jei (float): Synaptic weight for excitatory to inhibitory connections.
        inhibit_neuron (NeuronGroup): Group containing the inhibitory neuron.
        excitatory_neurons (NeuronGroup): Group containing the excitatory neurons.
        theta_matrix (ndarray): Matrix of angular distances between neurons.
        weights_matrix (ndarray): Matrix of synaptic weights for excitatory to excitatory connections.
        Ring2Inh (Synapses): Synapses from excitatory neurons to inhibitory neuron.
        Inh2Ring (Synapses): Synapses from inhibitory neuron to excitatory neurons.
        Ring2Ring (Synapses): Synapses from excitatory neurons to other excitatory neurons.
        net (Network): The network containing all neuron groups and synapses.
        state_monitors (StateMonitor): Monitor for recording the membrane potential of excitatory neurons.
        spike_monitors (SpikeMonitor): Monitor for recording spikes of excitatory neurons.
        inhibitory_state_monitors (StateMonitor): Monitor for recording the membrane potential of the inhibitory neuron.
        inhibitory_spike_monitors (SpikeMonitor): Monitor for recording spikes of the inhibitory neuron.
        """
        
        
        self.N = N
        self.Je = Je_Val*mA
        
        self.Ji = Ji_Val*mA
        self.Jei = Jei_Val*mA

        self.inhibit_neuron = NeuronGroup(1, neuron_eq, threshold = "V > Vth", reset = "V = V_reset", method="euler", name="inhibitory_neurons")
        self.excitatory_neurons = NeuronGroup(self.N, neuron_eq, threshold = "V > Vth", reset = "V = V_reset", method="euler", name="excitatory_neurons")
        self.inhibit_neuron.V = V_rest
        self.excitatory_neurons.V = V_rest
        # self.inhibit_neuron.I_syn, self.inhibit_neuron.I_ext = 0 * amp, 0 * amp
        # self.excitatory_neurons.I_syn, self.excitatory_neurons.I_ext = 0 * amp, 0 * amp
        self.inhibit_neuron.tau = tauVal*ms
        self.excitatory_neurons.tau = tauVal*ms
        

        rows, cols = np.indices((self.N, self.N))
        distance_matrix = neuron_distance(rows, cols, self.N)
        delta_theta = 2*np.pi/self.N
        self.theta_matrix = delta_theta * distance_matrix
        


        # SYNAPSES DEFINITION
        #+-------------------------------------------------------------------------------------------------------------------+
        self.Ring2Inh = Synapses(self.excitatory_neurons, self.inhibit_neuron, "Jei : amp", name="ring2inh_synapses", on_pre="V_post += Jei*ohm")
        self.Inh2Ring = Synapses(self.inhibit_neuron, self.excitatory_neurons, model="Ji : amp", name="inh2ring_synapses", on_pre="V_post -= Ji*ohm")
        # self.Inh2Inh = Synapses(self.inhibit_neuron, self.inhibit_neuron, model = "W_inh2inh : volt", name="inh2inh_synapses", on_pre="V_post -= W_inh2inh")
        self.Ring2Ring = Synapses(self.excitatory_neurons, self.excitatory_neurons, model="W_ring2ring : amp", name="ring2rings_synapses", on_pre="V_post += W_ring2ring*ohm")

        self.Ring2Inh.connect()
        self.Inh2Ring.connect()
        # self.Inh2Inh.connect()
        self.Ring2Ring.connect()
        self.Ring2Inh.Jei = self.Jei
        self.Inh2Ring.Ji = self.Ji
        # self.Inh2Inh.W_inh2inh = wii
        self.weights_matrix = self.Je * cos(self.theta_matrix)
        # self.weights_matrix[self.weights_matrix < 0*amp] = 0*amp
        self.Ring2Ring.W_ring2ring[:] = self.weights_matrix.flatten()
        
        self.net = Network(collect())
        self.net.add([self.excitatory_neurons, self.inhibit_neuron, self.Ring2Inh, self.Ring2Ring, self.Inh2Ring]) # self.Inh2Inh])

        
        self.state_monitors = StateMonitor(self.excitatory_neurons, "V", record=True, name="state_excitatory")
        self.spike_monitors = SpikeMonitor(self.excitatory_neurons, name="spike_excitatory")
        self.inhibitory_state_monitors = StateMonitor(self.inhibit_neuron, "V", record=True, name="state_inhibitory")
        self.inhibitory_spike_monitors = SpikeMonitor(self.inhibit_neuron, name="spike_inhibitory")
        monitors = [self.state_monitors, self.inhibitory_state_monitors, self.spike_monitors, self.inhibitory_spike_monitors]

        self.net.add(monitors)