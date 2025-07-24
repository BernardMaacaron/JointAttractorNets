from brian2 import *

import os
print("Current working directory:", os.getcwd())
repo_directory = os.path.dirname(os.getcwd())
print("Repository directory:", repo_directory)

import sys
dynapse_path = os.path.join(repo_directory, 'dynapse-simulator')
if dynapse_path not in sys.path:
    sys.path.append(dynapse_path)
    
from DynapSE import DynapSE

from equations.dynapse_eq import *
from parameters.dynapse_param import *

# C++ code generation for faster spiking network simulation
set_device('cpp_standalone')

# The clock of Brian2 simulation for numerically solve ODEs
defaultclock.dt = 20 * us