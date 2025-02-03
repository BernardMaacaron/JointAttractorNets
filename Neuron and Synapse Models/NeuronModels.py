# These neuron models are for use with the Brian simulator.

# LIF Neuron Model
# This is Federica's leaky integrate-and-fire neuron model.
# The membrane potential is governed by the equation:
LIF_eq = '''
dV/dt = (V_rest-V + I/g_leak)/tau_m : volt
I = I_exc + I_inh : amp

I_exc : amp
I_inh : amp
tau_m = 5*ms        : second (shared)

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