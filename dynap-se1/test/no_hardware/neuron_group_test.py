import unittest

import sys
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
from io import StringIO
from netgen import Neuron, NeuronGroup 

class NeuronGroupTest(unittest.TestCase):
    chip1 = 0
    core1 = 0
    nids1 = [101,102,103]

    def init_neuron_group(self):
        neuron_group = NeuronGroup(self.chip1,self.core1,self.nids1)
        return neuron_group
    
    def test_init_neurons(self):
        # given
        expected_neurons = []
        for nid in self.nids1:
            expected_neurons.append(Neuron(self.chip1,self.core1,nid))

        # when
        neuron_group = self.init_neuron_group()
        result_neurons = neuron_group.neurons

        # then
        self.assertEqual(expected_neurons, result_neurons)

    def test_neurons_property(self):
        # given
        new_chip_id = 2
        expected_neurons = []
        for nid in self.nids1:
            expected_neurons.append(Neuron(new_chip_id,self.core1,nid))
        
        # when
        neuron_group = self.init_neuron_group()
        neuron_group.chip_id = new_chip_id
        result_neurons = neuron_group.neurons

        # then
        self.assertEqual(expected_neurons, result_neurons)
    
    def test_errors(self):
        """Test exceptions"""
        # TODO: add subtests for all Exceptions
        with self.assertRaises(Exception):
            NeuronGroup(5,0,[0,1,2])
    
    def test_warning(self):
        output = StringIO()
        sys.stdout = output
        NeuronGroup(0, 0, [0])
        sys.stdout = sys.__stdout__
        self.assertEqual(output.getvalue(), "WARNING: be careful, you are using neuron 0 from a chip to construct a neuron group!\n")
        
    
if __name__ == "__main__":
    """ execute all tests in module """
    unittest.main()