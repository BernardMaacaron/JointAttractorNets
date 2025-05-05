import samna.dynapse1 as dyn1
import sys
# Note: change the path to where your lib files are
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
import dynapse1utils as ut
from dynapse1constants import MAX_NUM_CAMS
from netgen import Neuron, NetworkGenerator

if __name__ == "__main__":
    # create a network
    net_gen = NetworkGenerator()

    # Test different abnormal cases
    is_spikegen = True
    try:
        print("--------------- WRONG post is spikegen ---------------")
        # post.is_spike_gen
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20,is_spikegen), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("WRONG post is spikegen pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG remove nonexisting conn ---------------")
        # remove nonexisting conn
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.remove_connection(Neuron(2,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        print("WRONG remove nonexisting conn pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- correct remove existing conn ---------------")
        net_gen.print_network()
        net_gen.remove_connection(Neuron(0,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.print_network()
        print("correct remove existing conn pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG Aliasing 1.1: same post, pre in different (Dynapse1/spikeGen) chips with different weight ---------------")
        # Aliasing 1.1: same post, pre in different (Dynapse1/spikeGen) chips with different weight
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10,is_spikegen), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("try 3 pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG Aliasing 1.2: same post, pre in different Dynapse1 chips with different weight ---------------")
        # Aliasing 1.2: same post, pre in different Dynapse1 chips with different weight
        net_gen.clear_network()
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(1,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("try 4 pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG Aliasing 2: different post neurons in the same core, receive different pre with same pre_tag ---------------")
        # Aliasing 2: different post neurons in the same core, receive different pre with same pre_tag
        net_gen.clear_network()
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(2,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("try 5 pass")

    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG out of cams ---------------")
        # out of cams
        net_gen.clear_network()
        for i in range(MAX_NUM_CAMS + 1):
            net_gen.add_connection(Neuron(0,0,i+10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("try 6 pass")

    except Exception as e:
        print(e)

    try:
        print("--------------- correct max cams ---------------")
        # max cams
        net_gen.clear_network()
        for i in range(MAX_NUM_CAMS):
            net_gen.add_connection(Neuron(0,0,i+10), Neuron(0,0,20), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("Max cams try pass")
    except Exception as e:
        print("Max cams try", e)

    try:
        print("--------------- correct cam reuse ---------------")
        # Warning only: cam reuse
        net_gen.clear_network()
        net_gen.add_connection(Neuron(2,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,50), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(2,0,10), Neuron(0,0,50), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("cam reuse, weight>1 try pass")
    except Exception as e:
        print(e)

    try:
        print("--------------- WRONG cam reuse + aliasing ---------------")
        # ERROR
        net_gen.clear_network()
        net_gen.add_connection(Neuron(2,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(3,0,10), Neuron(0,0,50), dyn1.Dynapse1SynType.AMPA)
        net_gen.add_connection(Neuron(2,0,10), Neuron(0,0,50), dyn1.Dynapse1SynType.AMPA)
        new_config = net_gen.make_dynapse1_configuration()
        print("cam reuse + aliasing try pass")
    except Exception as e:
        print(e)

    # build a network
    net_gen.clear_network()

    neuron_ids = [(0,0,10), (0,0,30), (0,2,60), (1,1,60), (3,1,107), (2,1,107), (2,3,152)]

    net_gen.add_connection(Neuron(0,1,66,is_spikegen), Neuron(0,0,10), dyn1.Dynapse1SynType.AMPA)
    # check sram of Neuron(0,0,10)
    net_gen.add_connection(Neuron(0,0,10), Neuron(0,0,30), dyn1.Dynapse1SynType.AMPA)
    net_gen.add_connection(Neuron(0,0,10), Neuron(0,2,60), dyn1.Dynapse1SynType.NMDA)
    net_gen.add_connection(Neuron(0,0,10), Neuron(1,1,60), dyn1.Dynapse1SynType.GABA_A)
    # check cam of Neuron(2,3,152)
    net_gen.add_connection(Neuron(3,1,107), Neuron(2,3,152), dyn1.Dynapse1SynType.GABA_B)
    net_gen.add_connection(Neuron(2,1,107), Neuron(2,3,152), dyn1.Dynapse1SynType.GABA_B)
    net_gen.add_connection(Neuron(3,1,107), Neuron(2,3,152), dyn1.Dynapse1SynType.GABA_B)
    net_gen.add_connection(Neuron(2,1,107), Neuron(2,3,152), dyn1.Dynapse1SynType.GABA_B)

    # print the network
    net_gen.print_network()

    # make a dynapse1config using the network
    new_config = net_gen.make_dynapse1_configuration()

    # print cam and sram of the above neurons
    for nid in neuron_ids:
        neuron = ut.get_neuron_from_config(new_config, nid[0], nid[1], nid[2])
        print("------------Neuron", nid, "------------")
        print("Cams:")
        ut.print_neuron_synapses(neuron, range(4))
        print("Srams:")
        ut.print_neuron_destinations(neuron)

    model, gui_process = ut.open_dynapse1()

    print("get dynapse1 model")
    # get the interface api
    api = model.get_dynapse1_api()
    print("get dynapse1 api")

    # apply the config
    model.apply_configuration(new_config)

    # check the config using get_config
    config = model.get_configuration()

    # print cam and sram of the above neurons
    for nid in neuron_ids:
        neuron = ut.get_neuron_from_config(config, nid[0], nid[1], nid[2])
        print("------------Neuron", nid,"------------")
        print("Cams:")
        ut.print_neuron_synapses(neuron, range(4))
        print("Srams:")
        ut.print_neuron_destinations(neuron)

    # net_gen.print_network()

    ut.close_dynapse1(model, gui_process)