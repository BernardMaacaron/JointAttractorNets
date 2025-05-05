import samna.dynapse1 as dyn1
import sys
# Note: change the path to where your lib files are
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
from netgen import Neuron, NeuronGroup, Synapses, WTA_connections, NetworkGenerator, add_synapses, add_wta_conns

if __name__ == "__main__":
    """This is an example of how to use NeuronGroup and add_connections* functions 
    to create network and the corresponding Dynapse1Configuration using NetworkGenerator."""
    # define 2 neuron groups
    chip1 = 0
    core1 = 0
    nids1 = [101,102,103]
    pop1 = NeuronGroup(chip1,core1,nids1,True)
    print('pop1',pop1.chip_id, pop1.core_id, pop1.neuron_ids,pop1.neurons)

    chip2 = 0
    core2 = 1
    nids2 = [14,15,16]
    pop2 = NeuronGroup(chip2,core2,nids2)
    print('pop2',pop2.chip_id, pop2.core_id, pop2.neuron_ids,pop2.neurons)

    # define 2 neuron groups
    print('When chip_id changes, neurons follow the change!')
    pop2.chip_id = 2
    print('pop2',pop2.chip_id, pop2.core_id, pop2.neuron_ids,pop2.neurons)

    net_gen = NetworkGenerator()

    print('\nadd_connections_from_list')
    net_gen.add_connections_from_list(pop1.neurons, pop2.neurons, dyn1.Dynapse1SynType.AMPA, [0,1,2,0], [2,1,0,2])
    print(net_gen.network)
    
    print('remove_connections_from_list')
    net_gen.remove_connections_from_list(pop1.neurons, pop2.neurons, dyn1.Dynapse1SynType.AMPA, [0,1,2,0], [2,1,0,2])
    print(net_gen.network)

    print('\nadd_connections_from_type, one2one')
    net_gen.add_connections_from_type(pop1.neurons, pop2.neurons, dyn1.Dynapse1SynType.AMPA, 'one2one')
    print(net_gen.network)
    net_gen.clear_network()

    print('add_connections_from_type, all2all')
    net_gen.add_connections_from_type(pop1.neurons, pop2.neurons, dyn1.Dynapse1SynType.AMPA, conn_type='all2all', p=0.8, rand_seed=56)
    print(net_gen.network)
    net_gen.clear_network()

    print('add_synapses using NeuronGroup, one2one')
    pre_group = NeuronGroup(chip1, core1, nids1)
    post_group = NeuronGroup(chip2,core2,nids2)
    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.AMPA, conn_type='one2one')
    add_synapses(net_gen, syn)
    print(net_gen.network)
    net_gen.clear_network()

    print('add_synapses using NeuronGroup, all2all')
    pre_group = NeuronGroup(chip1, core1, nids1)
    post_group = NeuronGroup(chip2,core2,nids2)
    syn = Synapses(pre_group, post_group, dyn1.Dynapse1SynType.AMPA, conn_type='all2all')
    add_synapses(net_gen, syn)
    print(net_gen.network)
    net_gen.clear_network()

    print('add_synapses using NeuronGroup, WTA')
    pre_group = NeuronGroup(chip1, core1, nids1)
    post_group = NeuronGroup(chip2,core2,nids2)
    wta = WTA_connections(pre_group, post_group, syn_type_ei= dyn1.Dynapse1SynType.AMPA, syn_type_ie=dyn1.Dynapse1SynType.GABA_B, syn_type_ee=dyn1.Dynapse1SynType.NMDA, ee_pres=[0,1], ee_posts=[0,1])
    add_wta_conns(net_gen, wta)
    print(net_gen.network)
    net_gen.clear_network()

    new_config = net_gen.make_dynapse1_configuration()