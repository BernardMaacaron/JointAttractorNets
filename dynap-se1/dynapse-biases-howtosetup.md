# Setting up biases on Dynap-SE
## Guidelines for setting up the biases on the Dynap-SE.

*Overall goals*
1. Tune the biases of the neuron and synapse circuits to respond to their input in a biologically plausible way.
2. Find bias settings that do not make neurons fire spontaneously in absence of input.
3. Set the synaptic weight and threshold biases so that the neuron responds with a gain (output spikes / input spikes) of less than 1 (e.g., 0.10  or 0.3) when stimulating a single synapse.


## Procedure
Start by tuning the neuron's parameter, then the synapse's parameters and finally look at out how to configure the network and set the weights

### Preparation
1. Switch off all synapses so that they do not leak into the neurons:
   - Set `NPDPIE_TAU_F_P` = (255, 7), `NPDPIE_TAU_S_P` = (255, 7), `NPDPII_TAU_F_P` = (255, 7), `NPDPII_TAU_S_P` = (255, 7)
   - Set `NPDPIE_THR_F_P` = (0, 0), `NPDPIE_THR_S_P` = (0, 0), `NPDPII_THR_F_P` = (0, 0), `NPDPII_THR_S_P` = (0, 0)
2. Switch off the spike frequency adaptation:
   Set `IF_AHTAU_N` = (255, 7), `IF_AHW_P` = (0, 0), `IF_AHTHR_N` = (0, 0)
3. Switch off all neurons:
   Set `IF_DC_P` = (0, 0), `IF_TAU1_N` = (255, 7), `IF_TAU2_N` = (255, 7)

### Parameters Neuron

### 1.) Neuron time constant bias
a. `IF_TAUx_N`, x either 1 or 2
b. Biases 1 and 2 correspond to different registers. Each neuron can be assigned one of them.
c. Set the value to about 10 times the slow synapse TAU (NMDA-synapses) or 1/4 of the fast synapse TAU (AMPA-synapses). The time constant of the neuron should be around 40ms.
d. To find the neuron's time constant:
    i) Set the `IF_TAUx_N` of the tested core to a medium value.
    ii) Apply a subthreshold current to the neuron (e.g. `IF_DC_P` = (200, 3)) for about 0.5s. Make sure the neuron is not spiking!
    iii) Look at decay of Vmem in oscilloscope. The time constant is roughly 2/3 * of the time it takes for Vmem to decay.

### 2.) Neuron threshold bias
a. Set `IF_THR_N` to 2x or at most 3x the `IF_TAUx_N`  values found.

### 3.) Neuron refractory period bias
a. Inject a large DC current to make the neuron fire at a very high firing rate.
b. Set the refractory period bias so that the maximum firing rate is between 200Hz and 300HZ.

### Parameters Synapses

### 4.) Synapses time constant bias
a. `NPDPIx_TAU_y_P` where x is E (excitatory) or I (inhibitory) and y is F (fast) or S (slow)
b. TAU determines the strength of the leak. Small values correspond to a long synaptic time constant
c. For slow synapses small values are desirable (coarse value between 0 and 3). However if they are too slow, current will leak to the neurons, causing spontaneous firing
d. The time constant of the fast synapse should be around 10ms and the time constant of the slow synapse should be as large as possible, around 100ms.

Either:
e. Calculate the synapses time constant biases as described above in *Neuron time constant bias* and adjust the values for the synapses' smaller capacitors.

or:
e. To find the synapses's time constant:
   Set `IF_TAUx_N` of the tested core to a high value so that the neuron directly follows the synaptic input.
   Use the spike generator to apply input spikes through the synapses to the neuron.
   Look at decay of Vmem in oscilloscope. The neuron's Vmem directly follow the synapse now. Hence, the synapses time constant is roughly 2/3 * of the time it takes for Vmem to decay.

### 5.) Synapses threshold bias
a. Set `NPDPIx_THR_y_P` (synapses, x is I or E, y is F or S) to 2x or at most 3x the TAU values found.
b. THR corresponds to an input gain


It might be necessary to iterate over these steps several times. The goal is that there is no spontaneous firing of neurons anymore, while still keeping the TAUs low. 
If there are some neurons that continue firing spontaneously, they can be silenced by assigning them the second TAU bias instead of the first and setting this bias very high. Those neurons need to be selected manually.


### 6.) Weights and pulse width biases
  `PULSE_PWLK_P`, `PS_WEIGHT_xxx_y` (xxx is EXC or INH, y is F or S)
  - Monitor the spike response of single neurons for different synapse types
    - Start with slow excitatory synapses
    - Choose neurons that are not at the array boundaries
  - Send about 100Hz-1kHz input spikes
  - Balance weight and pulse width.
    - High weights and small pulse width: less mismatch (and vice versa)
    - Pulse width is global for all synapse types, so set is only once and then adapt biases for each synapse type
    - Weights for fast synapses will probably be about 10 times smaller than for slow ones
  - For inhibitory synapse also send input via an excitatory synapse and observe how the inhibitory input affects the neuron response


### 7.) Set up your nework
  - Observe activities, apply fine tuning where necessary


## Advanced stages

### 8.) Adaptation
  - Negative self-feedback to each neuron, for short-term depression
  - `IF_AHW_P`: feedback weight
  - `IF_AHTAU_N`, `IF_AHTHR_N`: correspond to  TAU and THR
  - `IF_CASC_N` sets an upper limit for effect of the negative feedback. If you want to use adaptation, make sure this is large enough (coarse value about 5 or higher)

### 9.) NMDA
  `IF_NMDA_N` 
  - Slow excitatory synapses only have an effect on the neuron potential if this potential is above some threshod value that is set with `IF_NMDA_N`. Therefore, if this bias is non-zero, some other form of input (fast synapses) is needed to bring the neuron potential above this threshold. 
  - This may be used to introduce “phase transitions” in the network. 
  - The exact relation between the bias and the resulting threshold value is not known. Bias needs to be set manually, while monitoring how the neuron responds to inputs.
  - Has not been studied in much detail, so far.

