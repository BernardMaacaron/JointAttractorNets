import time

import samna
import samna.dynapse1 as dyn1

import sys
# Note: change the path to where your lib files are
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
import dynapse1utils as ut
from netgen import Neuron, NetworkGenerator

from params import set_params

# open DYNAP-SE1 board to get Dynapse1Model (with spiking GUI)
model, gui_process = ut.open_dynapse1()

# get Dynapse1 api from the model
api = model.get_dynapse1_api()

serial_number = ut.get_serial_number()
print("serial number is", serial_number)

# monitor neuron using oscilloscope
print("Monitor neuron 123 in chip 1")
api.monitor_neuron(1, 123)

# ------------------- build network -------------------
net_gen = NetworkGenerator()

spikegen_ids = [(0,2,50)]
spikegens = []
for spikegen_id in spikegen_ids:
    spikegens.append(Neuron(spikegen_id[0],spikegen_id[1],spikegen_id[2],True))

chip = 1
neuron_ids = [(chip,0,20), (0,0,36), (0,2,60), (1,1,60), (2,1,107), (2,3,152)]
neurons = []
for nid in neuron_ids:
    neurons.append(Neuron(nid[0],nid[1],nid[2]))

# connect spikeGen to neuron0
w = 1
for i in range(w):
    net_gen.add_connection(spikegens[0], neurons[0], dyn1.Dynapse1SynType.AMPA)

# connect neuron0 to other neurons
net_gen.add_connection(neurons[0], neurons[1], dyn1.Dynapse1SynType.AMPA)
net_gen.add_connection(neurons[0], neurons[2], dyn1.Dynapse1SynType.NMDA)
net_gen.add_connection(neurons[0], neurons[3], dyn1.Dynapse1SynType.GABA_A)
net_gen.add_connection(neurons[1], neurons[4], dyn1.Dynapse1SynType.GABA_B)
net_gen.add_connection(neurons[2], neurons[5], dyn1.Dynapse1SynType.GABA_B)

# print the network so you can double check (optional)
print(net_gen.network)

# make a dynapse1config using the network
new_config = net_gen.make_dynapse1_configuration()

# apply the configuration
model.apply_configuration(new_config)
# ------------------- build network -------------------

# set up Poisson spike generators
global_poisson_gen_ids = ut.get_global_id_list(spikegen_ids)
rate = 200
poisson_gen = model.get_poisson_gen()
poisson_gen.set_chip_id(chip)
poisson_gen.write_poisson_rate_hz(global_poisson_gen_ids[0], rate)

# check the configuration...
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

# start the poisson gen
poisson_gen.start()

# how to get events of selected neurons
monitored_neurons = neuron_ids[:1]
graph, filter_node, sink_node = ut.create_neuron_select_graph(model, monitored_neurons)
graph.start()

# select the neurons to monitor
monitored_neurons = neuron_ids[0:2]
print("monitored neurons:", monitored_neurons)
filter_node.set_neurons(monitored_neurons)

# clear the buffer
sink_node.get_events()

# get spikes every 2 seconds
for i in range(3):
    time.sleep(2)
    events = sink_node.get_events()

    # process the events
    print(len(events),"events.")
    # for evt in events:
    #     ut.print_dynapse1_spike(evt)
    # print("")

graph.stop()

poisson_gen.stop()

print("Example finished")

# close Dynapse1
ut.close_dynapse1(model, gui_process)
