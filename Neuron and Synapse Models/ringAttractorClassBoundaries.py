from neuronModels import *
from brian2 import (implementation, check_units, mV, ms, pi, NeuronGroup, Synapses,
                    defaultclock, Network, SpikeMonitor, volt, arctan2, sin, cos)
import numpy as np  # ensure np is defined explicitly
import os
import sys
 
# Add the Tools directory to the path
tools_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Tools')
sys.path.append(tools_path)
 
from plottingTools import *
from utils import *
"""Helper and connectivity shaping functions with C++ standalone support.
 
These functions are defined at module scope (instead of inside __init__) so that
Brian2's code generation (cpp_standalone) can translate them. They are fully
parameterized (no access to self / closures) to ensure portability. The network
code therefore passes all required scalar parameters explicitly in the weight
equations.
"""
 
 
@implementation('cpp', """
inline double linear_interp(double x, double x0, double y0, double xf, double yf){
    return y0 + (yf - y0) * (x - x0) / (xf - x0);
}
""")
@check_units(x=1, x0=1, y0=1, xf=1, yf=1, result=1)
def linear_interp(x, x0, y0, xf, yf):
    return y0 + (yf - y0) * (x - x0) / (xf - x0)
 
 
# NOTE: The following functions are intentionally verbose (if/else logic) rather than
# using numpy.select to ease translation to C++ and avoid reliance on closures.
# All parameters are dimensionless scalars (angles in radians, already unitless in Brian2 expressions).
 
@implementation('cpp', """
inline double positive_velocity_connectivity(double theta_pre, double theta_post, double t_thresh, double theta_star, double joint_limit, double g_sine_over_mV){
    const double TWO_PI = 6.283185307179586;
    double a = 1.0;
    if(theta_pre < t_thresh){
        a = linear_interp(theta_pre, 0.0, 0.0, t_thresh, -1.0);
    } else if(theta_pre < theta_star - t_thresh){
        a = -1.0;
    } else if(theta_pre <= theta_star){
        a = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0);
    } else if(theta_pre <= theta_star + t_thresh){
        a = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0);
    } else if(theta_pre <= TWO_PI - t_thresh){
        a = 1.0;
    } else {
        a = linear_interp(theta_pre, TWO_PI - t_thresh, 1.0, TWO_PI, 0.0);
    }
    return g_sine_over_mV * a * sin(-theta_pre + theta_post);
}
""")
@check_units(theta_pre=1, theta_post=1, t_thresh=1, theta_star=1, joint_limit=1, g_sine_over_mV=1, result=1)
def positive_velocity_connectivity(theta_pre, theta_post, t_thresh, theta_star, joint_limit, g_sine_over_mV):
    """Vectorised numpy implementation (Brian2 numpy backend).
    Piecewise definition reproduced with np.select so that theta_pre, theta_post can be arrays.
    """
    theta_pre = np.asarray(theta_pre)
    theta_post = np.asarray(theta_post)
    cond1 = (theta_pre < t_thresh)
    cond2 = (theta_pre >= t_thresh) & (theta_pre < theta_star - t_thresh)
    cond3 = (theta_pre >= theta_star - t_thresh) & (theta_pre <= theta_star)
    cond4 = (theta_pre > theta_star) & (theta_pre <= theta_star + t_thresh)
    cond5 = (theta_pre > theta_star + t_thresh) & (theta_pre <= 2 * np.pi - t_thresh)
    cond6 = (theta_pre > 2 * np.pi - t_thresh)
 
    interp1 = linear_interp(theta_pre, 0.0, 0.0, t_thresh, -1.0)
    interp2 = -1.0
    interp3 = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0)
    interp4 = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0)
    interp5 = 1.0
    interp6 = linear_interp(theta_pre, 2 * np.pi - t_thresh, 1.0, 2 * np.pi, 0.0)
 
    a = np.select([cond1, cond2, cond3, cond4, cond5, cond6],
                  [interp1, interp2, interp3, interp4, interp5, interp6],
                  default=1.0)
    return g_sine_over_mV * a * np.sin(-theta_pre + theta_post)
 
 
@implementation('cpp', """
inline double negative_velocity_connectivity(double theta_pre, double theta_post, double t_thresh, double theta_star, double joint_limit, double g_sine_over_mV){
    const double TWO_PI = 6.283185307179586;
    double a = 1.0;
    if(theta_pre <= joint_limit - t_thresh){
        a = 1.0;
    } else if(theta_pre <= joint_limit){
        a = linear_interp(theta_pre, joint_limit - t_thresh, 1.0, joint_limit, 0.0);
    } else if(theta_pre <= joint_limit + t_thresh){
        a = linear_interp(theta_pre, joint_limit, 0.0, joint_limit + t_thresh, -1.0);
    } else if(theta_pre <= theta_star - t_thresh){
        a = -1.0;
    } else if(theta_pre <= theta_star){
        a = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0);
    } else if(theta_pre <= theta_star + t_thresh){
        a = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0);
    } else { // theta_pre <= 2*pi
        a = 1.0;
    }
    return g_sine_over_mV * a * sin(-theta_pre + theta_post);
}
""")
@check_units(theta_pre=1, theta_post=1, t_thresh=1, theta_star=1, joint_limit=1, g_sine_over_mV=1, result=1)
def negative_velocity_connectivity(theta_pre, theta_post, t_thresh, theta_star, joint_limit, g_sine_over_mV):
    """Vectorised numpy implementation (Brian2 numpy backend)."""
    theta_pre = np.asarray(theta_pre)
    theta_post = np.asarray(theta_post)
    cond1 = (theta_pre <= joint_limit - t_thresh)
    cond2 = (theta_pre > joint_limit - t_thresh) & (theta_pre <= joint_limit)
    cond3 = (theta_pre > joint_limit) & (theta_pre <= joint_limit + t_thresh)
    cond4 = (theta_pre > joint_limit + t_thresh) & (theta_pre <= theta_star - t_thresh)
    cond5 = (theta_pre > theta_star - t_thresh) & (theta_pre <= theta_star)
    cond6 = (theta_pre > theta_star) & (theta_pre <= theta_star + t_thresh)
    cond7 = (theta_pre > theta_star + t_thresh)
 
    interp1 = 1.0
    interp2 = linear_interp(theta_pre, joint_limit - t_thresh, 1.0, joint_limit, 0.0)
    interp3 = linear_interp(theta_pre, joint_limit, 0.0, joint_limit + t_thresh, -1.0)
    interp4 = -1.0
    interp5 = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0)
    interp6 = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0)
    interp7 = 1.0
 
    a = np.select([cond1, cond2, cond3, cond4, cond5, cond6, cond7],
                  [interp1, interp2, interp3, interp4, interp5, interp6, interp7],
                  default=1.0)
    return g_sine_over_mV * a * np.sin(-theta_pre + theta_post)
 
class BoundedRingAttractor():
    def __init__(self,
                 neuron_eq, N=120,
                 Vth=-48*mV, V_reset=-80*mV, refractory_period=5*ms, # Neuron parameters
                 syn_profile='mexican_hat',                          # Choose connectivity profile: 'mexican_hat', 'gaussian', or 'cosine'
                 autapse = False, normalized = False,
                 glob_inh = False, w_inh = -0.15*mV,                 # Global Inhibitory neuron parameters
                 mujoco = False, limit_neuron=None,
                 **syn_params):
        """
        Constructs a ring attractor network with boundary conditions.
       
        Parameters:
          neuron_eq: string or Equations defining the neuron dynamics.
          N: number of neurons on the ring.
          Vth: threshold voltage for spiking.
          V_reset: reset voltage after spiking.
          refractory_period: refractory period for the neurons.
          syn_profile: Connectivity profile; one of 'mexican_hat', 'gaussian', or 'cosine'.
          autapse: If True, self-connections are allowed; default is False.
          limit_neuron: the index (from 0 to N-1) of the boundary neuron (last neuron within limits), correspond to a joint_limit of limit_neuron*2*pi/N .
 
          **syn_params: Additional parameters for the chosen connectivity:
              For 'mexican_hat': sigma_exc (default 1.0), sigma_inh (default 3.0),
                                g_exc (default 0.1*mV), g_inh (default -0.15*mV).
              For 'gaussian':    sigma_gauss (default 1.0), g_gauss (default 0.1*mV). BOUNDARIES ONLY WORK FOR THIS PROFILE
              For 'cosine':      g_cosine (default 0.1*mV).
        """
       
        self.numNeurons = N
        self.syn_profile = syn_profile.lower()
        self.autapse = autapse
        self.normalized = normalized
        self.glob_inh = glob_inh
        self.w_inh = w_inh
        self.BrianObjects = []
        self.limit_neuron = limit_neuron
        if limit_neuron is not None:
            self.joint_limit = (self.limit_neuron) * (2 * pi) / N
            joint_limit=self.joint_limit
            self.theta_star=(self.joint_limit / 2 + pi)
        else:
            self.joint_limit = None
            self.theta_star=None
        self.N_inboundNeurons=self.limit_neuron+1
        self.N_outboundNeurons=self.numNeurons-self.N_inboundNeurons
       
 
 
        # Create neuron positions uniformly along the ring [0, 2*pi)
        self.positions = np.linspace(0, 2*pi, self.numNeurons, endpoint=False)
                                     
        if mujoco:
            reset_string = '''V = V_reset
            dummy_var = store_spike(i, t)'''
        else:
            reset_string = 'V = V_reset'
           
        self.ring_pool = NeuronGroup(self.numNeurons, neuron_eq, threshold = 'V > Vth', reset = reset_string, refractory=refractory_period,
                                    method="euler", name="ring_neurons", namespace={'Vth': Vth, 'V_reset': V_reset})
        self.ring_pool.V = V_reset
       
 
        # Synapse Definition
        #+-------------------------------------------------------------------+
        # Build the weight matrix based on the chosen connectivity profile.
        if self.syn_profile == 'mexican_hat':
            # Use default parameters if not provided:
            sigma_exc = syn_params.get('sigma_exc', 1.0)
            sigma_inh = syn_params.get('sigma_inh', 3.0)
            g_exc     = syn_params.get('g_exc', 0.1*mV)
            g_inh     = syn_params.get('g_inh', -0.15*mV)
            self.connectivity_eq = 'g_exc * exp(-(theta_pre - theta_post)**2/(2*sigma_exc**2))\
                                    + g_inh * exp(-(theta_pre - theta_post)**2/(2*sigma_inh**2))'
            self.connectivityAsym_eq = 'g_exc * exp(-(theta_pre - theta_post - (pi/2))**2/(2*sigma_exc**2))\
                                    + g_inh * exp(-(theta_pre - theta_post - (pi/2))**2/(2*sigma_inh**2))'
            # self.weights_matrix = g_exc * np.exp(-angular_distMat**2/(2*sigma_exc**2)) \
            #                       + g_inh * np.exp(-angular_distMat**2/(2*sigma_inh**2))      
                             
        elif self.syn_profile == 'gaussian':
            sigma_gauss = syn_params.get('sigma_gauss', 1.0)
            g_gauss     = syn_params.get('g_gauss', 0.1*mV)
            self.connectivity_eq = 'g_gauss * exp(-(theta_pre - theta_post)**2/(2*sigma_gauss**2))'
            # self.weights_matrix = g_gauss * np.exp(-angular_distMat**2/(2*sigma_gauss**2))
           
        elif self.syn_profile == 'cosine':
            g_cosine = syn_params.get('g_cosine', 0.1*mV)
            g_sine = syn_params.get('g_sine', 1.0*mV)
            self.connectivity_eq = 'g_cosine * cos(theta_pre - theta_post)'
            self.connectivityAsym_eq = 'g_sine * sin(theta_pre - theta_post)'
            # self.weights_matrix = g_cosine * np.cos(angular_distMat)
            # self.weights_matrix_asym = g_sine * np.sin(angular_distMat)
 
            if self.limit_neuron < N-1:
                # Compute threshold based on available neurons inbound/outbound.
                n_neurons_to_interpolate_linearly_inbound = (self.N_inboundNeurons - 2) // 4
                t_thresh_inbound = n_neurons_to_interpolate_linearly_inbound * (2 * np.pi / self.numNeurons)
                n_neurons_to_interpolate_linearly_outbound = (self.N_outboundNeurons - 2) // 4
                t_thresh_outbound = n_neurons_to_interpolate_linearly_outbound * (2 * np.pi / self.numNeurons)
                self.t_thresh = min(t_thresh_inbound, t_thresh_outbound)
                t_thresh = self.t_thresh
 
                # Precompute dimensionless gain
                g_sine_over_mV = (g_sine / mV)
 
                # Use parameterized functions (fully supported in cpp_standalone)
                self.connectivityAsym_eq = '0*mV'
                self.connectivityAsymPositive_eq = (
                    f'positive_velocity_connectivity(theta_pre, theta_post, {t_thresh}, {self.theta_star}, {joint_limit}, {g_sine_over_mV})*mV'
                )
                self.connectivityAsymNegative_eq = (
                    f'negative_velocity_connectivity(theta_pre, theta_post, {t_thresh}, {self.theta_star}, {joint_limit}, {g_sine_over_mV})*mV'
                )
           
        else:
            raise ValueError("Unsupported syn_profile. Choose 'mexican_hat', 'gaussian', or 'cosine'.")
       
        if self.normalized == True:
            num_neurons = self.numNeurons
            self.connectivity_eq = "(" + self.connectivity_eq + ") / num_neurons"
            self.connectivityAsym_eq = "(" + self.connectivityAsym_eq + ") / num_neurons"
            if hasattr(self, 'connectivityAsymPositive_eq'):
                self.connectivityAsymPositive_eq = "(" + self.connectivityAsymPositive_eq + ") / num_neurons"
            if hasattr(self, 'connectivityAsymNegative_eq'):
                self.connectivityAsymNegative_eq = "(" + self.connectivityAsymNegative_eq + ") / num_neurons"
            self.w_inh = self.w_inh / num_neurons
 
        # Create synapses: on a presynaptic spike, add weight to postsynaptic I_syn.
        self.ring_synapses = Synapses(self.ring_pool, self.ring_pool, model='w: volt',
                                on_pre='I_syn_post += w', name='ring_synapses')
        self.ring_synapses.connect()
        self.ring_synapses.w = self.connectivity_eq
 
        #syn_asymEq = syn_asymMujoco if mujoco else syn_asym
           
        self.ring_synapses_asym = Synapses(self.ring_pool, self.ring_pool,
                                   model='''vel_in : 1 (shared)
                                            vel_on : boolean (shared)
                                            w_asym : volt
                                            w_asym_positive : volt
                                            w_asym_negative : volt''',
                                   on_pre='I_vel_post += int(vel_on)*(vel_in * (w_asym+ w_asym_positive * int(vel_in > 0) - w_asym_negative * int(vel_in < 0)))')
        self.ring_synapses_asym.connect()
        self.ring_synapses_asym.w_asym = self.connectivityAsym_eq
        # If the class has member self.connectivityAsymPositive_eq, set w_asym_positive accordingly
        if hasattr(self, 'connectivityAsymPositive_eq'):
            self.ring_synapses_asym.w_asym_positive = self.connectivityAsymPositive_eq
        else:
            self.ring_synapses_asym.w_asym_positive = '0*mV'
        if hasattr(self, 'connectivityAsymNegative_eq'):
            self.ring_synapses_asym.w_asym_negative = self.connectivityAsymNegative_eq
        else:
            self.ring_synapses_asym.w_asym_negative = '0*mV'
 
        if not mujoco:
            self.ring_synapses_asym.vel_in = 0.0  # Default velocity input for asymmetrical synapses        
 
        # END Synapse Definition
        #+-------------------------------------------------------------------+
       
        # Remove self-connections if autapse is False.
        if not self.autapse:
            self.ring_synapses.w['i==j'] = 0*mV
            self.ring_synapses_asym.w_asym['i==j'] = 0*mV
       
        # Create a global inhibitory neuron if glob_inh is True.    
        if self.glob_inh:
            self.glob_inh_neuron = NeuronGroup(1, neuron_eq, threshold='V > Vth', reset='V = V_reset', refractory=refractory_period,
                                                method="euler", name="glob_inh_neuron", namespace={'Vth': Vth, 'V_reset': V_reset})
            self.glob_inh_neuron.V = V_reset
       
            # Synapses from the global inhibitory neuron to all neurons in the ring.
            self.glob_inh2pool = Synapses(self.glob_inh_neuron, self.ring_pool, model='w_inh : volt',
                                              on_pre='I_syn_post += w_inh', name='glob_inh2pool')
            self.glob_inh2pool.connect()
            self.glob_inh2pool.w_inh = self.w_inh
           
            # Synapses from the ring neurons to the global inhibitory neuron.
            self.pool2glob_inh = Synapses(self.ring_pool, self.glob_inh_neuron, model='w_exc : volt',
                                          on_pre='I_syn_post += w_exc', name='pool2glob_inh')
            self.pool2glob_inh.connect()
            self.pool2glob_inh.w_exc = -self.w_inh # casts the weight to all neurons in the ring
           
            self.BrianObjects.extend([self.glob_inh_neuron, self.glob_inh2pool, self.pool2glob_inh])
         
       
        self.BrianObjects.extend([self.ring_pool, self.ring_synapses, self.ring_synapses_asym])
       
 
    def evaluateStability(self, plot = True):
        WeightMatrix = np.reshape(np.array(self.ring_synapses.w_), (self.numNeurons, self.numNeurons))
        eigenvalues = np.linalg.eigvals(WeightMatrix)
        if plot:
            spectrumPlot(eigenvalues)
        return eigenvalues
 
    def runSimulation(self, device = None, dt=0.1*ms,
                      inputParams = None, inputType='Uniform',
                      velInput = 0.0, runTime=50*ms, plot=False):
       
       
        if device == 'cpp_standalone':
            device.reinit()
            device.activate()
            set_device(device, build_on_run=False)
 
        # Define simulation parameters
        defaultclock.dt = dt
       
        # Define Inputs
 
        I0 = inputParams.get('I0', 0) * mV
        targetPosition = inputParams.get('targetPosition', 0) # Consider this is in degrees
 
        # Calculate external input based on input type
        I_ext_array = np.zeros(self.numNeurons) * mV
        if inputType == 'Gaussian':
            # Original Gaussian input
            stimulus_center = np.deg2rad(targetPosition) % (2*np.pi)  # Convert degrees to radians
            stimulus_width = 0.5  # width in radians
           
            d = arctan2(sin(self.positions - stimulus_center), cos(self.positions - stimulus_center))
            I_ext_array += I0 * np.exp(-(d**2) / (2 * stimulus_width**2))
       
        elif inputType == 'Uniform':
            # Equal input to all neurons
            I_ext_array += np.ones(self.numNeurons) * I0
 
            target_index = self.__get_neuron_index(targetPosition, in_degrees=True)
            I_ext_array[target_index] += inputParams.get('I_target', 1.0)*mV
 
        self.ring_pool.I_ext = I_ext_array
 
        # # Define run_regularly calls
        # self.ring_pool.run_regularly('V = clip(V, V_reset, inf*volt)', dt=defaultclock.dt)
 
        # Define Monitors
        # By default include a spike monitor
        self.spikeMonitor = SpikeMonitor(self.ring_pool)
        localObjects = [self.spikeMonitor]
 
        # Generate Brian Network
        net = Network(self.BrianObjects + localObjects)
 
        # Run the simulation
       
        self.ring_pool.I_ext = I_ext_array
        self.ring_synapses_asym.vel_in = velInput  # Default velocity input for asymmetrical synapses
        self.ring_synapses_asym.vel_on = False
        net.run(500*ms) # Run for initial transient
       
        I_ext_array[target_index] -= inputParams.get('I_target', 1.0)*mV
        self.ring_pool.I_ext = I_ext_array
        self.ring_synapses_asym.vel_on = True
        net.run(runTime)
        simTime = runTime + 500*ms
       
        if device == 'cpp_standalone':
            device.build(directory = 'internalSim_build', compile=True, run=True, debug=False, clean=False)
       
        firingRates = computeInstRate(self.spikeMonitor, self.numNeurons, meanISI = True)
       
        pva_angle, pva_magnitude = computePVA(firingRates, runTime)
       
        if plot:
            raster_plot(self.spikeMonitor,duration=simTime, num_neurons=self.numNeurons, y_axisFull=True)
 
        return pva_angle, pva_magnitude
       
    def calibrateVelocityGain(self):
        pass
   
 
#---------------------------
# Utility Functions
#---------------------------
    def _get_neuron_index(self, target_position, in_degrees=True):
        """
        Find the neuron index closest to a given target position.
       
        Parameters:
        -----------
        target_position : float
            The target position on the ring.
        in_degrees : bool, optional
            If True, target_position is in degrees [0, 360].
            If False, target_position is in radians [0, 2π].
       
        Returns:
        --------
        index : int
            The index of the neuron closest to the target position.
        """
        # Convert degrees to radians if necessary
        if in_degrees:
            target_rad = np.deg2rad(target_position) % (2*np.pi)
        else:
            target_rad = target_position % (2*np.pi)
           
        # Calculate the circular distance to each neuron
        distances = np.abs(np.mod(self.positions - target_rad + np.pi, 2*np.pi) - np.pi)
       
        # Find the neuron with the minimum distance
        closest_index = np.argmin(distances)
       
        return closest_index