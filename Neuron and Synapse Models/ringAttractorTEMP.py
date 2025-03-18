from neuronModels import *
from brian2 import *

class RingAttractor():
    def __init__(self, 
                 neuron_eq, 
                 N=120,
                 Vth=-48*mV, V_reset=-80*mV, refractory_period=5*ms,
                 # Choose connectivity profile: 'mexican_hat', 'gaussian', or 'cosine'
                 syn_profile='mexican_hat',
                 autapse=False,
                 **syn_params):
        """
        Constructs a ring attractor network.
        
        Parameters:
          neuron_eq: string or Equations defining the neuron dynamics.
          N: number of neurons on the ring.
          Vth: threshold voltage for spiking.
          V_reset: reset voltage after spiking.
          refractory_period: refractory period for the neurons.
          syn_profile: Connectivity profile; one of 'mexican_hat', 'gaussian', or 'cosine'.
          autapse: If True, self-connections are allowed; default is False.
          
          **syn_params: Additional parameters for the chosen connectivity:
              For 'mexican_hat': sigma_exc (default 1.0), sigma_inh (default 3.0),
                                g_exc (default 0.1*mV), g_inh (default -0.15*mV).
              For 'gaussian':    sigma_gauss (default 1.0), g_gauss (default 0.1*mV).
              For 'cosine':      g_cosine (default 0.1*mV).
        """
        
        self.N = N
        self.syn_profile = syn_profile.lower()
        self.autapse = autapse

        # Create neuron positions uniformly along the ring [0, 2*pi)
        self.positions = np.linspace(0, 2*pi, N, endpoint=False)
        self.ring_pool = NeuronGroup(self.N, neuron_eq, threshold = 'V > Vth', reset = "V = V_reset", refractory=refractory_period,
                                    method="euler", name="ring_neurons")
        self.ring_pool.V = V_reset
        

        rows, cols = np.indices((N, N))
        index_distMat = np.minimum(np.abs(rows - cols), N - np.abs(rows - cols))
        angular_distMat = index_distMat * 2 * pi / N
        
        
        # Synapse Definition
        #+-------------------------------------------------------------------+
        # Build the weight matrix based on the chosen connectivity profile.
        if self.syn_profile == 'mexican_hat':
            # Use default parameters if not provided:
            sigma_exc = syn_params.get('sigma_exc', 1.0)
            sigma_inh = syn_params.get('sigma_inh', 3.0)
            g_exc     = syn_params.get('g_exc', 0.1*mV)
            g_inh     = syn_params.get('g_inh', -0.15*mV)
            self.weights_matrix = g_exc * np.exp(-angular_distMat**2/(2*sigma_exc**2)) \
                                  + g_inh * np.exp(-angular_distMat**2/(2*sigma_inh**2))
                                  
        elif self.syn_profile == 'gaussian':
            sigma_gauss = syn_params.get('sigma_gauss', 1.0)
            g_gauss     = syn_params.get('g_gauss', 0.1*mV)
            self.weights_matrix = g_gauss * np.exp(-angular_distMat**2/(2*sigma_gauss**2))
            
        elif self.syn_profile == 'cosine':
            g_cosine = syn_params.get('g_cosine', 0.1*mV)
            self.weights_matrix = g_cosine * (np.cos(angular_distMat) + 1) / 2
        else:
            raise ValueError("Unsupported syn_profile. Choose 'mexican_hat', 'gaussian', or 'cosine'.")
        
        # Remove self-connections if autapse is False.
        if not self.autapse:
            np.fill_diagonal(self.weights_matrix, 0)

    
         # Create synapses: on a presynaptic spike, add weight to postsynaptic I_syn.
        self.synapses = Synapses(self.ring_pool, self.ring_pool, model='w : volt',
                                 on_pre='I_syn_post += w', name='ring_synapses')
        self.synapses.connect()  
        self.synapses.w = self.weights_matrix.flatten()
        
        # END Synapse Definition
        #+-------------------------------------------------------------------+
        self.BrianObjects = [self.ring_pool, self.synapses]

    
        # self.Ring2Inh = Synapses(self.excitatory_neurons, self.inhibit_neuron, "W_ring2inh : volt", name="ring2inh_synapses", on_pre="V_post += W_ring2inh", dt=dt)
        # self.Inh2Ring = Synapses(self.inhibit_neuron, self.excitatory_neurons, model="W_inh2ring : volt", name="inh2ring_synapses", on_pre="V_post -= W_inh2ring ", dt=dt) #in this case I want the inhibitory neuron (presynaptic) to inhibit the neuron only if the post synaptic (excitatory) is firing too much
        # self.Inh2Inh = Synapses(self.inhibit_neuron, self.inhibit_neuron, model = "W_inh2inh : volt", name="inh2inh_synapses", on_pre="V_post -= W_inh2inh", dt=dt)
        # self.Ring2Ring = Synapses(self.excitatory_neurons, self.excitatory_neurons, model="W_ring2ring : volt", name="ring2rings_synapses", on_pre="V_post += W_ring2ring", dt=dt)

        # self.Ring2Inh.connect()
        # self.Inh2Ring.connect()
        # self.Inh2Inh.connect()
        # self.Ring2Ring.connect()
        # self.Ring2Inh.W_ring2inh = wei
        # self.Inh2Ring.W_inh2ring = wie
        # self.Inh2Inh.W_inh2inh = wii
        # self.Ring2Ring.W_ring2ring[:] = self.weights_matrix.flatten()
        

        # self.state_monitors = StateMonitor(self.excitatory_neurons, "V", record=True, name="state_excitatory")
        # self.spike_monitors = SpikeMonitor(self.excitatory_neurons, name="spike_excitatory")
        # self.inhibitory_state_monitors = StateMonitor(self.inhibit_neuron, "V", record=True, name="state_inhibitory")
        # self.inhibitory_spike_monitors = SpikeMonitor(self.inhibit_neuron, name="spike_inhibitory")
        # monitors = [self.state_monitors, self.inhibitory_state_monitors, self.spike_monitors, self.inhibitory_spike_monitors]

        # self.net.add(monitors)