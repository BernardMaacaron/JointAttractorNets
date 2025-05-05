import samna
import samna.dynapse1 as dyn1

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


def gen_param_group_c1():
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

def gen_param_group_c2():
    """Generate a Dynapse1ParameterGroup of one core with some synapse
    weights turned on for examples.

    Returns:
        samna.dynapse1.Dynapse1ParameterGroup: Dynapse1ParameterGroup.
    """
    
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

        # neuron time constant = affects how quickly the neuron's membrane potential changes in response to inputs
        # shorter time constant --> neuron more sensitive to rapid changes, less responsive to sustained inputs
 
    param_group.param_map["IF_TAU2_N"].coarse_value = 7
    param_group.param_map["IF_TAU2_N"].fine_value = 255

    param_group.param_map["IF_DC_P"].coarse_value = 0 # was 4
    param_group.param_map["IF_DC_P"].fine_value = 0 # was 150
 
    param_group.param_map["NPDPIE_TAU_F_P"].coarse_value = 4
    param_group.param_map["NPDPIE_TAU_F_P"].fine_value = 80

    param_group.param_map["NPDPIE_THR_F_P"].coarse_value = 4
    param_group.param_map["NPDPIE_THR_F_P"].fine_value = 80

    param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 6 #6.80 per INP_E
    param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 70 # was 40
    
        # Fast excitatory (AMPA) synapse weights
        # sets the weight of the fast excitatory synapses
        # determines strength of synaptic input to the neuron
        # increasing it = increase strength of excitatory input, can increase network's overall activity and excitability

    param_group.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
    param_group.param_map["NPDPIE_TAU_S_P"].fine_value = 80

    param_group.param_map["NPDPIE_THR_S_P"].coarse_value = 4
    param_group.param_map["NPDPIE_THR_S_P"].fine_value = 80

    param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 6 # 6.80 per EE
    param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 40

    param_group.param_map["IF_NMDA_N"].coarse_value = 0
    param_group.param_map["IF_NMDA_N"].fine_value = 0

    param_group.param_map["NPDPII_TAU_F_P"].coarse_value = 2
    param_group.param_map["NPDPII_TAU_F_P"].fine_value = 60
        # Fast inhibitory (GABA_A) synapses time constant
        # Affects how quickly inhibitory currents decay.
        # increasing: inhibitory effect lasts longer - can lead to more prolonged inhibition, potentially suppressing network activity more effectively
        # decreasing: shorten time constant, inhibitory effects decay faster - can reduce duration of inhibition, potentially allowing network to recover more quickly from inhibitory events

    param_group.param_map["NPDPII_THR_F_P"].coarse_value = 5 # was 5 
    param_group.param_map["NPDPII_THR_F_P"].fine_value = 80 # was 80
    
        # Fast inhibitory (GABA_A) synapses threshold ((i.e. max I_syn value)
        # Sets threshold for fast inhibitory synapses, affecting max inhibitory synaptic current.

    param_group.param_map["PS_WEIGHT_INH_F_N"].coarse_value = 5 # was 6 # GABA A
    param_group.param_map["PS_WEIGHT_INH_F_N"].fine_value = 250 # was 50

    param_group.param_map["NPDPII_TAU_S_P"].coarse_value = 4 # gaba b synaptic time constant
    param_group.param_map["NPDPII_TAU_S_P"].fine_value = 80

    param_group.param_map["NPDPII_THR_S_P"].coarse_value = 4 # gaba b synaptic threshold 
    param_group.param_map["NPDPII_THR_S_P"].fine_value = 90

    param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 7 # gaba B synaptic weight # was 4
    param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = 255 # was 14

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

    return param_group"""

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

def gen_param_group_c3():
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

        # neuron time constant = affects how quickly the neuron's membrane potential changes in response to inputs
        # shorter time constant --> neuron more sensitive to rapid changes, less responsive to sustained inputs
 
    param_group.param_map["IF_TAU2_N"].coarse_value = 7
    param_group.param_map["IF_TAU2_N"].fine_value = 255

    param_group.param_map["IF_DC_P"].coarse_value = 0# was 4
    param_group.param_map["IF_DC_P"].fine_value = 0 # was 150
 
    param_group.param_map["NPDPIE_TAU_F_P"].coarse_value = 5
    param_group.param_map["NPDPIE_TAU_F_P"].fine_value = 80

    param_group.param_map["NPDPIE_THR_F_P"].coarse_value = 4
    param_group.param_map["NPDPIE_THR_F_P"].fine_value = 80

    param_group.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 6 #6.80 per INP_E
    param_group.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 20 # was 40 # was 70
    
        # Fast excitatory (AMPA) synapse weights
        # sets the weight of the fast excitatory synapses
        # determines strength of synaptic input to the neuron
        # increasing it = increase strength of excitatory input, can increase network's overall activity and excitability

    param_group.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
    param_group.param_map["NPDPIE_TAU_S_P"].fine_value = 80

    param_group.param_map["NPDPIE_THR_S_P"].coarse_value = 4
    param_group.param_map["NPDPIE_THR_S_P"].fine_value = 80

    param_group.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 6 # 6.80 per EE
    param_group.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 40

    param_group.param_map["IF_NMDA_N"].coarse_value = 6 # enable NMDA gating!
    param_group.param_map["IF_NMDA_N"].fine_value = 200

    param_group.param_map["NPDPII_TAU_F_P"].coarse_value = 2
    param_group.param_map["NPDPII_TAU_F_P"].fine_value = 60
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

    param_group.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 6 # gaba B synaptic weight  # making this stronger to use with Mirco's chip # before it was 2 coarse, 8 fine
    param_group.param_map["PS_WEIGHT_INH_S_N"].fine_value = 120 # was 8

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

def set_params(model, dc=False, param_group=None):
    """Set 16 DYNAP-SE1  cores with the same Dynapse1ParameterGroup for examples.

    Args:
        model (samna.dynapse1.Dynapse1Model): Dynapse1Model
        dc (bool, optional): Turn DC on if True. Defaults to False.
        param_group (samna.dynapse1.Dynapse1ParameterGroup, optional): 
            Dynapse1ParameterGroup can be specified. Defaults to None.
    """
    """if param_group is None:
        if dc:
            param_group = gen_dc_params()
        else:
            param_group = gen_param_group()"""
        
    #for chip in [0]:
        #for core in range(4):
    model.update_parameter_group(gen_param_group_c0(), 0, 0)
    model.update_parameter_group(gen_param_group_c1(), 0, 1)
    model.update_parameter_group(gen_param_group_c2(), 0, 2)
    model.update_parameter_group(gen_param_group_c3(), 0, 3)
        
def set_stdp_params(model):
    """Set 16 DYNAP-SE1 cores with the same Dynapse1ParameterGroup for STDP example.

    Args:
        model (samna.dynapse1.Dynapse1Model): Dynapse1Model
    """
    param_group = gen_stdp_params()

    for chip in range(4):
        for core in range(4):
            model.update_parameter_group(param_group, chip, core)
