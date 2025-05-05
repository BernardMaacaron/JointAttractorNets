import time
import random
import samnagui
import samna
from multiprocessing import Process

"""
Outdated testing code for samna 0.8.32.0
"""

# initialize the main SamnaNode
# ports = random.sample(range(10**4, 10**5), k=2)
# sender_endpoint = "tcp://0.0.0.0:"+str(ports[0])
# receiver_endpoint = "tcp://0.0.0.0:"+str(ports[1])

sender_endpoint = "tcp://0.0.0.0:33336"
receiver_endpoint = "tcp://0.0.0.0:33335"
node_id = 1
interpreter_id = 2
device_name = "dynapse1"
visualizer_id = 3

samna_node = samna.SamnaNode(sender_endpoint, receiver_endpoint, node_id)

samna.setup_local_node(receiver_endpoint, sender_endpoint, interpreter_id)

samna.open_remote_node(node_id, "device_node")

# retrieve unopened device
devices = samna.device_node.DeviceController.get_unopened_devices()

if len(devices) == 0:
    raise Exception("no device detected!")

# let user select a device to open
for i in range(len(devices)):
    print("["+str(i)+"]: ", devices[i])

idx = input("Select the device you want to open by index: ")

# open the device
samna.device_node.DeviceController.open_device(devices[int(idx)], device_name)

model = getattr(samna.device_node, device_name)

# add a node in filter graph
graph = samna.graph.EventFilterGraph()
# Add a converter node that translate the raw DVS events
dynapse1_to_visualizer_converter_id = graph.add_filter_node("Dynapse1EventToRawConverter")
# Add a streamer node that streams visualization events to our graph
streamer_id = graph.add_filter_node("VizEventStreamer")

# connect nodes in graph
graph.connect(dynapse1_to_visualizer_converter_id, streamer_id)

# connect a node from outside a graph to a node inside the graph
# We need to explicitly select the input channel
model.get_source_node().add_destination(graph.get_node_input(dynapse1_to_visualizer_converter_id))

graph.start()

# create gui process
gui_process = Process(target=samnagui.runVisualizer)
gui_process.start()
time.sleep(1)

# open a connection to the GUI node
samna.open_remote_node(visualizer_id, "visualizer")

# The GUI node contains a ZMQ receiver endpoint by default, we can set the address it should listen on
samna.visualizer.receiver.set_receiver_endpoint("tcp://0.0.0.0:40000") # local connection on port 40000

# get streamer node
streamer_node = graph.get_node(streamer_id)
# stream on the same endpoint as the receiver is listening to
streamer_node.set_streamer_endpoint("tcp://0.0.0.0:40000")

# Connect the receiver output to the visualizer plots input
samna.visualizer.receiver.add_destination(samna.visualizer.splitter.get_input_channel())

# Add plots to the GUI
activity_plot_id = samna.visualizer.plots.add_activity_plot(64, 64, "DYNAP-SE1")
samna.visualizer.splitter.add_destination("passthrough", samna.visualizer.plots.get_plot_input(activity_plot_id))

# List currently displayed plots
samna.visualizer.plots.report()