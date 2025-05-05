import numpy as np
import samna
import sys
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
from dynapse1constants import MAX_NUM_CAMS

def create_stdp_graph(model, spike_sink_debug=False):
    """Create a filtering graph to track the neuron traces required by
    STDP-like learning algorithms. Graph:
        source_node in model -> Dynapse1NeuronSelect filter_node
        -> Dynapse1NeuronTrace onpost and onpre trace filter_nodes
        -> onpost and onpre trace sink_nodes

    Returned nodes:
        - 'spike_filter': passes spikes of pre and post neurons.
        - 'onpre_trace_filter': tracks and generates traces that are updated 
        at pre neurons' spiking times, which triggers LTD.
        - 'onpost_trace_filter': tracks and generates traces that are updated 
        at post neurons' spiking times, which triggers LTP.
        - 'onpre_trace_sink': receives onpre trace events for LTD weight update.
        - 'onpost_trace_sink': receives onpost trace events for LTP weight update.

        If spike_sink_debug is True, the following nodes will also be created:
            - 'pre_spike_filter': passes pre neurons' spikes.
            - 'post_spike_filter': passes post neurons' spikes.
            - 'pre_spike_sink': receives pre neurons' spikes.
            - 'post_spike_sink': receives post neurons' spikes.

    Args:
        model (samna.dynapse1.Dynapse1Model): Dynapse1Model.
        spike_sink_debug (bool, optional): whether to add spike filtering nodes for 
            debugging. Defaults to False.

    Returns:
        graph (samna.graph.EventFilterGraph): samna filtering graph.
        nodes (dictionary{'str':samna_nodes}): See explanation above.
    """    
    graph = samna.graph.EventFilterGraph()

    # create sink nodes
    onpost_trace_sink = samna.BasicSinkNode_dynapse1_dynapse1_trace()
    onpre_trace_sink = samna.BasicSinkNode_dynapse1_dynapse1_trace()

    _, spike_filter_node, onpre_trace_node, _ = graph.sequential([model.get_source_node(), "Dynapse1NeuronSelect", "Dynapse1NeuronTrace", onpre_trace_sink])
    _, onpost_trace_node, _ = graph.sequential([spike_filter_node, "Dynapse1NeuronTrace", onpost_trace_sink])


    nodes = {
        'spike_filter': spike_filter_node,
        'onpre_trace_filter': onpre_trace_node,
        'onpost_trace_filter': onpost_trace_node,
        'onpre_trace_sink': onpre_trace_sink,
        'onpost_trace_sink': onpost_trace_sink
    }

    if spike_sink_debug:
        """
        Dynapse1NeuronSelect filter_node above
        -> Dynapse1NeuronSelect pre and post spike filter_nodes
        -> pre and post spike sink_nodes
        """
        # create sink nodes
        pre_spike_sink = samna.BasicSinkNode_dynapse1_dynapse1_event()
        post_spike_sink = samna.BasicSinkNode_dynapse1_dynapse1_event()

        _, pre_spike_filter, _ = graph.sequential([spike_filter_node, "Dynapse1NeuronSelect", pre_spike_sink])
        _, post_spike_filter, _ = graph.sequential([spike_filter_node, "Dynapse1NeuronSelect", post_spike_sink])

        spike_nodes = {
            'pre_spike_filter': pre_spike_filter,
            'post_spike_filter': post_spike_filter,
            'pre_spike_sink': pre_spike_sink,
            'post_spike_sink': post_spike_sink
        }
        nodes.update(spike_nodes)

    return graph, nodes

def bad_traces(onpre_traces, onpost_traces, max_num=10, max_time_interval=3*1e5):
    """Checks if the received traces are abnormal.
    To handle the abnormal traces after restart of STDP.
    Bad traces should be dropped, not processed anymore.
    Traces are bad if

        1) not synchronized: time difference between the traces is too large.
        2) too many traces received which will take too long to process.

    Args:
        onpre_traces (list[samna.dynapse1.Dynapse1Trace]): onpre traces
            which triggers LTD.
        onpost_traces (list[samna.dynapse1.Dynapse1Trace]): onpost traces
            which triggers LTP.
        max_num (int, optional): number of received traces at one get_events(). 
            Defaults to 10.
        max_time_interval (int, optional): time difference between the traces, 
            in microsecond. Defaults to 3*1e5.

    Returns:
        bool: True if the received traces are abnormal.
    """    
    if len(onpre_traces)>max_num or len(onpost_traces)>max_num:
        return True

    start_times = []
    end_times = []
    if len(onpre_traces):
        start_times.append(onpre_traces[0].timestamp)
        end_times.append(onpre_traces[-1].timestamp)
    if len(onpost_traces):
        start_times.append(onpost_traces[0].timestamp)
        end_times.append(onpost_traces[-1].timestamp)

    for start in start_times:
        for end in end_times:
            if (end-start)>max_time_interval:
                return True

    return False

def floatW2intW(float_w_plast, max_pre_count, rand_seed=None, unit=0.1):
    """An example to do weight discretization.
    Converts a float weight matrix learned by STDP into an int matrix
    that can be applied to DYNAP-SE1 board.
    Here, 0.1 -> 1 connection

    Args:
        float_w_plast (numpy.array): float weight matrix
        max_pre_count (int): the maximum number of incoming synapses of a neuron.
        rand_seed (int or None, optional): rand seed. Defaults to None.
        unit (float, optional): unit value that will become 1 connection. 
            Defaults to 0.1.

    Returns:
        _type_: _description_
    """    
    np.random.seed(rand_seed)
    int_w_plast = float_w_plast*(1/unit)
    int_w_plast = int_w_plast.astype(int)
    post_cam_counts = np.sum(int_w_plast, axis=0)

    for post in range(len(post_cam_counts)):
        if post_cam_counts[post] > max_pre_count:
            # number of cams that needs to be removed
            extra_cam_count = post_cam_counts[post]-max_pre_count

            pre_post_weights = int_w_plast[:,post]
            num_pres = len(pre_post_weights)

            # pruning of pre_post_weights: randomly remove extra_cam_count cams
            while(extra_cam_count>0):
                pre = np.random.randint(num_pres, size=1)
                if int_w_plast[pre,post] !=0:
                    int_w_plast[pre,post] -= 1
                    extra_cam_count -= 1

    np.random.seed(None)
    
    return int_w_plast