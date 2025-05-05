import time
import random
import os
import _thread
import numpy as np

import samna

from stdp_algorithms.triplet_stdp_details import TripletStdp
from stdp_utils import create_stdp_graph, bad_traces

class Stdp:
    """A class which implements STDP-like learning framework between
    a pre neuron population and a post neuron population with a 
    computer in the loop.

    Args:
        model (samna.dynapse1.Dynapse1Model): Dynapse1Model you use to configure DYNAP-SE1 board.
        net_gen (netgen.NetworkGenerator): NetworkGenerator you use to change the 
            network connections. 
        pre_neuron_ids (list[tuple(int,int,int)]): presynaptic neuron IDs (chip, core, neuron). 
        post_neuron_ids (list[tuple(int,int,int)]): postsynaptic neuron IDs (chip, core, neuron). 
        w_plast (numpy.array): initial weight matrix.
        param_file (str): json filename that store the STDP algorithm parameters.
        algorithm (str, optional): learning algorithm name. Defaults to 'triplet_stdp'. 
            'triplet_stdp' is implemented, and other STDP-like learning algorithms can be 
            implemented by users.
        new_thread (bool, optional): True if you want to start a new thread for STDP backend running.
            Because you may need another thread to change network connections. Defaults to True.
        remove_bad_traces (bool, optional): whether to drop abnormal traces during learning. 
            Defaults to False.
        stop_graph (bool, optional): whether to stop filtering graph when stop_stdp. 
            Defaults to False.
        spike_sink_debug (bool, optional): whether to add spike filters to debug trace filters. 
            Defaults to False. 
        max_num (int, optional): number of received traces at one get_events(). 
            Defaults to 10.
        max_time_interval (int, optional): time difference between the traces, 
            in microsecond. Defaults to 3*1e5.

    Attributes:
        model (samna.dynapse1.Dynapse1Model): Dynapse1Model you use to configure DYNAP-SE1 board.
        net_gen (netgen.NetworkGenerator): NetworkGenerator you use to change the 
            network connections. 
        pre_neuron_ids (list[tuple(int,int,int)]): presynaptic neuron IDs (chip, core, neuron). 
        post_neuron_ids (list[tuple(int,int,int)]): postsynaptic neuron IDs (chip, core, neuron). 
        w_plast (numpy.array): plastic weight matrix updated over time during learning.
        param_file (str): json filename that store the STDP algorithm parameters.
        algorithm (str): learning algorithm name. Defaults to 'triplet_stdp'. 'triplet_stdp'
            is implemented, and other STDP-like learning algorithms can be implemented by users.
        new_thread (bool): True if you want to start a new thread for STDP backend running.
            Because you may need another thread to change network connections. Defaults to True.
        remove_bad_traces (bool): whether to drop abnormal traces during learning. 
            Defaults to False.
        stop_graph (bool): whether to stop filtering graph when stop_stdp. 
            Defaults to False.
        spike_sink_debug (bool): whether to add spike filters to debug trace filters. 
            Defaults to False. 
        max_trace_num (int, optional): max_trace_num of bad traces. Defaults to 10.
        max_time_interval (int, optional): max_time_interval of bad traces. 
            Defaults to 3*1e5, in microsecond.
        graph (samna.graph.EventFilterGraph): samna filtering graph.
        nodes (dictionary{'str', samna_nodes}): if spike_sink_debug is False, nodes contains

            .. code-block::

                nodes = {
                    'spike_filter': spike_filter_node,
                    'onpre_trace_filter': onpre_trace_node,
                    'onpost_trace_filter': onpost_trace_node,
                    'onpre_trace_sink': onpre_trace_sink,
                    'onpost_trace_sink': onpost_trace_sink
                }
            Otherwise, nodes also has the following elements:
            
            .. code-block::
            
                spike_nodes = {
                    'pre_spike_filter': pre_spike_filter,
                    'post_spike_filter': post_spike_filter,
                    'pre_spike_sink': pre_spike_sink,
                    'post_spike_sink': post_spike_sink
                }
        trip (triplet_stdp_details.TripletStdp, optional): implementation of triplet STDP algorithm
            if algorithm is 'triplet_stdp', which creates a filtering graph to generate Dynapse1Trace
            events with recorded neuron traces and update weights using LTP and LTD.
        stdp_on (bool): whether STDP is running or not.
    
    """
    def __init__(self, model, net_gen, pre_neuron_ids, post_neuron_ids, w_plast, param_file, algorithm='triplet_stdp', new_thread = True, remove_bad_traces=False, stop_graph=False, spike_sink_debug=False, max_trace_num=10, max_time_interval=3*1e5):
        self.model = model
        self.net_gen = net_gen
        self.pre_neuron_ids = pre_neuron_ids
        self.post_neuron_ids = post_neuron_ids
        self.w_plast = w_plast
        self.algorithm = algorithm

        self.new_thread = new_thread
        self.stop_graph = stop_graph
        self.remove_bad_traces = remove_bad_traces
        if remove_bad_traces:
            self.max_trace_num = max_trace_num
            self.max_time_interval = max_time_interval
        self.spike_sink_debug = spike_sink_debug

        self.graph, self.nodes = create_stdp_graph(model, spike_sink_debug)

        # set trace graph for the required traces
        if self.algorithm == 'triplet_stdp':
            self.trip = TripletStdp(param_file)
            self.trip.set_triplet_stdp_graph(self.nodes['spike_filter'], self.nodes['onpre_trace_filter'], self.nodes['onpost_trace_filter'], self.pre_neuron_ids, self.post_neuron_ids)

            if self.spike_sink_debug:
                self.nodes['pre_spike_filter'].set_neurons(pre_neuron_ids)
                self.nodes['post_spike_filter'].set_neurons(post_neuron_ids)

        else:
            print("Wrong algorithm name. Learning setup failed.")

        self.stdp_on = False
    
    def start_stdp(self):
        """Start STDP learning algorithm so that weight update is turned on.
        """
        if not self.stdp_on:
            self.graph.start()
            
            self.stdp_on = True

            if self.new_thread:
                _thread.start_new_thread(self.__run_stdp, ())
            else:
                self.__run_stdp()

    def stop_stdp(self):
        """Stop STDP learning algorithm so that weight update is turned off.
        """
        # terminate the stdp thread while loop
        self.stdp_on = False

        if self.stop_graph:
            self.graph.stop()
    
    def _get_traces(self):
        """Get Dynapse1Trace events from the graph.

        Returns:
            onpre_traces (list[samna.dynapse1.Dynapse1Trace]): onpre traces
                which triggers LTD.
            onpost_traces (list[samna.dynapse1.Dynapse1Trace]): onpost traces
                which triggers LTP.
        """
        onpre_traces = self.nodes['onpre_trace_sink'].get_events()
        onpost_traces = self.nodes['onpost_trace_sink'].get_events()
        return onpre_traces, onpost_traces
    
    def get_spikes_debug(self):
        """Get Spike events from the graph if spike_sink_debug is True.

        Returns:
            pre_spikes (list[samna.dynapse1.Spike]): pre spikes. 
            post_spikes (list[samna.dynapse1.Spike]): post spikes.
            or None if spike_sink_debug is False.
        """
        if self.spike_sink_debug:
            pre_spikes = self.nodes['pre_spike_sink'].get_events()
            post_spikes = self.nodes['post_spike_sink'].get_events()
            return pre_spikes, post_spikes
        else:
            return False
        
    def __run_stdp(self):
        """Run STDP algorithm in a while loop to update weights
        regularly from the trace events received by sink nodes.
        """
        # empty the buffer
        onpre_traces, onpost_traces = self._get_traces()

        while(self.stdp_on):
            onpre_traces, onpost_traces = self._get_traces()

            # drop bad traces, do not touch w_plast using them
            if self.remove_bad_traces and bad_traces(onpre_traces, onpost_traces, self.max_trace_num, self.max_time_interval):
                continue
            
            if len(onpre_traces) or len(onpost_traces):
                # update w_plast using a specific learning algorithm
                if self.algorithm == 'triplet_stdp':
                    self.trip.triplet_stdp_algorithm(self.w_plast, onpre_traces, onpost_traces, self.pre_neuron_ids, self.post_neuron_ids)
                else:
                    print("Wrong algorithm name. Learning setup failed.")