Modules
========

dynapse1utils
--------------
`dynapse1utils.py` contains functions that wrap around low-level Samna APIs for DYNAP-SE1 users. 

.. automodule:: dynapse1utils
    :members:
    :undoc-members:
    :show-inheritance:


netgen
--------------
`netgen.py` includes basic network elements, e.g. neuron groups, synapses, and Winner-Take-All
(WTA) structures, that can be added into ``NetworkGenerator`` to implement Spiking Neural Networks
(SNNs) on DYNAP-SE1 processor.

.. automodule:: netgen
    :members:
    :undoc-members:
    :show-inheritance:

params
--------------
`params.py` gives some board parameter configurations as examples.

.. automodule:: params
    :members:
    :undoc-members:
    :show-inheritance:

STDP learning
--------------
`stdp.py` and `stdp_utils.py` provide a learning framework for STDP-like algorithms. 
Implementation of triplet-STDP is given as an example, and other algorithms can be implemented by
users. An example of training the plastic connections between a presynaptic and a postsynaptic 
neuron group is in `example/test_stdp.py`.

stdp
^^^^
.. automodule:: stdp
    :members:
    :undoc-members:
    :show-inheritance:

stdp_utils
^^^^^^^^^^

.. automodule:: stdp_utils
    :members:
    :undoc-members:
    :show-inheritance:

stdp_algorithms
^^^^^^^^^^^^^^^^^

.. automodule:: stdp_algorithms.triplet_stdp_details
    :members:
    :undoc-members:
    :show-inheritance:

Detailed netgen Implementation
--------------------------------
The detailed implementation of NetworkGenerator is in `details/
netgen_details.py`.

.. automodule:: details.netgen_details
    :members:
    :undoc-members:
    :show-inheritance: