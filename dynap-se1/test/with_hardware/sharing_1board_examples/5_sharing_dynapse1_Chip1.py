import samna.dynapse1 as dyn1
import dynapse1utils as ut
import netgen as n
from netgen import Neuron
from dynapse1constants import *
import time
import samna
import json

"""
Outdated testing code for samna 0.8.32.0
"""

# read the samna info from json file written by py_server.py
with open('./samna_info.json') as f:
    data = json.load(f)
print(data)
sender_port = data["sender_port"]
receiver_port = data["receiver_port"]
samna_node_id = data["samna_node_id"]
device_name = data["device_name"]
python_node_id = data["python_node_id"]

python_node_id += 1

# setup the python interpreter node
samna.setup_local_node(receiver_port, sender_port, python_node_id)
# open a connection to device_node, i.e. the store. Must open the device_node here
samna.open_remote_node(samna_node_id, "device_node")
store = samna.device_node
model = getattr(store, device_name)

# get Dynapse1 api from the model
api = model.get_dynapse1_api()

# ------------------- build network -------------------
net_gen = n.NetworkGenerator()

chip = 1
core = 2
spikegen_ids = [(0,core,66,True)]
spikegens = []
for spikegen_id in spikegen_ids:
    spikegens.append(Neuron(spikegen_id[0],spikegen_id[1],spikegen_id[2],spikegen_id[3]))
neuron_ids = [(chip,0,10), (chip,core,25), (chip,1,31), (chip,3,65), (chip,0,107), (chip,2,152)]
neurons = []
for nid in neuron_ids:
    neurons.append(Neuron(nid[0],nid[1],nid[2]))

net_gen.add_connection(spikegens[0], neurons[0], dyn1.Dynapse1SynType.AMPA)
net_gen.add_connection(neurons[0], neurons[1], dyn1.Dynapse1SynType.AMPA)
net_gen.add_connection(neurons[0], neurons[2], dyn1.Dynapse1SynType.NMDA)
net_gen.add_connection(neurons[0], neurons[3], dyn1.Dynapse1SynType.GABA_A)
net_gen.add_connection(neurons[1], neurons[4], dyn1.Dynapse1SynType.GABA_B)
net_gen.add_connection(neurons[2], neurons[5], dyn1.Dynapse1SynType.GABA_B)

# print the network so you can double check (optional)
net_gen.print_network()

# make a dynapse1config using the network
new_config = net_gen.make_dynapse1_configuration_in_chip(chip)

# apply the configuration
model.apply_configuration_by_chip(new_config, chip)
# ------------------- build network -------------------

# check the configuration...
config = model.get_configuration()
for nid in neuron_ids:
    neuron = ut.get_neuron_from_config(config, nid[0], nid[1], nid[2])
    print("------------Neuron", nid,"------------")
    print("Cams:")
    ut.print_neuron_synapses(neuron, range(12))
    print("Srams:")
    ut.print_neuron_destinations(neuron)

# set spike generators (0,1,66)
poisson_gen_id = ut.get_global_id(0,1,66)
rate = 200
poisson_gen = model.get_poisson_gen()
poisson_gen.set_chip_id(0)
poisson_gen.write_poisson_rate_hz(poisson_gen_id, rate) # neuron20 on chip 0 core 0

# set parameters
ut.set_parameters_in_txt_file(model, './parameters.txt')

# save parameters
ut.save_parameters2txt_file(model.get_configuration(), './current_parameters_sharing.txt')

# start the poisson gen
poisson_gen.start()


poisson_gen.stop()

while True:
    pass