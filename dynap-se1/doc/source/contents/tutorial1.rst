Tutorial 1: basic usage
=========================

Import required libraries
----------------------------------

Here, we import the related files as the following:

.. code-block::

    import samna.dynapse1 as dyn1
    from dynapse1constants import *
    import dynapse1utils as ut
    import netgen as n
    from netgen import Neuron


Open DYNAP-SE1 board to get Dynapse1Model
------------------------------------------------

You can open the board with or without the Graphical User Interfaces (GUI) using :func:`open_dynapse1 <dynapse1utils.open_dynapse1>`.

With the GUI: you should see blinking spikes of the firing silicon neurons.

.. code-block::

    model, gui_process = ut.open_dynapse1()

Without the GUI: if your PC cannot get the required visualization libraries, e.g. glx, installed.

.. code-block::

    model, gui_process = ut.open_dynapse1(gui=False)

``gui_process`` will be empty if ``gui=False``.


``model`` is :class:`Dynapse1Model <Dynapse1Model>`, with which you can configure DYNAP-SE1 
board, get the current configuration of the board, set the parameters, set up the stimulus, 
get the spikes out of DYNAP-SE1 and so on. 


Create a network
-----------------------
We need to use the :func:`NetworkGenerator <NetworkGenerator.NetworkGenerator>` to first 
create a network specifying the connections among neurons, then make a DYNAP-SE1 
configuration out of this network, and apply the configuration to the board.

To define the network, you need to use :func:`Neuron <NetworkGenerator.Neuron>` instead of 
:func:`Dynapse1Neuron <samna.dynapse1.Dynapse1Neuron>` as the basic unit, and add 
connections between them to the network. The former only holds the topology-related 
information of the network, the latter maintains the hardware-specific data structures 
required by the :func:`Dynapse1Configuration <samna.dynapse1.Dynapse1Configuration>`.

Apart from the basic unit :func:`Neuron <NetworkGenerator.Neuron>`, we provide some building
blocks, e.g. ``NeuronGroup``, ``Synapses``, ``WTA_connections`` that use groups of 
:func:`Neuron <NetworkGenerator.Neuron>` to construct the network. 

Define neuron groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create 2 neuron groups, one with spike generators and the other with neurons, using ``NeuronGroup``

.. code-block::

    chip1 = 0
    core1 = 0
    nids1 = [101,102,103]

    chip2 = 0
    core2 = 1
    nids2 = [14,15,16]

    # create spikegen group by selecting the spikegens you want to use
    pre_group = NeuronGroup(chip1,core1,nids1,is_spike_gen=True)
    # optional prints
    print('pre_group', pre_group.chip_id, pre_group.core_id, pre_group.neuron_ids,pre_group.neurons)

    # create neuron group by selecting the neurons you want to use
    post_group = NeuronGroup(chip2,core2,nids2)
    # optional prints
    print('post_group',post_group.chip_id, post_group.core_id, post_group.neuron_ids,post_group.neurons)

Define synapses between neuron groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Define connections between the 2 neuron groups using ``Synapses``. Connection pattern can be
defined using ``conn_type``, ``weight_matrix`` or ``pre_list`` and ``post_list``. 
``conn_type`` can be 'one2one' or 'all2all'. ``mux_conn`` can be used to duplicate the 
defined connectivity by multiplying the weights by ``mux_conn``.

* One-to-one connections: 

.. code-block::

    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.AMPA, conn_type='one2one')

* All-to-all random connections with a possibility of 0.7. When 'all2all' is used, ``p`` can be used to specify the possibility of all2all random connections and ``rand_seed`` can be defined.

.. code-block::

    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.NMDA, conn_type='all2all', p=0.7, rand_seed=60)

* Connection pattern defined by weight matrix:

.. code-block::

    int_w = np.array([
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 2],
    ])
    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.AMPA, weight_matrix=int_w)

* Self-defined pre-post pairs:

.. code-block::

    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.AMPA, pre_list=[1,0,2], post_list=[0,2,1])
    
Add synapses into the network generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We need to add synapses (which contain also the related neuron groups' information) into the
network generator to create a network, then convert the network into a DYNAP-SE1 
configuration and apply it to the hardware.

.. code-block::

    # initialize a network generator
    net_gen = n.NetworkGenerator()

    # add synapses into the netgen
    add_synapses(net_gen, syn)

    # print the network so you can double-check (optional)
    print(net_gen.network)

    # make a dynapse1config using the network
    new_config = net_gen.make_dynapse1_configuration()

    # apply the configuration
    model.apply_configuration(new_config)


Create WTA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Define 2 neuron groups (note here: both of them are physical neurons instead of spike 
generators), specify the WTA connections between them using ``WTA_connections``, then add 
the WTA into the network generator.

.. code-block::

    exc_group = NeuronGroup(chip1, core1, nids1)
    inh_group = NeuronGroup(chip2, core2, nids2)

    wta = WTA_connections(exc_group, inh_group, syn_type_ei= dyn1.Dynapse1SynType.AMPA, 
    syn_type_ie=dyn1.Dynapse1SynType.GABA_B, syn_type_ee=dyn1.Dynapse1SynType.NMDA, ee_pres=
    [0,1,2], ee_posts=[0,1,2])

    add_wta_conns(net_gen, wta)


Define a network using individual neurons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also customize your network by selecting the spike generators and neurons you want 
to use, and building connections between individual neurons. An example is shown below.

.. code-block::

    # select the spikegens you want to use
    spikegen_ids = [(0,2,50)]
    spikegens = []
    for spikegen_id in spikegen_ids:
        spikegens.append(Neuron(spikegen_id[0],spikegen_id[1],spikegen_id[2],True))

    # select the neurons you want to use
    chip = 1
    neuron_ids = [(chip,0,20), (0,0,36), (0,2,60), (1,1,60), (2,1,107), (2,3,152)]
    neurons = []
    for nid in neuron_ids:
        neurons.append(Neuron(nid[0],nid[1],nid[2]))

    # connect spikeGen to neuron0
    w = 1
    for i in range(w):
        net_gen.add_connection(spikegens[0], neurons[0], dyn1.Dynapse1SynType.AMPA)

    # initialize a networkgenerator
    net_gen = n.NetworkGenerator()

    # connect neuron0 to other neurons
    net_gen.add_connection(neurons[0], neurons[1], dyn1.Dynapse1SynType.AMPA)
    net_gen.add_connection(neurons[0], neurons[2], dyn1.Dynapse1SynType.NMDA)
    net_gen.add_connection(neurons[0], neurons[3], dyn1.Dynapse1SynType.GABA_A)
    net_gen.add_connection(neurons[1], neurons[4], dyn1.Dynapse1SynType.GABA_B)
    net_gen.add_connection(neurons[2], neurons[5], dyn1.Dynapse1SynType.GABA_B)

    # print the network so you can double-check (optional)
    net_gen.print_network()

    # make a dynapse1config using the network
    new_config = net_gen.make_dynapse1_configuration()

    # apply the configuration
    model.apply_configuration(new_config)


Set up Dynapse1PoissonGen
--------------------------------
Below is an example of how to set up one single Poisson spike generator 
:class:`Dynapse1PoissonGen <Dynapse1PoissonGen>`. Here we use spike generator No.10 
on the FPGA to generate Poisson spikes at 200 Hz.

.. code-block::

    # poissongen_id, range = [0, 1024)
    poissongen_id = 10
    rate = 200

    # get poissongen from the model
    poisson_gen = model.get_poisson_gen()
    # set the target chip of the post neurons
    post_chip = 0
    poisson_gen.set_chip_id(post_chip)
    poisson_gen.write_poisson_rate_hz(poissongen_id, rate)

    # remember to start the poissongen
    poisson_gen.start()


Set up Dynapse1FpgaSpikeGen
------------------------------------
Below is an example of how to set up the FPGA spike generators 
:class:`Dynapse1FpgaSpikeGen <Dynapse1FpgaSpikeGen>` using :func:`set_fpga_spike_gen 
<dynapse1utils.set_fpga_spike_gen>`. Here, we use spike generator No.15 on the FPGA to 
generate 400 spikes in 2 seconds with a constant inter-spike interval.

.. code-block::
    
    # only use 1 spikegen No.15, [0,1024)
    spikegen_id = 15
    # 400 spikes in 2 second
    spike_times = np.linspace(0, 2, 400)
    # spikegen id list corresponding to spike_times
    indices = [spikegen_id]*len(spike_times)

    # the chip where the post neurons are
    post_chip = 0
    target_chips = [post_chip]*len(indices)
    isi_base = 900
    repeat_mode=False

    # get the fpga spike gen from Dynapse1Model
    fpga_spike_gen = model.get_fpga_spike_gen()

    # set up the fpga_spike_gen
    ut.set_fpga_spike_gen(fpga_spike_gen, spike_times, indices, target_chips, isi_base, 
    repeat_mode)

    # remember to start the spikegen
    fpga_spike_gen.start()

Set up parameters
-----------------------
Each parameter group :class:`Dynapse1ParameterGroup <samna.dynapse1.
Dynapse1ParameterGroup>` has 25 different parameters. A parameter 
:class:`Dynapse1Parameter <samna.dynapse1.Dynapse1Parameter>` has name, coarse value, and 
fine value. Below are recommended initial values of the parameters.

.. code-block:: 

    # param_name, coarse_value, fine_value

    #THR, gain factor of neuron
    Dynapse1Parameter("IF_THR_N", 5, 80)

    #refactory period
    Dynapse1Parameter("IF_RFR_N", 4, 128)

    #leakage
    Dynapse1Parameter("IF_TAU1_N", 4, 80)
    Dynapse1Parameter("IF_TAU2_N", 0, 0)
    
    #DC
    Dynapse1Parameter("IF_DC_P", 0 , 0)
    
    #Fast excitatory synapses, AMPA
    Dynapse1Parameter("NPDPIE_TAU_F_P", 4, 80)
    Dynapse1Parameter("NPDPIE_THR_F_P", 0, 0)
    Dynapse1Parameter("PS_WEIGHT_EXC_F_N", 0, 0)
    
    #Slow excitatory synapses, NMDA
    Dynapse1Parameter("NPDPIE_TAU_S_P", 4, 80)
    Dynapse1Parameter("NPDPIE_THR_S_P", 0, 0)
    Dynapse1Parameter("PS_WEIGHT_EXC_S_N", 0, 0)
    Dynapse1Parameter("IF_NMDA_N", 6, 148)
    
    #Fast inhibitory synapses, shunting, GABA_A
    Dynapse1Parameter("NPDPII_TAU_F_P", 4, 80)
    Dynapse1Parameter("NPDPII_THR_F_P", 0, 0)
    Dynapse1Parameter("PS_WEIGHT_INH_F_N", 0, 0)
    
    #Slow inhibitory synapses, GABA_B
    Dynapse1Parameter("NPDPII_TAU_S_P", 4, 80)
    Dynapse1Parameter("NPDPII_THR_S_P", 0, 0)
    Dynapse1Parameter("PS_WEIGHT_INH_S_N", 0, 0)            
    
    #adaptation                       
    Dynapse1Parameter("IF_AHTAU_N", 4, 80)
    Dynapse1Parameter("IF_AHTHR_N", 0, 0)
    Dynapse1Parameter("IF_AHW_P", 0, 0)            
    Dynapse1Parameter("IF_CASC_N", 0, 0)            

    #pulse width
    Dynapse1Parameter("PULSE_PWLK_P", 4, 106)
    
    #voltage readout
    Dynapse1Parameter("R2R_P", 3, 85)
    Dynapse1Parameter("IF_BUF_P", 3, 80)

Set parameters per core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You have 3 ways to set up the parameters.

1. Generate parameter groups and apply them using :func:`update_parameter_group() <Dynapse1Model.update_parameter_group>`. 
Below is an example of a configuration that silences the neurons of the 16 cores in 4 chips.

.. code-block:: 

    from params import gen_clean_param_group

    paramGroup = gen_clean_param_group()

    for chip in range(4):
        for core in range(4):
            model.update_parameter_group(paramGroup, chip, core)

2. Set the parameters saved in a JSON file. Below is an example. JSON is a standard 
formatting style. An example JSON parameter file is `here <https://gitlab.com/neuroinf/
ctxctl_contrib/-/blob/samna-dynapse1/example/example_parameter_files/FS_EXC_parameters.
json>`_.

.. code-block:: 

    # set parameters using a JSON file
    ut.set_parameters_in_json_file(model, './example_parameter_files/FS_EXC_parameters.json')

    # save parameters to a JSON file
    # get the current config
    config = model.get_configuration()
    # save params
    save_parameters2json_file(config, filename="./dynapse_parameters.json")

3. Set the parameters saved in a txt file. Below is an example. The txt format here is 
self-defined and more compact than JSON format. An example txt parameter file is `here <https://gitlab.com/
neuroinf/ctxctl_contrib/-/blob/samna-dynapse1/example/example_parameter_files/parameters.
txt>`_.

.. code-block:: 

    ut.set_parameters_in_txt_file(model, './example_parameter_files/parameters.txt')

    # save parameters to a txt file
    # get the current config
    config = model.get_configuration()
    # save params
    save_parameters2txt_file(config, filename="./dynapse_parameters.txt")

Change a single parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to change only 1 single parameter value, you can use the method :func:`update_single_parameter <Dynapse1Model.update_single_parameter>`.

.. code-block:: 

    param = dyn1.Dynapse1Parameter("IF_THR_N", 5, 90)
    chip = 0
    core = 0
    model.update_single_parameter(param, chip, core)


Get spikes out of DYNAP-SE1
--------------------------------------

In most cases, we would need to monitor spikes of some specific neurons in our network during the experiments. For this, we need
to create a graph using :func:`create_neuron_select_graph() <dynapse1utils. 
create_neuron_select_graph>` to stream the spikes out. In this graph, we connect the 
source node in Dynapse1Model to a filter node that filters the spikes of the selected 
neurons, then this filter node is connected to a sink node which receives the spikes and 
stores them in its buffer.

``monitored_neurons`` requires neuron IDs as a list of tuples (chip_id, core_id, neuron_id).


.. code-block:: 

    # create a graph
    monitored_neurons = [(0,1,14), (0,1,15)]
    graph, filter_node, sink_node = ut.create_neuron_select_graph(model, monitored_neurons)

    # start the graph
    graph.start()

    # (optional) change the monitored neuron IDs "on the fly" if needed.
    monitored_neurons = [(0,1,16)]
    filter_node.set_neurons(monitored_neurons)

    # clear the buffer
    sink_node.get_events()
    # collect the spikes during 2 second
    time.sleep(2)
    # get the spikes accumulated in the buffer
    events = sink_node.get_events()

    # process the events (optional)
    print(len(events),"events.")
    for evt in events:
        ut.print_dynapse1_spike(evt)
    print("")

    # stop the graph
    graph.stop()


Monitor the membrane potential of neurons using an oscilloscope
------------------------------------------------------------------

To monitor Imem of the silicon neurons using an oscilloscope, you first get the 
Dynapse1Model model, then get the Dynapse1Interface api, then :func:`monitor_neuron 
<Dynapse1Interface.monitor_neuron>` can be called using this api. In each core, one neuron 
can be monitored at a time.

.. code-block:: 

    api  =  model.get_dynapse1_api()
    api.monitor_neuron(chip_id, neuron_id_in_chip)

Note: you should use the neuron ID in the corresponding chip ranging [0, 1023), not the global neuron ID out of 4 chips.


Close DYNAP-SE1
--------------------------

You should use :func:`close_dynapse1 <dynapse1utils.close_dynapse1>` at the end of your script the close the device.

If you opened DYNAP-SE1 with the GUI, this function will block the running program of your 
script til you click the close button of the GUI window. If you close the GUI window when 
your script is still running, it will NOT affect the running program, however, you will not 
be able open the GUI again until the next time you open the device.

.. code-block:: 

    ut.close_dynapse1(model, gui_process)