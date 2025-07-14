# These neuron models are for use with the Brian simulator.

# LIF Neuron Model
# The membrane potential is governed by the equation:

LIF_sim_eq = '''
dV/dt = (V_rest-V + I_ext)/tau : volt

tau                 : second (shared)
V_rest = -70*mV     : volt (shared)
I_ext : volt
'''

LIF_xi_eq = '''
dV/dt = (V_rest - V + I_syn + I_ext)/tau + sigma_noise*xi*tau**(-0.5) : volt (unless refractory)
I_syn : volt
I_ext : volt
'''
 
LIF_xi_vel_eq = '''
dV/dt = (V_rest - V + I_syn + I_ext + I_vel)/tau + sigma_noise*xi*tau**(-0.5) : volt (unless refractory)
I_syn : volt
I_ext : volt
I_vel : volt
theta = 2*pi*i/N : 1
'''

LIF_Mujoco = '''
dV/dt = (V_rest - V + I_syn + I_ext + I_vel)/tau + sigma_noise*xi*tau**(-0.5) : volt (unless refractory)

timeM = get_socket_sample(0) : 1 (shared)
timeStepM = get_socket_sample(1) : 1 (shared)
I0 = get_socket_sample(2)*mV : volt (shared)
stimCenter = get_socket_sample(3) : 1 (shared)

I_syn : volt
theta = 2*pi*i/N : 1

stimulus_width = 0.5 : 1
d = arctan2(sin(theta - stimCenter), cos(theta - stimCenter)) : 1
I_ext = I0*exp(-(d**2)/(2 * stimulus_width**2)) : volt
I_vel : volt
'''


# Synapse Model
syn_sym = 'w : volt'

syn_asym = '''
vel_in : 1 (shared)
w_asym : volt
'''

syn_asymMujoco = '''
vel_in = get_socket_sample(4): 1 (shared)
w_asym : volt
'''