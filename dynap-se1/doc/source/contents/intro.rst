Getting started
=======================


About DYNAP-SE1
------------------

A DYNAP-SE1 board has 4 :func:`chips <samna.dynapse1.Dynapse1Chip>` and each chip contains 4 
:func:`cores <samna.dynapse1.Dynapse1Core>` featuring 256 silicon :func:`neurons <samna.dynapse1.
Dynapse1Neuron>`. 
We call the state of the 4 chips a :func:`configuration <samna.dynapse1.Dynapse1Configuration>`. 
Each silicon neuron has 64 :func:`synapses <samna.dynapse1.Dynapse1Synapse>` to receive the
incoming connections of its presynaptic neurons. 
Each core holds a :func:`parameter group <samna.dynapse1.Dynapse1ParameterGroup>` to store the
neuronal and synaptic parameters for its 256 neurons and their incoming synapses. 
The neurons in the same core share the same parameter values. 
There are 4 types of synapses: AMPA, NMDA, GABA_A, and GABA_B. 
1024 spike generators are available (implemented on the FPGA). 
Each of the spike generators can be used as a :func:`Poisson spike generator <samna.dynapse1.
Dynapse1PoissonGen>` or a :func:`normal FPGA spike generator <samna.dynapse1.
Dynapse1FpgaSpikeGen>`.

How to use it?
----------------

To use DYNAP-SE1, we recommend `Samna <https://synsense-sys-int.gitlab.io/samna/>`_ and its
Python utilities `library <https://gitlab.com/neuroinf/ctxctl_contrib/-/
tree/samna-dynapse1>`_. The latter is developed primarily by the `NCS 
group <https://www.ini.uzh.ch/en/research/groups/ncs.html>`_ of `INI <https://www.ini.uzh.ch/en.html>`_.
DYNAP-SE1 related section in Samna documentation is `here <https://synsense-sys-int.
gitlab.io/samna/devkits/dynapSeSeries/dynapse1/summary.html>`_ which describes some basic core APIs.
The Python repository adds more features to Samna for DYNAP-SE1, which wraps around the plain
Samna classes and functions to provide more user-friendly and convenient Python APIs 
for constructing networks, configuring hardware parameters, monitoring neurons activity, 
implementing learning algorithms, etc.

To get started, choose a directory and do the following to download the library:

.. code-block:: bash

    git clone git@gitlab.com:neuroinf/ctxctl_contrib.git
    cd ctxctl_contrib
    git checkout samna-dynapse1

Utilities library overview
----------------------------

The Python files (libraries) in the `samna-dynapse1` branch of the Python `repository <https://gitlab.com/neuroinf/ctxctl_contrib/-/tree/samna-dynapse1>`_ have the following functions: 

* `dynapse1constants.py` defines the hardware-specific parameters. 

* `dynapse1utils.py` contains functions that wrap around low-level Samna APIs for DYNAP-SE1 users.

* `netgen.py` includes basic network elements, e.g. neuron groups, synapses, and Winner-Take-All (WTA) structures, that can be added into ``NetworkGenerator`` to implement Spiking Neural Networks (SNNs) on DYNAP-SE1 processor.

* The `example` folder has some example scripts to use the DYNAP-SE1 board. `example.py` gives a simple example of how to implement a network on DYNAP-SE1 and `example_fpga_gen.py` changes the input from Poisson to constant spikes. `example_neuron_group.py` shows how to use building blocks in `netgen.py` to construct a network. Some example parameter files can be found in `example_parameter_files` folder. The other folders hold some testing scripts.

* `params.py` gives some board parameter configurations as examples.

* `stdp.py` and `stdp_utils.py` provide a learning framework for STDP-like algorithms. Implementation of triplet-STDP is given as an example, and other algorithms can be implemented by users. An example of training the plastic connections between a presynaptic and a postsynaptic neuron group is in `example/test_stdp.py`.