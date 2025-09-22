
import os
os.environ['BRIAN2_LOG_LEVEL'] = 'ERROR'
from ringAttractorClassBoundaries import  BoundedRingAttractor
from brian2 import *  # Reuse same Brian2 symbolic names (V, mV, ms, etc.)
from ringAttractorClass import RingAttractor
import numpy as np
from warnings import warn

import sys
import warnings
warnings.filterwarnings('ignore')



# Add the Tools directory to the path
tools_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Tools')
sys.path.append(tools_path)

from plottingTools import *
from utils import *

class FaithfulBoundedRingAttractor(BoundedRingAttractor):
    def __init__(self,
                 neuron_eq, N=120,
                 Vth=-48*mV, V_reset=-80*mV, refractory_period=5*ms, # Neuron parameters,
                 w_sub = -0.15*mV,                 # Global Inhibitory neuron parameters
                 mujoco = False, limit_neuron=None,
                 **syn_params):
        super().__init__(neuron_eq, N=N,
                         Vth=Vth, V_reset=V_reset, refractory_period=refractory_period,
                         autapse=True, glob_inh=False,
                         mujoco=mujoco, limit_neuron=limit_neuron,
                         **syn_params)
        # Compute the subtractive term, respecting normalization if requested
        subtract_term = abs(w_sub)

        # Apply subtractive inhibition to all synaptic weights numerically
        # (This avoids needing symbol names inside the assignment expression.)
        self.ring_synapses.w = self.ring_synapses.w - subtract_term

        # Ensure autapse setting is respected after modification
        if not self.autapse:
            self.ring_synapses.w['i==j'] = 0 * mV

        # Nothing to add to BrianObjects (we didn't create new groups/synapses)
 