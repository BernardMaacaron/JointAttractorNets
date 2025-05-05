Tutorial 2: train a network on chip using STDP
==================================================

Since DYNAP-SE1 doesn't have on-chip learning circuits, to train an SNN on chip
we use the learning modules of this library with a computer in the loop.
`stdp.py` and `stdp_utils.py` provide a learning framework for STDP-like algorithms. 
Implementation of triplet-STDP is given as an example, and alternative algorithms can be 
implemented by users. An example of training the plastic connections between a 
presynaptic and a postsynaptic neuron group is given in `example/test_stdp.py`.

`example/test_stdp.py` is a demo of STDP training with 10 samples. The samples have 
the same value. The learned weight matrix should be similar to

.. code-block::

    w = [[ 1  1  1]
        [ 0 10  0]
        [ 1  1  1]]

I.e., w[1][1] has the strongest weights because pre neuron1 and post neuron1 receive 
the strongest stimulation from the spike generators and thus fire the most.

A network consisting of a spike generator group of 3 spike generators, a pre and a post 
neuron group with 3 neurons, respectively is built on chip using the code below. The
spike generators are connected to both pre and post neuron groups with one-to-one 
connections. The pre neuron group is connected to the post one with the initial weight 
matrix ``int_w_plast``.

.. code-block::

    spikegen_group = NeuronGroup(schip,score,sids,True)

    pre_neuron_group = NeuronGroup(chip,core,pre_nids)
    post_neuron_group = NeuronGroup(chip,core,post_nids)

    # connect spikegen_group to pre and post neuron_group, connect pre to post
    connectivity = {
        'pre_gen2pre': Synapses(spikegen_group, pre_neuron_group, dyn1.Dynapse1SynType.
        NMDA, conn_type='one2one', mux_conn=mux_conn_spikegen),
        'post_gen2post': Synapses(spikegen_group, post_neuron_group, dyn1.Dynapse1SynType.
        NMDA, conn_type='one2one', mux_conn=mux_conn_spikegen),
        'pre2post': Synapses(pre_neuron_group, post_neuron_group, dyn1.Dynapse1SynType.
        AMPA, weight_matrix=int_w_plast)
    }

    for conn in connectivity:
        add_synapses(net_gen, connectivity[conn])
    
    new_config = net_gen.make_dynapse1_configuration()
    model.apply_configuration(new_config)

The STDP module is instantiated using ``Stdp`` class.

.. code-block::

    stdp = Stdp(model, net_gen, pre_neuron_ids, post_neuron_ids, w_plast, stdp_param_file, 
    algorithm=algorithm, new_thread=stdp_new_thread)

``stdp.start_stdp()`` starts the learning. Then 10 training samples (with the same input)
are fed to the SNN in a loop:

.. code-block::

    for sample in range(num_samples):
        # give new stimulation
        for i in range(len(global_poisson_gen_ids)):
            poisson_gen.write_poisson_rate_hz(global_poisson_gen_ids[i], rates[i])
        poisson_gen.start()

        # learn: w_plast being updated in another thread
        time.sleep(float(duration_per_sample/1e3))

        poisson_gen.stop()

        # remove the current pre-post connections
        remove_synapses(net_gen, connectivity['pre2post'])

        # add new pre-post connections using the latest w_plast
        current_w_plast = stdp.w_plast
        int_w_plast = floatW2intW(current_w_plast, max_pre_count)
        connectivity['pre2post'] = Synapses(pre_neuron_group, post_neuron_group, dyn1.Dynapse1SynType.AMPA, weight_matrix=int_w_plast)
        add_synapses(net_gen, connectivity['pre2post'])

        print(current_w_plast)
        print(int_w_plast)

        new_config = net_gen.make_dynapse1_configuration()
        model.apply_configuration(new_config)

        # cooling down
        time.sleep(float(duration_cool_down/1e3))

    stdp.stop_stdp()

After each training sample lasting for ``duration_per_sample``, the updated ``stdp.w_plast``
maintained by the STDP module is applied to the hardware. To change the connections inside 
the network generator, the old 'pre2post' connections are first removed using ``remove_synapses(net_gen, connectivity['pre2post'])``, then the new ``int_w_plast`` discretized using ``stdp.w_plast``
are added to the network generator using ``add_synapses(net_gen, connectivity['pre2post'])``.
Note that the ``remove_synapses`` and ``add_synapses`` are only operated inside the network
generator, not the hardware. The new DYNAP-SE1 configuration has to be generated using 
``net_gen.make_dynapse1_configuration()``, and applied to the hardware.

Since the rates of the spike generators are set to ``rates = [0, 200, 0]``, i.e. the middle 
neuron in each neural population receives the strongest stimulation, the synapse between this
pair of neurons grows to be the strongest one.