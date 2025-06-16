# These neuron models are for use with the Brian simulator.

# LIF Neuron Model
# This is Federica's leaky integrate-and-fire neuron model.
# The membrane potential is governed by the equation:
LIF_eq = '''
dV/dt = (V_rest-V + I/g_leak)/tau : volt
I = I_exc + I_inh : amp

I_exc : amp
I_inh : amp
tau = 5*ms        : second (shared)

g_leak = 1*nS       : siemens (shared)
V_rest = -70*mV     : volt (shared)
'''

LIF_sim_eq = '''
dV/dt = (V_rest-V + I/g_leak)/tau : volt
I = I_exc + I_inh : amp

I_exc : amp
I_inh : amp
tau   : second (shared)

g_leak = 1*nS       : siemens (shared)
V_rest = -70*mV     : volt (shared)
'''


LIFN_eq = '''
dv/dt = (E-v)/tau_m + I)/C : volt
I :  amp
noise  = mu + sigma*sqrt(noise_dt)*xi_pop: amp

mu               : amp (shared)
sigma            : amp (shared)
noise_dt = 1*ms  : second (shared)
C = 250*pF       : farad (shared)
tau_m = 10*ms      : second (shared)
E = -70*mV       : volt (shared)
'''


LIF_sim_eq = '''
dV/dt = (V_rest-V + I_ext)/tau : volt

tau                 : second (shared)
V_rest = -70*mV     : volt (shared)
I_ext : volt
'''

# LIF_xi_eq = '''
# dV/dt = (V_rest - V + I_syn + I_ext)/tau + sigma_noise*xi*tau**(-0.5) : volt (unless refractory)
# I_syn : volt
# I_ext : volt
# '''
 
LIF_xi_vel_eq = '''
dV/dt = (V_rest - V + I_syn + I_ext + I_vel)/tau + sigma_noise*xi*tau**(-0.5) : volt (unless refractory)
I_syn : volt
I_ext : volt
I_vel : volt
theta = 2*pi*i/N : 1
'''    