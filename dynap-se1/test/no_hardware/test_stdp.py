import unittest
import numpy as np
import sys
sys.path.append("/home/jingyue/aa_projects/samna_projects/ctxctl_contrib/")
from stdp_utils import floatW2intW

class StdpTest(unittest.TestCase):
    num_hidIn_neurons = 4
    num_hidOut_neurons = 4
    def test_floatW2intW(self):
        # given 
        expect_int_w = np.ones((self.num_hidIn_neurons, self.num_hidOut_neurons), dtype=int)
        expect_int_w[0][2] = 2

        # when
        float_w = np.ones((self.num_hidIn_neurons, self.num_hidOut_neurons), dtype=float) * 0.1
        float_w[0][2] = 0.4

        result_int_w = floatW2intW(float_w, 5, 66, 0.1)
        # then
        self.assertEqual(expect_int_w.all(), result_int_w.all())

if __name__ == "__main__":
    unittest.main()