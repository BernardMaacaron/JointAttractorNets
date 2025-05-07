import sys
sys.path.append('.')
import samna
import numpy as np
import matplotlib.pyplot as plt
import samna.dynapse1 as dyn1
import dynapse1utils as ut
from netgen import Neuron, NetworkGenerator
from params_all_cores import *
import time
import importlib


# to be used when connecting to Dynap-se locally 
devices = samna.device.get_unopened_devices()
model   = samna.device.open_device(devices[int(0)])


def woker_run(params_tuple):

    def gen_clean_param_group():
        """Generate a Dynapse1ParameterGroup of one core which should 
        be able to silence the neurons.

        Returns:
            samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
        """
        param_group = dyn1.Dynapse1ParameterGroup()
        # THR
        # ok
        param_group.param_map["IF_THR_N"].coarse_value = 5
        param_group.param_map["IF_THR_N"].fine_value = 80

        # refactory period
        param_group.param_map["IF_RFR_N"].coarse_value = 4
        param_group.param_map["IF_RFR_N"].fine_value = 128

        # leakage
        param_group.param_map["IF_TAU1_N"].coarse_value = 4
        param_group.param_map["IF_TAU1_N"].fine_value = 80

        param_group.param_map["IF_TAU2_N"].coarse_value = 7
        param_group.param_map["IF_TAU2_N"].fine_value = 255

        param_group.param_map["IF_DC_P"].coarse_value = 0
        param_group.param_map["IF_DC_P"].fine_value = 0

        param_group.param_map["NPDPIE_TAU_F_P"].coarse_value = 4
        param_group.param_map["NPDPIE_TAU_F_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_F_P"].coarse_value = 0
        param_group.param_map["NPDPIE_THR_F_P"].fine_value = 0

        param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 0
        param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 0

        param_group.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
        param_group.param_map["NPDPIE_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_S_P"].coarse_value = 0
        param_group.param_map["NPDPIE_THR_S_P"].fine_value = 0

        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 0
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 0

        param_group.param_map["IF_NMDA_N"].coarse_value = 0
        param_group.param_map["IF_NMDA_N"].fine_value = 0

        param_group.param_map["NPDPII_TAU_F_P"].coarse_value = 4
        param_group.param_map["NPDPII_TAU_F_P"].fine_value = 80

        param_group.param_map["NPDPII_THR_F_P"].coarse_value = 0
        param_group.param_map["NPDPII_THR_F_P"].fine_value = 0

        param_group.param_map["PS_WEIGHT_INH_F_N"].coarse_value = 0
        param_group.param_map["PS_WEIGHT_INH_F_N"].fine_value = 0

        param_group.param_map["NPDPII_TAU_S_P"].coarse_value = 4 # gaba b synaptic time constant
        param_group.param_map["NPDPII_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPII_THR_S_P"].coarse_value = 0 # gaba b synaptic threshold
        param_group.param_map["NPDPII_THR_S_P"].fine_value = 0

        param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 0 # gaba b synaptic weight
        param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = 0

        param_group.param_map["IF_AHTAU_N"].coarse_value = 4
        param_group.param_map["IF_AHTAU_N"].fine_value = 80

        param_group.param_map["IF_AHTHR_N"].coarse_value = 0
        param_group.param_map["IF_AHTHR_N"].fine_value = 0

        param_group.param_map["IF_AHW_P"].coarse_value = 0
        param_group.param_map["IF_AHW_P"].fine_value = 0

        param_group.param_map["IF_CASC_N"].coarse_value = 0
        param_group.param_map["IF_CASC_N"].fine_value = 0

        param_group.param_map["PULSE_PWLK_P"].coarse_value = 4
        param_group.param_map["PULSE_PWLK_P"].fine_value = 106

        param_group.param_map["R2R_P"].coarse_value = 3
        param_group.param_map["R2R_P"].fine_value = 85

        param_group.param_map["IF_BUF_P"].coarse_value = 3
        param_group.param_map["IF_BUF_P"].fine_value = 80

        return param_group

    def gen_param_group_c0():
        """Generate a Dynapse1ParameterGroup of one core with some synapse
        weights turned on for examples.

        Returns:
            samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
        """
        param_group = dyn1.Dynapse1ParameterGroup()
        # THR
        # ok
        param_group.param_map["IF_THR_N"].coarse_value = 5
        param_group.param_map["IF_THR_N"].fine_value = 80

        # refactory period
        param_group.param_map["IF_RFR_N"].coarse_value = 4
        param_group.param_map["IF_RFR_N"].fine_value = 128

        # leakage
        param_group.param_map["IF_TAU1_N"].coarse_value = 2 # was 4
        param_group.param_map["IF_TAU1_N"].fine_value = 60 # was 120

            # Main neuron time constant (unless switched to TAU2)

            # neuron time constant = how quickly neuron's membrane potential changes in response to inputs
            # short time constant --> neuron more sensitive to rapid changes, less responsive to sustained inputs
    
        param_group.param_map["IF_TAU2_N"].coarse_value = 7
        param_group.param_map["IF_TAU2_N"].fine_value = 255

        param_group.param_map["IF_DC_P"].coarse_value = 0
        param_group.param_map["IF_DC_P"].fine_value = 0

        param_group.param_map["NPDPIE_TAU_F_P"].coarse_value = 5
        param_group.param_map["NPDPIE_TAU_F_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_F_P"].coarse_value = 4
        param_group.param_map["NPDPIE_THR_F_P"].fine_value = 80

        param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 6 #trying new values to test with Mirco's chip # was 6
        param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 40 # was 40
        
            # Fast excitatory (AMPA) synapse weights
            # sets weight of the fast excitatory synapses
            # determines strength of synaptic input to the neuron
            # increasing it = increase strength of excitatory input, can increase network's overall activity and excitability

        param_group.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
        param_group.param_map["NPDPIE_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_S_P"].coarse_value = 4
        param_group.param_map["NPDPIE_THR_S_P"].fine_value = 80

        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 6 # 6.80 per EE
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 30

        param_group.param_map["IF_NMDA_N"].coarse_value = 0
        param_group.param_map["IF_NMDA_N"].fine_value = 0

        param_group.param_map["NPDPII_TAU_F_P"].coarse_value = 3
        param_group.param_map["NPDPII_TAU_F_P"].fine_value = 80
            # Fast inhibitory (GABA_A) synapses time constant
            # Affects how quickly inhibitory currents decay.
            # increasing: inhibitory effect lasts longer - can lead to more prolonged inhibition, potentially suppressing network activity more effectively
            # decreasing: shorten time constant, inhibitory effects decay faster - can reduce duration of inhibition, potentially allowing network to recover more quickly from inhibitory events

        param_group.param_map["NPDPII_THR_F_P"].coarse_value = 5 # was 5
        param_group.param_map["NPDPII_THR_F_P"].fine_value = 80 # was 80
        
            # Fast inhibitory (GABA_A) synapses threshold ((i.e. max I_syn value)
            # Sets threshold for fast inhibitory synapses, affecting max inhibitory synaptic current.

        param_group.param_map["PS_WEIGHT_INH_F_N"].coarse_value = 6 # was 6
        param_group.param_map["PS_WEIGHT_INH_F_N"].fine_value = 50 # was 50

        param_group.param_map["NPDPII_TAU_S_P"].coarse_value = 3 # gaba b synaptic time constant - slow inhibitory
        param_group.param_map["NPDPII_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPII_THR_S_P"].coarse_value = 4 # gaba b synaptic threshold  # mirco modification # was 4
        param_group.param_map["NPDPII_THR_S_P"].fine_value = 80 # mirco modification  # was 80

        param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 7 # gaba B synaptic weight # making this stronger to use with Mirco's chip # before it was 7 coarse, 20 fine
        param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = 20

        param_group.param_map["IF_AHTAU_N"].coarse_value = 4
        param_group.param_map["IF_AHTAU_N"].fine_value = 80

        param_group.param_map["IF_AHTHR_N"].coarse_value = 0
        param_group.param_map["IF_AHTHR_N"].fine_value = 0

        param_group.param_map["IF_AHW_P"].coarse_value = 0
        param_group.param_map["IF_AHW_P"].fine_value = 0

        param_group.param_map["IF_CASC_N"].coarse_value = 0
        param_group.param_map["IF_CASC_N"].fine_value = 0

        param_group.param_map["PULSE_PWLK_P"].coarse_value = 4
        param_group.param_map["PULSE_PWLK_P"].fine_value = 106

        param_group.param_map["R2R_P"].coarse_value = 3
        param_group.param_map["R2R_P"].fine_value = 85

        param_group.param_map["IF_BUF_P"].coarse_value = 3
        param_group.param_map["IF_BUF_P"].fine_value = 80

        return param_group

    def gen_param_group_c1(params_tuple):
        """Generate parameter group for core 1 (global inhibitory population).
        
        Args:
            params_tuple: Tuple containing optimization parameters
                - params_tuple[0]: PS_WEIGHT_EXC_S_N coarse (NMDA weight)
                - params_tuple[1]: PS_WEIGHT_EXC_S_N fine (NMDA weight)
                - params_tuple[2]: NPDPIE_THR_S_P coarse (NMDA gain)
                - params_tuple[3]: NPDPIE_THR_S_P fine (NMDA gain)
        """
        param_group = dyn1.Dynapse1ParameterGroup()
        
        # Standard parameters
        param_group.param_map["IF_THR_N"].coarse_value = 5
        param_group.param_map["IF_THR_N"].fine_value = 80
        
        param_group.param_map["IF_RFR_N"].coarse_value = 4
        param_group.param_map["IF_RFR_N"].fine_value = 128
        
        param_group.param_map["IF_TAU1_N"].coarse_value = 2
        param_group.param_map["IF_TAU1_N"].fine_value = 60
        
        # Other parameters remain unchanged
        
        # Parameters to optimize from params_tuple
        # NMDA weight in core 1 (coarse and fine)
        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = int(params_tuple[0])
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = int(params_tuple[1])
        
        # NMDA gain in core 1 (coarse and fine)
        param_group.param_map["NPDPIE_THR_S_P"].coarse_value = int(params_tuple[2])
        param_group.param_map["NPDPIE_THR_S_P"].fine_value = int(params_tuple[3])
        
        return param_group

    def gen_param_group_c2():
        """Generate a Dynapse1ParameterGroup of one core with some synapse
        weights turned on for examples.

        Returns:
            samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
        """

        param_group = dyn1.Dynapse1ParameterGroup()
        # THR
        # ok
        param_group.param_map["IF_THR_N"].coarse_value = 5
        param_group.param_map["IF_THR_N"].fine_value = 80

        # refactory period
        param_group.param_map["IF_RFR_N"].coarse_value = 4
        param_group.param_map["IF_RFR_N"].fine_value = 128

        # leakage
        param_group.param_map["IF_TAU1_N"].coarse_value = 2 # was 4 
        param_group.param_map["IF_TAU1_N"].fine_value = 60 # was 120

            # Main neuron time constant (unless switched to TAU2)

            # neuron time constant = how quickly neuron's membrane potential changes in response to inputs
            # short time constant --> neuron more sensitive to rapid changes, less responsive to sustained inputs
    
        param_group.param_map["IF_TAU2_N"].coarse_value = 7
        param_group.param_map["IF_TAU2_N"].fine_value = 255

        param_group.param_map["IF_DC_P"].coarse_value = 0
        param_group.param_map["IF_DC_P"].fine_value = 0

        param_group.param_map["NPDPIE_TAU_F_P"].coarse_value = 5
        param_group.param_map["NPDPIE_TAU_F_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_F_P"].coarse_value = 4
        param_group.param_map["NPDPIE_THR_F_P"].fine_value = 80

        param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 6 #6.80 per INP_E
        param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 50 # was 60         # PS_WEIGHT_EXC_F_N: excitatory (AMPA) synapse weights
        
            # PS_WEIGHT_EXC_F_N: AMPA synapse weight. increasing = increase strength of exc input
            
        param_group.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
        param_group.param_map["NPDPIE_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPIE_THR_S_P"].coarse_value = 4
        param_group.param_map["NPDPIE_THR_S_P"].fine_value = 80

        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 6 # 6.80 per EE
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 30

        param_group.param_map["IF_NMDA_N"].coarse_value = 0
        param_group.param_map["IF_NMDA_N"].fine_value = 0

        param_group.param_map["NPDPII_TAU_F_P"].coarse_value = 3 
        param_group.param_map["NPDPII_TAU_F_P"].fine_value = 80
            # Fast inhibitory (GABA_A) synapses time constant
            # Affects how quickly inhibitory currents decay.
            # increasing: inhibitory effect lasts longer - can lead to more prolonged inhibition, potentially suppressing network activity more effectively
            # decreasing: shorten time constant, inhibitory effects decay faster - can reduce duration of inhibition, potentially allowing network to recover more quickly from inhibitory events

        param_group.param_map["NPDPII_THR_F_P"].coarse_value = 5 # was 5 
        param_group.param_map["NPDPII_THR_F_P"].fine_value = 80 # was 80
        
            # Fast inhibitory (GABA_A) synapses threshold ((i.e. max I_syn value)
            # Sets threshold for fast inhibitory synapses, affecting max inhibitory synaptic current.

        param_group.param_map["PS_WEIGHT_INH_F_N"].coarse_value = 6 # was 6
        param_group.param_map["PS_WEIGHT_INH_F_N"].fine_value = 50 # was 50

        param_group.param_map["NPDPII_TAU_S_P"].coarse_value = 3 # gaba b synaptic time constant
        param_group.param_map["NPDPII_TAU_S_P"].fine_value = 80

        param_group.param_map["NPDPII_THR_S_P"].coarse_value = 4 # gaba b synaptic threshold 
        param_group.param_map["NPDPII_THR_S_P"].fine_value = 80

        param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 7 # gaba B synaptic weight  # making this stronger to use with Mirco's chip # before it was 7 coarse, 20 fine
        param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = 20

        param_group.param_map["IF_AHTAU_N"].coarse_value = 4
        param_group.param_map["IF_AHTAU_N"].fine_value = 80

        param_group.param_map["IF_AHTHR_N"].coarse_value = 0
        param_group.param_map["IF_AHTHR_N"].fine_value = 0

        param_group.param_map["IF_AHW_P"].coarse_value = 0
        param_group.param_map["IF_AHW_P"].fine_value = 0

        param_group.param_map["IF_CASC_N"].coarse_value = 0
        param_group.param_map["IF_CASC_N"].fine_value = 0

        param_group.param_map["PULSE_PWLK_P"].coarse_value = 4
        param_group.param_map["PULSE_PWLK_P"].fine_value = 106

        param_group.param_map["R2R_P"].coarse_value = 3
        param_group.param_map["R2R_P"].fine_value = 85

        param_group.param_map["IF_BUF_P"].coarse_value = 3
        param_group.param_map["IF_BUF_P"].fine_value = 80

        return param_group

    def gen_param_group_c3(params_tuple):
        """Generate parameter group for core 3 (ring populations).
        
        Args:
            params_tuple: Tuple containing optimization parameters
                - params_tuple[4]: PS_WEIGHT_EXC_F_N coarse (AMPA weight)
                - params_tuple[5]: PS_WEIGHT_EXC_F_N fine (AMPA weight)
                - params_tuple[6]: PS_WEIGHT_EXC_S_N coarse (NMDA weight)
                - params_tuple[7]: PS_WEIGHT_EXC_S_N fine (NMDA weight)
                - params_tuple[8]: PS_WEIGHT_INH_S_N coarse (GABA B weight)
                - params_tuple[9]: PS_WEIGHT_INH_S_N fine (GABA B weight)
                - params_tuple[10]: NPDPIE_THR_F_P coarse (AMPA gain)
                - params_tuple[11]: NPDPIE_THR_F_P fine (AMPA gain)
                - params_tuple[12]: NPDPIE_THR_S_P coarse (NMDA gain)
                - params_tuple[13]: NPDPIE_THR_S_P fine (NMDA gain)
                - params_tuple[14]: NPDPII_THR_S_P coarse (GABA B gain)
                - params_tuple[15]: NPDPII_THR_S_P fine (GABA B gain)
        """
        param_group = dyn1.Dynapse1ParameterGroup()
        
        # Standard parameters
        param_group.param_map["IF_THR_N"].coarse_value = 5
        param_group.param_map["IF_THR_N"].fine_value = 80
        
        param_group.param_map["IF_RFR_N"].coarse_value = 4
        param_group.param_map["IF_RFR_N"].fine_value = 128
        
        param_group.param_map["IF_TAU1_N"].coarse_value = 2
        param_group.param_map["IF_TAU1_N"].fine_value = 60
        
        # Other parameters remain unchanged
        
        # Parameters to optimize from params_tuple
        # AMPA weight in core 3 (coarse and fine)
        param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = int(params_tuple[4])
        param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = int(params_tuple[5])
        
        # NMDA weight in core 3 (coarse and fine)
        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = int(params_tuple[6])
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = int(params_tuple[7])
        
        # GABA B weight in core 3 (coarse and fine)
        param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = int(params_tuple[8])
        param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = int(params_tuple[9])
        
        # AMPA gain in core 3 (coarse and fine)
        param_group.param_map["NPDPIE_THR_F_P"].coarse_value = int(params_tuple[10])
        param_group.param_map["NPDPIE_THR_F_P"].fine_value = int(params_tuple[11])
        
        # NMDA gain in core 3 (coarse and fine)
        param_group.param_map["NPDPIE_THR_S_P"].coarse_value = int(params_tuple[12])
        param_group.param_map["NPDPIE_THR_S_P"].fine_value = int(params_tuple[13])
        
        # GABA B gain in core 3 (coarse and fine)
        param_group.param_map["NPDPII_THR_S_P"].coarse_value = int(params_tuple[14])
        param_group.param_map["NPDPII_THR_S_P"].fine_value = int(params_tuple[15])
        
        return param_group

    def gen_dc_params():
        """Generate a Dynapse1ParameterGroup based on silent neurons, and turned
        DC current on.

        Returns:
            samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
        """
        param_group = gen_clean_param_group()

        param_group.param_map["IF_DC_P"].coarse_value = 0 # was 2 
        param_group.param_map["IF_DC_P"].fine_value = 0 # was 150

        return param_group

    def gen_stdp_params():
        """Generate a Dynapse1ParameterGroup for STDP example.

        Returns:
            samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
        """
        param_group = gen_param_group_c2()

        param_group.param_map["IF_TAU1_N"].coarse_value = 4
        param_group.param_map["IF_TAU1_N"].fine_value = 80

        param_group.param_map["IF_THR_N"].coarse_value = 4
        param_group.param_map["IF_THR_N"].fine_value = 80

        # NMDA, pre to post neurons
        param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 7
        param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 80

        # AMPA, spikegen to neurons
        param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 6
        param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 80

        return param_group

    def set_params(model, params_tuple, dc=False, param_group=None):
        """Set DYNAP-SE1 cores with parameter groups.
        
        Args:
            model: Dynapse1Model
            params_tuple: Tuple containing optimization parameters
            dc: Turn DC on if True
            param_group: Optional pre-defined parameter group
        """
        model.update_parameter_group(gen_param_group_c0(), 0, 0)
        model.update_parameter_group(gen_param_group_c1(params_tuple), 0, 1)
        model.update_parameter_group(gen_param_group_c2(), 0, 2)
        model.update_parameter_group(gen_param_group_c3(params_tuple), 0, 3)
            
    def set_stdp_params(model):
        """Set 16 DYNAP-SE1 cores with the same Dynapse1ParameterGroup for STDP example.

        Args:
            model (samna.dynapse1.Dynapse1Model): Dynapse1Model
        """
        param_group = gen_stdp_params()

        for chip in range(4):
            for core in range(4):
                model.update_parameter_group(param_group, chip, core)



    api = model.get_dynapse1_api()
    config1 = model.get_configuration()
    # param_group_c0 = config1.chips[0].cores[0].parameter_group 
    # param_group_c1 = config1.chips[0].cores[1].parameter_group 
    # param_group_c2 = config1.chips[0].cores[2].parameter_group 
    # param_group_c3 = config1.chips[0].cores[3].parameter_group 

    # LIF encoding

    # ----------------  stimulus: a Gaussian bump ----------------
    n_pts     = 1000                 # number of samples
    t_end     = 1.0                  # seconds  (→ dt = 1 ms)
    t         = np.linspace(0, t_end, n_pts, endpoint=False)
    x         = np.linspace(-4, 4, n_pts)
    sigma = 0.6  # Try smaller values: 1.0 (default), 0.5, 0.25, etc.
    gauss = (1/(sigma * np.sqrt(2*np.pi))) * np.exp(-0.5 * (x / sigma)**2)
    I_peak    = 30000000e-12              # 1000 pA

    I         = gauss/gauss.max() * I_peak   # injected current (A)

    # ----------------  LIF neuron parameters ----------------------
    tau_m     = 20e-3                # 20 ms membrane time constant
    R_m       = 100e6                # 100 MΩ  (=> C = tau/R)
    C_m       = tau_m / R_m
    v_rest    = -65e-3               # -65 mV
    v_reset   = -65e-3
    v_thresh  = -50e-3               # spike threshold
    t_ref     = 2e-3                 # 2 ms refractory period
    dt        = t_end / n_pts        # simulation time-step (s)

    # # ----------------  simulation loop ----------------------------
    # v        = v_rest
    # next_ok  = 0.0                   # time when refractory ends
    # v_trace  = np.empty(n_pts)
    # spikes   = []

    # for k in range(n_pts):
    #     if t[k] >= next_ok:          # not in refractory
    #         dv = (-(v - v_rest) + R_m * I[k]) / (R_m * C_m) * dt
    #         v += dv
    #         if v >= v_thresh:        # spike!
    #             spikes.append(t[k])
    #             v = v_reset
    #             next_ok = t[k] + t_ref
    #     v_trace[k] = v

    spikes = np.array(spikes)
    spike_times_all = spikes#*1e3
    spike_ids = np.full(len(spikes), 1)
    spikegen_ids = [(0, 1, n) for n in range(10)]


    config1 = model.get_configuration()
    param_group_c0 = config1.chips[0].cores[0].parameter_group 

    p_E_E   = 0.5
    p_mexican = 1
    p_I_I   = 0 #1
    p_E_I   = 0 #0.1
    p_I_E   = 1 #0.4

    # initiate network 
    net_gen = NetworkGenerator()
    net_gen.clear_network()

    # create spikegens, one per ring attractor neural pop 
    spikegen_ids = [(0, 0, n) for n in range(10)]

    spikegens = []
    for spikegen_id in spikegen_ids:
        spikegens.append(Neuron(spikegen_id[0], spikegen_id[1],spikegen_id[2], True))

    # create neuron populations in the ring
    chip = 0
    core = 3
    npop = 3
    NBINS = 10

    # Create neuron populations for each band in core 0
    ring_pops = [
        [Neuron(chip, core, j) for j in range(10 + (i * npop), 10 + ((i + 1) * npop))]
        for i in range(NBINS)
    ]


    # create inhibitory population that connects to all other pops
    core_inh = 1
    start_inh_neuron = 4
    npop_inh = 4
    pop_inhibitory = [Neuron(chip, core_inh, j) for j in range(start_inh_neuron, start_inh_neuron + npop_inh, 1)]

            
    for i in ring_pops[3]:
        net_gen.add_connection(spikegens[1], i, dyn1.Dynapse1SynType.AMPA)
        

    # self excitation in each neural population in the ring: (todo determine if this is needed) 
    for pop in ring_pops:
        for pre in pop:
            for post in pop:
                if pre is not post and np.random.rand() < p_E_E:
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.NMDA)
                    
    # MEXICAN HAT CONNECTIONS
    OFFSET_1 = (-1, 1)         

    for i, pop_i in enumerate(ring_pops):
        for pre in pop_i:
            for d in OFFSET_1:
                j = (i + d) % NBINS          # wrap around
                for post in ring_pops[j]:
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.NMDA)
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.NMDA)
                    #net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.AMPA)

    OFFSET_2 = (-2, 2)          # ±3 bins wide “hat”

        # todo excitatory connections to second neighbors


    for i, pop_i in enumerate(ring_pops):
        for pre in pop_i:
            for d in OFFSET_2:
                j = (i + d) % NBINS          # wrap around
                for post in ring_pops[j]:
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.NMDA)
                    #net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.AMPA)

    OFFSET_3 = (-3, 3)          # ±3 bins wide “hat”
        # todo excitatory connections to third neighbors


    for i, pop_i in enumerate(ring_pops):
        for pre in pop_i:
            for d in OFFSET_3:
                j = (i + d) % NBINS          # wrap around
                for post in ring_pops[j]:
                    
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.NMDA)

        # todo inhibitory connections to all of the other pops
    OFFSET_inh = (-6, -5, -4, 4, 5, 6)          # all of the pops that are not being excited


    for i, pop_i in enumerate(ring_pops):
        for pre in pop_i:
            for d in OFFSET_inh:
                j = (i + d) % NBINS          # wrap around
                for post in ring_pops[j]:
                    net_gen.add_connection(pre, post, dyn1.Dynapse1SynType.GABA_B)

    # INH → EXC  (global inhibition pop to all pops in the ring)
    for inh in pop_inhibitory:
        for pop in ring_pops:
            for exc in pop:
                net_gen.add_connection(inh, exc, dyn1.Dynapse1SynType.GABA_B)

    # EXC → INH  (drive the global inhibition pop from all pops in the ring)
    for pop in ring_pops:
        for exc in pop:
            for inh in pop_inhibitory:
                net_gen.add_connection(exc, inh, dyn1.Dynapse1SynType.NMDA)


    # make a dynapse1config using the network
    new_config = net_gen.make_dynapse1_configuration()

    # apply the configuration
    model.apply_configuration(new_config)

    # Set hardware parameters
    set_params(model, params_tuple)

    #for rate in [50]:
    D_stim = 3 # stimulus duration (s)
    D_post_stim = 3 # post stimulus duration (s)
    D = D_stim + D_post_stim

    fpga_spike_gen = model.get_fpga_spike_gen() # set FPGA 

    # get events of selected neurons
    monitored_neurons = [
        (n.chip_id, n.core_id, n.neuron_id)   
        for pop in ring_pops
        for n   in pop
    ]

    monitored_neurons.extend([
        (neuron.chip_id, neuron.core_id, neuron.neuron_id)
        for neuron in pop_inhibitory  
    ])

    graph, filter_node, sink_node = ut.create_neuron_select_graph(model, monitored_neurons)
    graph.start()

    # clear the buffer
    sink_node.get_events()

    # select the neurons to monitor

    filter_node.set_neurons(monitored_neurons)

    api.reset_timestamp()

    time.sleep(0)

    spike_times_s = spike_times_all  # spike_times_all is in seconds!!!

    ut.set_fpga_spike_gen(
        fpga_spike_gen,
        spike_times_all,
        spike_ids,
        target_chips=[0] * len(spike_ids),
        isi_base=900,
        repeat_mode=False)

    fpga_spike_gen.start()

    timesleep = 3
    time.sleep(timesleep)

    fpga_spike_gen.stop()

    graph.stop()
    events = sink_node.get_events()

    NN = 256 # neurons in 1 core
    spike_id = []
    spike_t  = []
    for evt in events:
        #spike_id.append(evt.core_id*NN + evt.neuron_id)
        spike_id.append(evt.neuron_id)
        spike_t.append(evt.timestamp*1e-6)
    spike_id = np.array(spike_id)
    spike_t  = np.array(spike_t)
    
    return spike_id, spike_t
