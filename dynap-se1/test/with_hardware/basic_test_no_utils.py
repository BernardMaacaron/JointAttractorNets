import samna
import samna.dynapse1 as dyn1
import time
import datetime
import numpy as np
import samnagui
from multiprocessing import Process
import random

"""
Outdated testing code for samna 0.8.32.0
It can't be executed directly, copied to build/src, run there!
"""

def get_filtered_events(filteredSinkNode, selectedNeuronIds):
    t_start = datetime.datetime.now()
    events = filteredSinkNode.get_events()
    t_end = datetime.datetime.now()
    elapsed_time_ms = (t_end-t_start).microseconds / 1000
    # print("--------Filtered sink get_events takes ", elapsed_time_ms, "ms--------")
    print("--------Filtered eventVec size: ", len(events),"--------")

    if len(events) != 0:
        print_dynapse1_event(events[0])
        print_dynapse1_event(events[-1])

        filterWorks = True

        if selectedNeuronIds != None:
            for event in events:
                nid = event.neuron_id+event.core_id*256+event.chip_id*1024
                if nid not in selectedNeuronIds:
                    print("WRONG pass", nid)
                filterWorks = False

        if filterWorks:
            print("Neuron select filter Works!")

        return events

def get_full_events(full_readout_node):
    t_start = datetime.datetime.now()
    events = full_readout_node.get_events()
    t_end = datetime.datetime.now()
    elapsed_time_ms = (t_end-t_start).microseconds / 1000
    # print("Full sink get_events takes ", elapsed_time_ms, "ms")
    print("Full eventVec size: ", len(events))

    if len(events) != 0:
        print_dynapse1_event(events[0])
        print_dynapse1_event(events[-1])

    return events

def print_dynapse1_event(event):
    if isinstance(event, dyn1.Spike):
        print((event.timestamp, event.neuron_id+event.core_id*256+event.chip_id*1024))
    elif isinstance(event, dyn1.TimestampWrapEvent):
        print((event.timestamp))

def gen_param_group():
    paramGroup = dyn1.Dynapse1ParameterGroup()
    # THR
    # ok
    paramGroup.param_map["IF_THR_N"].coarse_value = 5
    paramGroup.param_map["IF_THR_N"].fine_value = 80

    # ok
    # paramGroup.param_map.get("IF_THR_N").coarse_value = 5
    # paramGroup.param_map.get("IF_THR_N").fine_value = 80

    # not work
    # paramGroup.param_map["IF_THR_N"] = dyn1.Dynapse1Parameter("IF_THR_N", 5, 80)

    # refactory period
    paramGroup.param_map["IF_RFR_N"].coarse_value = 4
    paramGroup.param_map["IF_RFR_N"].fine_value = 128

    # leakage
    paramGroup.param_map["IF_TAU1_N"].coarse_value = 4
    paramGroup.param_map["IF_TAU1_N"].fine_value = 80

    paramGroup.param_map["IF_TAU2_N"].coarse_value = 7
    paramGroup.param_map["IF_TAU2_N"].fine_value = 255

    paramGroup.param_map["IF_DC_P"].coarse_value = 0
    paramGroup.param_map["IF_DC_P"].fine_value = 0

    paramGroup.param_map["NPDPIE_TAU_F_P"].coarse_value = 4
    paramGroup.param_map["NPDPIE_TAU_F_P"].fine_value = 80

    paramGroup.param_map["NPDPIE_THR_F_P"].coarse_value = 4
    paramGroup.param_map["NPDPIE_THR_F_P"].fine_value = 80

    paramGroup.param_map["PS_WEIGHT_EXC_F_N"].coarse_value = 7
    paramGroup.param_map["PS_WEIGHT_EXC_F_N"].fine_value = 80

    paramGroup.param_map["NPDPIE_TAU_S_P"].coarse_value = 4
    paramGroup.param_map["NPDPIE_TAU_S_P"].fine_value = 80

    paramGroup.param_map["NPDPIE_THR_S_P"].coarse_value = 4
    paramGroup.param_map["NPDPIE_THR_S_P"].fine_value = 80

    paramGroup.param_map["PS_WEIGHT_EXC_S_N"].coarse_value = 7
    paramGroup.param_map["PS_WEIGHT_EXC_S_N"].fine_value = 80

    paramGroup.param_map["IF_NMDA_N"].coarse_value = 0
    paramGroup.param_map["IF_NMDA_N"].fine_value = 0

    paramGroup.param_map["NPDPII_TAU_F_P"].coarse_value = 4
    paramGroup.param_map["NPDPII_TAU_F_P"].fine_value = 80

    paramGroup.param_map["NPDPII_THR_F_P"].coarse_value = 0
    paramGroup.param_map["NPDPII_THR_F_P"].fine_value = 0

    paramGroup.param_map["PS_WEIGHT_INH_F_N"].coarse_value = 0
    paramGroup.param_map["PS_WEIGHT_INH_F_N"].fine_value = 0

    paramGroup.param_map["NPDPII_TAU_S_P"].coarse_value = 4
    paramGroup.param_map["NPDPII_TAU_S_P"].fine_value = 80

    paramGroup.param_map["NPDPII_THR_S_P"].coarse_value = 0
    paramGroup.param_map["NPDPII_THR_S_P"].fine_value = 0

    paramGroup.param_map["PS_WEIGHT_INH_S_N"].coarse_value = 0
    paramGroup.param_map["PS_WEIGHT_INH_S_N"].fine_value = 0

    paramGroup.param_map["IF_AHTAU_N"].coarse_value = 4
    paramGroup.param_map["IF_AHTAU_N"].fine_value = 80

    paramGroup.param_map["IF_AHTHR_N"].coarse_value = 0
    paramGroup.param_map["IF_AHTHR_N"].fine_value = 0

    paramGroup.param_map["IF_AHW_P"].coarse_value = 0
    paramGroup.param_map["IF_AHW_P"].fine_value = 0

    paramGroup.param_map["IF_CASC_N"].coarse_value = 0
    paramGroup.param_map["IF_CASC_N"].fine_value = 0

    paramGroup.param_map["PULSE_PWLK_P"].coarse_value = 4
    paramGroup.param_map["PULSE_PWLK_P"].fine_value = 106

    paramGroup.param_map["R2R_P"].coarse_value = 3
    paramGroup.param_map["R2R_P"].fine_value = 85

    paramGroup.param_map["IF_BUF_P"].coarse_value = 3
    paramGroup.param_map["IF_BUF_P"].fine_value = 80

    return paramGroup


if __name__ == "__main__":
    sender_endpoint = "tcp://0.0.0.0:33336"
    receiver_endpoint = "tcp://0.0.0.0:33335"
    node_id = 1
    interpreter_id = 2
    visualizer_id = 3
    samna_node = samna.SamnaNode(sender_endpoint, receiver_endpoint, node_id)

    # setup the python interpreter node
    samna.setup_local_node(receiver_endpoint, sender_endpoint, interpreter_id)

    # open a connection to device_node
    samna.open_remote_node(node_id, "device_node")

    # retrieve unopened device
    devices = samna.device_node.DeviceController.get_unopened_devices()

    # print the info of all available devices
    for i in range(len(devices)):
        print("[",i,"]: ", devices[i])

    # open a selected device, by default the first one should be DYNAP-SE1.
    samna.device_node.DeviceController.open_device(devices[0], "dynapse1")

    # get Dynapse1Model
    model = samna.device_node.dynapse1

    # --------------------- open GUI ----------------------------
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

    port = random.randint(10**4, 10**5)
    viz_name = "visualizer"+str(port)
    # open a connection to the GUI node
    samna.open_remote_node(visualizer_id, viz_name)
    visualizer = getattr(samna, viz_name)

    try:
        # The GUI node contains a ZMQ receiver endpoint by default, we can set the address it should listen on
        gui_receiving_port = "tcp://0.0.0.0:"+str(port)
        visualizer.receiver.set_receiver_endpoint(gui_receiving_port) # local connection on port 40000
    except Exception as e:
        print("ERROR: "+str(e)+", please re-run open_gui()!")

    # get streamer node
    streamer_node = gui_graph.get_node(streamer_id)
    # stream on the same endpoint as the receiver is listening to
    streamer_node.set_streamer_endpoint(gui_receiving_port)

    # Connect the receiver output to the visualizer plots input
    visualizer.receiver.add_destination(visualizer.splitter.get_input_channel())

    # Add plots to the GUI
    activity_plot_id = visualizer.plots.add_activity_plot(64, 64, "DYNAP-SE1")
    visualizer.splitter.add_destination("passthrough", visualizer.plots.get_plot_input(activity_plot_id))

    # List currently displayed plots
    visualizer.plots.report()
    # --------------------- open GUI ----------------------------


    # ---------------------Test get serial number---------------------
    print("DYNAP-SE1 serial number: ", devices[0].serial_number)

    # get the interface api
    api = model.get_dynapse1_api()

    # ---------------------Test get serial number---------------------
    # print("DYNAP-SE1 board serial number:", api.get_serial_number())

    # ---------------------Test monitor_neuron---------------------
    print("Monitor neuron 66 on chip 0")
    api.monitor_neuron(1, 66)

    # Full sinkNode
    full_readout_node = samna.BasicSinkNode_dynapse1_dynapse1_event()

    # connect source node in Dynapse1DevKit to full_readout_node.
    model.get_source_node().add_destination(full_readout_node.get_input_channel())

    # ----------- build a graph with a neuronSelectFilter ----------------
    postNeuron = 20
    dynapse1_graph = samna.graph.EventFilterGraph()

    # Filtered sinkNode. Node 3. Initialized outside dynapse1_graph, not by add_filter_node.
    neuron_select_readout_node = samna.BasicSinkNode_dynapse1_dynapse1_event()

    # NeuronSelectFilterNode. Node 2. Initialized inside dynapse1_graph, by add_filter_node.
    neuron_select_filter_id = dynapse1_graph.add_filter_node("Dynapse1NeuronSelect")
    # Get this filterNode from the created graph and set selected global neuron IDs.
    neuron_select_filter = dynapse1_graph.get_node(neuron_select_filter_id)
    neuron_select_filter.set_neurons([postNeuron])

    # model.get_source_node() is Node 1. Initialized outside dynapse1_graph, not by add_filter_node.
    # Connect Node 1 to Node 2, using add_destination because Node 1 not inside dynapse1_graph.
    # Use graph.connect(node_id_1, node_id_2) only if both nodes inside graph.
    model.get_source_node().add_destination(dynapse1_graph.get_node_input(neuron_select_filter_id))

    # connect Node 2 to Node 3.
    dynapse1_graph.add_destination(neuron_select_filter_id, neuron_select_readout_node.get_input_channel())

    # start the graph
    dynapse1_graph.start()

    events = full_readout_node.get_events()
    print("Full event size: ", len(events))

    get_filtered_events(neuron_select_readout_node, [postNeuron])
    # ----------- build a graph with a neuronSelectFilter ----------------


    # ----------- Test get/set parameters ----------------
    # get parameter "IF_THR_N"
    config = model.get_configuration()
    print("Before update_parameter_group, IF_THR_N: ",
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].coarse_value,
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].fine_value)

    # set parameters
    paramGroup = gen_param_group()
    print("gen_param_group, IF_THR_N: ",
    paramGroup.param_map["IF_THR_N"].coarse_value,
    paramGroup.param_map["IF_THR_N"].fine_value)
    for chip in range(4):
        for core in range(4):
            model.update_parameter_group(paramGroup, chip, core)

    config = model.get_configuration()
    print("After update_parameter_group, IF_THR_N: ",
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].coarse_value,
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].fine_value)

    print("Set parameters, updateSingleParameter...")
    # set parameters of all 16 cores
    param = dyn1.Dynapse1Parameter("IF_THR_N", 5, 90)
    print(type(param), param)
    print(param.param_name, param.coarse_value, param.fine_value, param.type)
    for chip in range(4):
        for core in range(4):
            model.update_single_parameter(param, chip, core)

    config = model.get_configuration()
    print("After updateSingleParameter, IF_THR_N: ",
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].coarse_value,
    config.chips[0].cores[0].parameter_group.param_map["IF_THR_N"].fine_value)

    print("After ParameterSetup, IF_DC_P: ",
    config.chips[0].cores[0].parameter_group.param_map["IF_DC_P"].coarse_value,
    config.chips[0].cores[0].parameter_group.param_map["IF_DC_P"].fine_value)

    # ----------- Test get/set parameters ----------------

    print("*****Sleeping*****")
    time.sleep(2)
    events = full_readout_node.get_events()
    print("Full event size: ", len(events))

    # set neuron again to test if this works
    print("set_neurons again test")
    neuron_select_filter.set_neurons([postNeuron])
    print("*****Sleeping*****")
    time.sleep(2)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test poissonGen---------------------
    # build a connection between poissonGen and a neuron
    print("Set up poissonGen, 200Hz")
    preVneuron = 50
    rate = 200
    poisson_gen = model.get_poisson_gen()
    poisson_gen.set_chip_id(0)
    poisson_gen.write_poisson_rate_hz(preVneuron, rate) # neuron20 on chip 0 core 0

    newConfig = dyn1.Dynapse1Configuration()
    newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_neuron_id = preVneuron
    newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_core_id = 0
    newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].syn_type = dyn1.Dynapse1SynType.AMPA

    model.apply_configuration(newConfig)

    config = model.get_configuration()
    print("After connect to PoissonGen, C0c0N20, syn0: ",
    config.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_neuron_id,
    config.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_core_id,
    "dest0: ", config.chips[0].cores[0].neurons[postNeuron].destinations[0].target_chip_id,
    config.chips[0].cores[0].neurons[postNeuron].destinations[0].in_use)

    # get_events again after start poissonGen, should have more spikes.
    # print("Before start PoissonGen")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("Start PoissonGen!")
    poisson_gen.start()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After start PoissonGen")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("Stop PoissonGen!")
    poisson_gen.stop()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After stop PoissonGen")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])
    # ---------------------Test poissonGen---------------------

    # test: start the graph only then, in theory, filteredSinkNode should not receive anything before this
    # print("-------start dynapse1_graph------------")
    # dynapse1_graph.start()


    # ---------------------Test FPGA spikeGen---------------------
    # postNeuron = 66
    # newConfig = dyn1.Dynapse1Configuration()
    # newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_neuron_id = preVneuron
    # newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].listen_core_id = 0
    # newConfig.chips[0].cores[0].neurons[postNeuron].synapses[0].syn_type = dyn1.Dynapse1SynType.NMDA

    # -------------Set FPGA spikeGen------------
    print("Setting up FPGA spikeGen, 400 spikes in 2 second...")
    spike_times = np.linspace(0, 2, 400)
    neuron_ids = [preVneuron]*len(spike_times) # pre_ids, here sent from 1 virtual neuron
    target_chips = [0]*len(neuron_ids)
    isi_base = 900
    repeat_mode=False

    unit_fpga = isi_base/90 #us
    spike_times_us = np.array(spike_times)*1e6
    spike_times_unit_fpga = (spike_times_us / unit_fpga).astype('int')

    fpga_isi = np.array([0]+list(np.diff(spike_times_unit_fpga)), dtype=int)
    fpga_nrn_ids = np.array(neuron_ids)
    fpga_target_chips = np.array(target_chips)

    fpga_events = []
    for idx_isi, isi in enumerate(fpga_isi):
        fpga_event = dyn1.FpgaSpikeEvent()
        fpga_event.core_mask = 15 # 1111: to all 4 cores
        fpga_event.neuron_id = fpga_nrn_ids[idx_isi]
        fpga_event.target_chip = fpga_target_chips[idx_isi]
        fpga_event.isi = isi
        # fpga_event = dyn1.FpgaSpikeEvent(15, fpga_nrn_ids[idx_isi], fpga_target_chips[idx_isi], isi)
        fpga_events.append(fpga_event)

    fpga_spike_gen = model.get_fpga_spike_gen()
    fpga_spike_gen.set_variable_isi_mode(True)
    fpga_spike_gen.preload_stimulus(fpga_events)
    fpga_spike_gen.set_isi_multiplier(isi_base)
    fpga_spike_gen.set_repeat_mode(repeat_mode)
    # -------------Set FPGA spikeGen------------

    # print("Before start FPGA SpikeGen")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("Start FPGA SpikeGen!")
    fpga_spike_gen.start()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After start FPGA SpikeGen, 1st 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After start FPGA SpikeGen, 2nd 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("Stop FPGA SpikeGen!")
    fpga_spike_gen.stop()
    # print("******Sleeping for 2 sec*****")
    # time.sleep(2)
    # print("After stop FPGA SpikeGen")
    # get_full_events(full_readout_node)
    # get_filtered_events(neuron_select_readout_node, [postNeuron])

    # Switch to Repeat mode
    print("Set FPGA SpikeGen to repeat mode and restart!")
    fpga_spike_gen.set_repeat_mode(True)
    fpga_spike_gen.start()

    # ---------------------Test reset_timestamp()---------------------
    print("Reset timestamp!")
    api.reset_timestamp()
    print("Restart FPGA SpikeGen!")
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    print("After restart FPGA SpikeGen, 1st 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test reset_tau_2---------------------
    print("Reset tau2: (7, 255)")
    api.reset_tau_2(0,0) #chipId, coreId. 7, 255
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After restart FPGA SpikeGen, reset_tau_2, 2nd 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test reset_tau_1---------------------
    print("Reset tau1: (4, 80)")
    api.reset_tau_1(0,0) #chipId, coreId. 4, 80
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After restart FPGA SpikeGen, reset_tau_1, 3rd 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test set_tau_2---------------------
    print("set_tau_2: (0, postNeuron)")
    api.set_tau_2(0, postNeuron)
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After restart FPGA SpikeGen, set_tau_2, 4th 2 sec:")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test reset_tau_1 after set_tau_2---------------------
    print("Reset tau1: (4, 80)")
    api.reset_tau_1(0,0) #chipId, coreId. 4, 80
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    # print("After restart FPGA SpikeGen, reset_tau_1 after set_tau_2")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test stop graph---------------------
    print("Stop filter graph, and clear sinkNode buffer")
    dynapse1_graph.stop()
    # neuron_select_readout_node.get_events()
    get_filtered_events(neuron_select_readout_node, [postNeuron])
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    # ---------------------Test restart graph---------------------
    print("Restart filter graph")
    dynapse1_graph.start()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, [postNeuron])

    print("==========Reset filter to pass all neurons==========")
    neuron_select_filter.reset()

    # ---------------------Test stop graph---------------------
    print("Stop filter graph, and clear sinkNode buffer")
    dynapse1_graph.stop()
    # neuron_select_readout_node.get_events()
    get_filtered_events(neuron_select_readout_node, None)
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, None)

    # ---------------------Test restart graph---------------------
    print("Restart filter graph")
    dynapse1_graph.start()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, None)

    # ---------------------Test stop graph---------------------
    print("Stop filter graph, and clear sinkNode buffer")
    dynapse1_graph.stop()
    # neuron_select_readout_node.get_events()
    get_filtered_events(neuron_select_readout_node, None)
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, None)

    # ---------------------Test restart graph---------------------
    print("Restart filter graph")
    dynapse1_graph.start()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, None)
    print("Stop FPGA SpikeGen!")
    fpga_spike_gen.stop()
    print("******Sleeping for 2 sec*****")
    time.sleep(2)

    # print("After stop FPGA SpikeGen")
    get_full_events(full_readout_node)
    get_filtered_events(neuron_select_readout_node, None)
    # ---------------------Test FPGA spikeGen---------------------

    print("Test done.")
    
    samna.device_node.DeviceController.close_device("dynapse1")
