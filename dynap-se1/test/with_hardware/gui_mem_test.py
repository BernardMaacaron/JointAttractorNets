import samna
import samna.dynapse1 as dyn1
import dynapse1utils as ut
import netgen as n
from netgen import Neuron
from dynapse1constants import *
import samnagui
import json
from multiprocessing import Process
import time
import random

from params import set_params

"""
Outdated testing code for samna 0.8.32.0
"""

def open_dynapse1_no_plot(device_name):
    """
    Attribute:
        device_name: string, name the DYNAP-SE1 board you want to open.
    """
    # ports = random.sample(range(10**4, 10**5), k=2)
    # has to be these 2 numbers if you want to run the GUI
    store, samna_info_dict = ut.open_device(device_name, 33336, 33335)
    visualizer_id = 3

    model = getattr(store, device_name)

    # add a node in filter gui_graph
    global gui_graph
    gui_graph = samna.graph.EventFilterGraph()
    # Add a converter node that translate the raw DVS events
    dynapse1_to_visualizer_converter_id = gui_graph.add_filter_node("Dynapse1EventToRawConverter")
    # Add a streamer node that streams visualization events to our graph
    streamer_id = gui_graph.add_filter_node("VizEventStreamer")

    # connect nodes in graph
    gui_graph.connect(dynapse1_to_visualizer_converter_id, streamer_id)

    # connect a node from outside a gui_graph to a node inside the gui_graph
    # We need to explicitly select the input channel
    model.get_source_node().add_destination(gui_graph.get_node_input(dynapse1_to_visualizer_converter_id))

    gui_graph.start()

    # create gui process
    gui_process = Process(target=samnagui.runVisualizer)
    gui_process.start()
    time.sleep(1)

    # open a connection to the GUI node
    samna.open_remote_node(visualizer_id, "visualizer")

    port = random.randint(10**4, 10**5)
    # port = 40000
    try:
        # The GUI node contains a ZMQ receiver endpoint by default, we can set the address it should listen on
        gui_receiving_port = "tcp://0.0.0.0:"+str(port)
        samna.visualizer.receiver.set_receiver_endpoint(gui_receiving_port) # local connection on port 40000
    except Exception as e:
        print("ERROR: "+str(e)+", please re-run open_dynapse1()!")

    # get streamer node
    streamer_node = gui_graph.get_node(streamer_id)
    # stream on the same endpoint as the receiver is listening to
    streamer_node.set_streamer_endpoint(gui_receiving_port)

    # Connect the receiver output to the visualizer plots input
    samna.visualizer.receiver.add_destination(samna.visualizer.splitter.get_input_channel())

    # Add plots to the GUI
    activity_plot_id = samna.visualizer.plots.add_activity_plot(64, 64, "DYNAP-SE1")
    samna.visualizer.splitter.add_destination("passthrough", samna.visualizer.plots.get_plot_input(activity_plot_id))

    # List currently displayed plots
    samna.visualizer.plots.report()

    samna_info_dict["gui_receiving_port"] = gui_receiving_port
    samna_info_dict["gui_node_id"] = visualizer_id

    print("Sender port:", samna_info_dict["sender_port"])
    print("Receiver port:", samna_info_dict["receiver_port"])
    print("Opened device name:", samna_info_dict["device_name"])
    print("SamnaNode ID:", samna_info_dict["samna_node_id"])
    print("PythonNode ID:", samna_info_dict["python_node_id"])
    print("GUI receiving port:", samna_info_dict["gui_receiving_port"])
    print("GUI node ID:", samna_info_dict["gui_node_id"])

    with open('samna_info.json', 'w') as json_file:
        json.dump(samna_info_dict, json_file, indent=4)

    return store, gui_process

# open DYNAP-SE1 board to get Dynapse1Model
device_name = "dynapse1"
store, gui_process = open_dynapse1_no_plot(device_name)
model = getattr(store, device_name)

# get Dynapse1 api from the model
api = model.get_dynapse1_api()

serial_number = ut.get_serial_number(store, device_name)
print(device_name, "serial number is", serial_number)

# monitor neuron using oscilloscope
print("Monitor neuron 123 in chip 1")
api.monitor_neuron(1, 123)

# ------------------- build network -------------------
chip = 1
neuron_ids = [(chip,0,20), (0,0,36), (0,2,60), (1,1,60), (2,1,107), (2,3,152)]

set_params(model, dc=True)

# start the poisson gen
# poisson_gen.start()

monitored_neurons = neuron_ids[:1]
graph, filter_node, sink_node = ut.create_neuron_select_graph(model, monitored_neurons)
graph.start()


t0 = time.time()
sink_node.get_events() # clear the buffer
while True:
    spikes = sink_node.get_events()
    if len(spikes):
        print("systime sec", int(time.time()-t0), len(spikes),"spikes. Last spike ts:",spikes[-1].timestamp)
    del spikes

    time.sleep(120) # 2 min

graph.stop()

# poisson_gen.stop()

# close Dynapse1
ut.close_dynapse1(store, device_name, gui_process)