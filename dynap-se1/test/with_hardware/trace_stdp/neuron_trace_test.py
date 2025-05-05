import samna
import samna.dynapse1 as dyn1

import time
import numpy as np
import sys
# Note: change the path to where your lib files are
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
import dynapse1utils as ut
from netgen import Neuron, NeuronGroup, Synapses, add_synapses, NetworkGenerator
from params import set_params
from plotter import plot_raster, plot_trace
import matplotlib.pyplot as plt

"""
Expected figure: the green trace of neuron 0 (1,0,16) decreases at each yellow spike (from trigger neuron 1 (1,0,17)), and increases at each blue spike (from the trace neuron itself). The increase at the blue spikes may not obvious because it's the value that's first decayed, then increased.
"""

if __name__ == "__main__":
    # open DYNAP-SE1 board to get Dynapse1Model
    model, gui_process = ut.open_dynapse1()

    # get Dynapse1 api from the model
    api = model.get_dynapse1_api()

    # ------------------- build network -------------------
    net_gen = NetworkGenerator()

    schip=0
    score=0
    sids = [1, 2]
    spikegen_group = NeuronGroup(schip,score,sids,True)

    chip=1
    core=0
    nids = [16, 17]
    neuron_group = NeuronGroup(chip,core,nids)

    # connect spikegen_group to neuron_group
    syn = Synapses(spikegen_group, neuron_group, dyn1.Dynapse1SynType.AMPA, conn_type='one2one')
    add_synapses(net_gen, syn)

    # print the network so you can double check (optional)
    print(net_gen.network)

    # make a dynapse1config using the network
    new_config = net_gen.make_dynapse1_configuration()

    # apply the configuration
    model.apply_configuration(new_config)
    # ------------------- build network -------------------

    # set up Poisson spike generators
    spikegen_ids = [(schip,score,x) for x in sids]
    global_poisson_gen_ids = ut.get_global_id_list(spikegen_ids)
    poisson_gen = model.get_poisson_gen()
    poisson_gen.set_chip_id(chip)
    rate = 200
    for poigen_id in global_poisson_gen_ids:
        poisson_gen.write_poisson_rate_hz(poigen_id, rate)

    # check the configuration...
    neuron_ids = [(chip,core,x) for x in nids]
    config = model.get_configuration()
    for nid in neuron_ids:
        neuron = ut.get_neuron_from_config(config, nid[0], nid[1], nid[2])
        print("------------Neuron", nid,"------------")
        print("Cams:")
        ut.print_neuron_synapses(neuron, range(12))
        print("Srams:")
        ut.print_neuron_destinations(neuron)

    # set parameters
    set_params(model)

    # ---------------- create a graph ----------------
    """
    create a graph: source node to 2 filter nodes, one neuron select, one neuron trace.
    connect source node to filter nodes, connect filter nodes to sink nodes
    """
    graph = samna.graph.EventFilterGraph()

    # create sink nodes
    spike_sink_node = samna.BasicSinkNode_dynapse1_dynapse1_event()
    trace_sink_node = samna.BasicSinkNode_dynapse1_dynapse1_trace()

    _, spike_filter_node, _ = graph.sequential([model.get_source_node(), "Dynapse1NeuronSelect", spike_sink_node])
    _, trace_filter_node, _ = graph.sequential([model.get_source_node(), "Dynapse1NeuronTrace", trace_sink_node])

    # configure filter node: which neurons to filter?
    tau = int(40*1e3) # 50*1e3 in microsec
    spike_filter_node.set_neurons(neuron_ids)

    # set_neurons params: trace_map_neuron_ids, trigger_neuron_ids, tau_list
    trace_filter_node.set_neurons([neuron_ids[0]], [neuron_ids[1]], [tau])
    method = "increase_by" # increase_by increase_to
    delta = 3
    trace_filter_node.set_trace_parameters(method, delta)

    trace_filter_node.set_value_only_at_trigger(False)
    trace_filter_node.set_value_before_spike(False)
    # ---------------- create a graph ----------------

    # start the poisson gen
    poisson_gen.start()
    # start the graph
    graph.start()

    print(trace_filter_node.get_tau_list([neuron_ids[0]]), trace_filter_node.get_method())

    api.reset_timestamp()

    # clear the buffer
    spike_sink_node.get_events()
    trace_sink_node.get_events()

    # get spikes during 2 seconds
    time.sleep(2)
    spikes = spike_sink_node.get_events()
    timed_traces = trace_sink_node.get_events()

    for spike in spikes:
        ut.print_dynapse1_spike(spike)
    print('')
    for trace in timed_traces:
        print(trace.timestamp, trace.trace_map, end=',')
    print('')

    # optional, just to show how the spikes and traces can be stored to file
    # and loaded as samna objects from the file.
    spike_file = './spikes.json'
    trace_file = './traces.json'
    ut.save_samna_objects2file(spikes, spike_file)
    ut.save_samna_objects2file(timed_traces, trace_file)
    spikes = ut.load_samna_objects_file(spike_file)
    timed_traces = ut.load_samna_objects_file(trace_file)

    fig = plt.figure()
    plot_raster(spikes, neuron_ids)
    plot_trace(timed_traces, [neuron_ids[0]])
    plt.xlabel('Time (us)')
    plt.ylabel('Trace')
    plt.show()

    graph.stop()
    poisson_gen.stop()

    print("Example finished")

    # close Dynapse1
    ut.close_dynapse1(model, gui_process)
