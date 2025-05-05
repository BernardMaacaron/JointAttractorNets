import samna
import samna.dynapse1 as dyn1

import time
import _thread
import numpy as np

import sys
# Note: change the path to where your lib files are
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
import dynapse1utils as ut
from netgen import Neuron, NeuronGroup, Synapses, add_synapses, NetworkGenerator

from params import set_params

if __name__ == "__main__":
    # open DYNAP-SE1 board to get Dynapse1Model
    model, gui_process = ut.open_dynapse1(gui=False)

    # set parameters
    set_params(model, dc=True)

    # get Dynapse1 api from the model
    api = model.get_dynapse1_api()

    graph, filter_node, sink_node = ut.create_neuron_select_graph(model, [(0,0,2)])
    graph.start()
    while(True):
        t1 = time.time()
        evts = sink_node.get_events()
        t2 = time.time()
        print(t2-t1)