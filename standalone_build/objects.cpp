

#include "objects.h"
#include "synapses_classes.h"
#include "brianlib/clocks.h"
#include "brianlib/dynamic_array.h"
#include "brianlib/stdint_compat.h"
#include "network.h"
#include<random>
#include<vector>
#include<iostream>
#include<fstream>
#include<map>
#include<tuple>
#include<cstdlib>
#include<string>

namespace brian {

std::string results_dir = "results/";  // can be overwritten by --results_dir command line arg

// For multhreading, we need one generator for each thread. We also create a distribution for
// each thread, even though this is not strictly necessary for the uniform distribution, as
// the distribution is stateless.
std::vector< RandomGenerator > _random_generators;

//////////////// networks /////////////////
Network network;

void set_variable_from_value(std::string varname, char* var_pointer, size_t size, char value) {
    #ifdef DEBUG
    std::cout << "Setting '" << varname << "' to " << (value == 1 ? "True" : "False") << std::endl;
    #endif
    std::fill(var_pointer, var_pointer+size, value);
}

template<class T> void set_variable_from_value(std::string varname, T* var_pointer, size_t size, T value) {
    #ifdef DEBUG
    std::cout << "Setting '" << varname << "' to " << value << std::endl;
    #endif
    std::fill(var_pointer, var_pointer+size, value);
}

template<class T> void set_variable_from_file(std::string varname, T* var_pointer, size_t data_size, std::string filename) {
    ifstream f;
    streampos size;
    #ifdef DEBUG
    std::cout << "Setting '" << varname << "' from file '" << filename << "'" << std::endl;
    #endif
    f.open(filename, ios::in | ios::binary | ios::ate);
    size = f.tellg();
    if (size != data_size) {
        std::cerr << "Error reading '" << filename << "': file size " << size << " does not match expected size " << data_size << std::endl;
        return;
    }
    f.seekg(0, ios::beg);
    if (f.is_open())
        f.read(reinterpret_cast<char *>(var_pointer), data_size);
    else
        std::cerr << "Could not read '" << filename << "'" << std::endl;
    if (f.fail())
        std::cerr << "Error reading '" << filename << "'" << std::endl;
}

//////////////// set arrays by name ///////
void set_variable_by_name(std::string name, std::string s_value) {
    size_t var_size;
    size_t data_size;
    // C-style or Python-style capitalization is allowed for boolean values
    if (s_value == "true" || s_value == "True")
        s_value = "1";
    else if (s_value == "false" || s_value == "False")
        s_value = "0";
    // non-dynamic arrays
    if (name == "glob_inh_neuron._spikespace") {
        var_size = 2;
        data_size = 2*sizeof(int32_t);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<int32_t>(name, _array_glob_inh_neuron__spikespace, var_size, (int32_t)atoi(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron__spikespace, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.I_ext") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_glob_inh_neuron_I_ext, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_I_ext, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.I_syn") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_glob_inh_neuron_I_syn, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_I_syn, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.I_vel") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_glob_inh_neuron_I_vel, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_I_vel, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.lastspike") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_glob_inh_neuron_lastspike, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_lastspike, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.not_refractory") {
        var_size = 1;
        data_size = 1*sizeof(char);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value(name, _array_glob_inh_neuron_not_refractory, var_size, (char)atoi(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_not_refractory, data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh_neuron.V") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_glob_inh_neuron_V, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_glob_inh_neuron_V, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons._spikespace") {
        var_size = 121;
        data_size = 121*sizeof(int32_t);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<int32_t>(name, _array_ring_neurons__spikespace, var_size, (int32_t)atoi(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons__spikespace, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.I_ext") {
        var_size = 120;
        data_size = 120*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_neurons_I_ext, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_I_ext, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.I_syn") {
        var_size = 120;
        data_size = 120*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_neurons_I_syn, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_I_syn, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.I_vel") {
        var_size = 120;
        data_size = 120*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_neurons_I_vel, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_I_vel, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.lastspike") {
        var_size = 120;
        data_size = 120*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_neurons_lastspike, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_lastspike, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.not_refractory") {
        var_size = 120;
        data_size = 120*sizeof(char);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value(name, _array_ring_neurons_not_refractory, var_size, (char)atoi(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_not_refractory, data_size, s_value);
        }
        return;
    }
    if (name == "ring_neurons.V") {
        var_size = 120;
        data_size = 120*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_neurons_V, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_neurons_V, data_size, s_value);
        }
        return;
    }
    if (name == "ring_synapses_asym.vel_in") {
        var_size = 1;
        data_size = 1*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, _array_ring_synapses_asym_vel_in, var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, _array_ring_synapses_asym_vel_in, data_size, s_value);
        }
        return;
    }
    // dynamic arrays (1d)
    if (name == "glob_inh2pool.delay") {
        var_size = _dynamic_array_glob_inh2pool_delay.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_glob_inh2pool_delay[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_glob_inh2pool_delay[0], data_size, s_value);
        }
        return;
    }
    if (name == "glob_inh2pool.w_inh") {
        var_size = _dynamic_array_glob_inh2pool_w_inh.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_glob_inh2pool_w_inh[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_glob_inh2pool_w_inh[0], data_size, s_value);
        }
        return;
    }
    if (name == "pool2glob_inh.delay") {
        var_size = _dynamic_array_pool2glob_inh_delay.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_pool2glob_inh_delay[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_pool2glob_inh_delay[0], data_size, s_value);
        }
        return;
    }
    if (name == "pool2glob_inh.w_exc") {
        var_size = _dynamic_array_pool2glob_inh_w_exc.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_pool2glob_inh_w_exc[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_pool2glob_inh_w_exc[0], data_size, s_value);
        }
        return;
    }
    if (name == "ring_synapses_asym.delay") {
        var_size = _dynamic_array_ring_synapses_asym_delay.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_ring_synapses_asym_delay[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_ring_synapses_asym_delay[0], data_size, s_value);
        }
        return;
    }
    if (name == "ring_synapses_asym.w_asym") {
        var_size = _dynamic_array_ring_synapses_asym_w_asym.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_ring_synapses_asym_w_asym[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_ring_synapses_asym_w_asym[0], data_size, s_value);
        }
        return;
    }
    if (name == "ring_synapses.delay") {
        var_size = _dynamic_array_ring_synapses_delay.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_ring_synapses_delay[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_ring_synapses_delay[0], data_size, s_value);
        }
        return;
    }
    if (name == "ring_synapses.w") {
        var_size = _dynamic_array_ring_synapses_w.size();
        data_size = var_size*sizeof(double);
        if (s_value[0] == '-' || (s_value[0] >= '0' && s_value[0] <= '9')) {
            // set from single value
            set_variable_from_value<double>(name, &_dynamic_array_ring_synapses_w[0], var_size, (double)atof(s_value.c_str()));

        } else {
            // set from file
            set_variable_from_file(name, &_dynamic_array_ring_synapses_w[0], data_size, s_value);
        }
        return;
    }
    std::cerr << "Cannot set unknown variable '" << name << "'." << std::endl;
    exit(1);
}
//////////////// arrays ///////////////////
double * _array_defaultclock_dt;
const int _num__array_defaultclock_dt = 1;
double * _array_defaultclock_t;
const int _num__array_defaultclock_t = 1;
int64_t * _array_defaultclock_timestep;
const int _num__array_defaultclock_timestep = 1;
int32_t * _array_glob_inh2pool_N;
const int _num__array_glob_inh2pool_N = 1;
int32_t * _array_glob_inh_neuron__spikespace;
const int _num__array_glob_inh_neuron__spikespace = 2;
int32_t * _array_glob_inh_neuron_i;
const int _num__array_glob_inh_neuron_i = 1;
double * _array_glob_inh_neuron_I_ext;
const int _num__array_glob_inh_neuron_I_ext = 1;
double * _array_glob_inh_neuron_I_syn;
const int _num__array_glob_inh_neuron_I_syn = 1;
double * _array_glob_inh_neuron_I_vel;
const int _num__array_glob_inh_neuron_I_vel = 1;
double * _array_glob_inh_neuron_lastspike;
const int _num__array_glob_inh_neuron_lastspike = 1;
char * _array_glob_inh_neuron_not_refractory;
const int _num__array_glob_inh_neuron_not_refractory = 1;
double * _array_glob_inh_neuron_V;
const int _num__array_glob_inh_neuron_V = 1;
int32_t * _array_pool2glob_inh_N;
const int _num__array_pool2glob_inh_N = 1;
int32_t * _array_ring_neurons__spikespace;
const int _num__array_ring_neurons__spikespace = 121;
int32_t * _array_ring_neurons_i;
const int _num__array_ring_neurons_i = 120;
double * _array_ring_neurons_I_ext;
const int _num__array_ring_neurons_I_ext = 120;
double * _array_ring_neurons_I_syn;
const int _num__array_ring_neurons_I_syn = 120;
double * _array_ring_neurons_I_vel;
const int _num__array_ring_neurons_I_vel = 120;
double * _array_ring_neurons_lastspike;
const int _num__array_ring_neurons_lastspike = 120;
char * _array_ring_neurons_not_refractory;
const int _num__array_ring_neurons_not_refractory = 120;
double * _array_ring_neurons_run_regularly_clock_dt;
const int _num__array_ring_neurons_run_regularly_clock_dt = 1;
double * _array_ring_neurons_run_regularly_clock_t;
const int _num__array_ring_neurons_run_regularly_clock_t = 1;
int64_t * _array_ring_neurons_run_regularly_clock_timestep;
const int _num__array_ring_neurons_run_regularly_clock_timestep = 1;
double * _array_ring_neurons_V;
const int _num__array_ring_neurons_V = 120;
int32_t * _array_ring_synapses_asym_N;
const int _num__array_ring_synapses_asym_N = 1;
double * _array_ring_synapses_asym_vel_in;
const int _num__array_ring_synapses_asym_vel_in = 1;
int32_t * _array_ring_synapses_N;
const int _num__array_ring_synapses_N = 1;
int32_t * _array_spikemonitor_1__source_idx;
const int _num__array_spikemonitor_1__source_idx = 1;
int32_t * _array_spikemonitor_1_count;
const int _num__array_spikemonitor_1_count = 1;
int32_t * _array_spikemonitor_1_N;
const int _num__array_spikemonitor_1_N = 1;
int32_t * _array_spikemonitor__source_idx;
const int _num__array_spikemonitor__source_idx = 120;
int32_t * _array_spikemonitor_count;
const int _num__array_spikemonitor_count = 120;
int32_t * _array_spikemonitor_N;
const int _num__array_spikemonitor_N = 1;
int32_t * _array_statemonitor_1__indices;
const int _num__array_statemonitor_1__indices = 120;
double * _array_statemonitor_1_I_ext;
const int _num__array_statemonitor_1_I_ext = (0, 120);
int32_t * _array_statemonitor_1_N;
const int _num__array_statemonitor_1_N = 1;
int32_t * _array_statemonitor_2__indices;
const int _num__array_statemonitor_2__indices = 1;
int32_t * _array_statemonitor_2_N;
const int _num__array_statemonitor_2_N = 1;
double * _array_statemonitor_2_V;
const int _num__array_statemonitor_2_V = (0, 1);
int32_t * _array_statemonitor__indices;
const int _num__array_statemonitor__indices = 120;
int32_t * _array_statemonitor_N;
const int _num__array_statemonitor_N = 1;
double * _array_statemonitor_V;
const int _num__array_statemonitor_V = (0, 120);

//////////////// dynamic arrays 1d /////////
std::vector<int32_t> _dynamic_array_glob_inh2pool__synaptic_post;
std::vector<int32_t> _dynamic_array_glob_inh2pool__synaptic_pre;
std::vector<double> _dynamic_array_glob_inh2pool_delay;
std::vector<int32_t> _dynamic_array_glob_inh2pool_N_incoming;
std::vector<int32_t> _dynamic_array_glob_inh2pool_N_outgoing;
std::vector<double> _dynamic_array_glob_inh2pool_w_inh;
std::vector<int32_t> _dynamic_array_pool2glob_inh__synaptic_post;
std::vector<int32_t> _dynamic_array_pool2glob_inh__synaptic_pre;
std::vector<double> _dynamic_array_pool2glob_inh_delay;
std::vector<int32_t> _dynamic_array_pool2glob_inh_N_incoming;
std::vector<int32_t> _dynamic_array_pool2glob_inh_N_outgoing;
std::vector<double> _dynamic_array_pool2glob_inh_w_exc;
std::vector<int32_t> _dynamic_array_ring_synapses__synaptic_post;
std::vector<int32_t> _dynamic_array_ring_synapses__synaptic_pre;
std::vector<int32_t> _dynamic_array_ring_synapses_asym__synaptic_post;
std::vector<int32_t> _dynamic_array_ring_synapses_asym__synaptic_pre;
std::vector<double> _dynamic_array_ring_synapses_asym_delay;
std::vector<int32_t> _dynamic_array_ring_synapses_asym_N_incoming;
std::vector<int32_t> _dynamic_array_ring_synapses_asym_N_outgoing;
std::vector<double> _dynamic_array_ring_synapses_asym_w_asym;
std::vector<double> _dynamic_array_ring_synapses_delay;
std::vector<int32_t> _dynamic_array_ring_synapses_N_incoming;
std::vector<int32_t> _dynamic_array_ring_synapses_N_outgoing;
std::vector<double> _dynamic_array_ring_synapses_w;
std::vector<int32_t> _dynamic_array_spikemonitor_1_i;
std::vector<double> _dynamic_array_spikemonitor_1_t;
std::vector<int32_t> _dynamic_array_spikemonitor_i;
std::vector<double> _dynamic_array_spikemonitor_t;
std::vector<double> _dynamic_array_statemonitor_1_t;
std::vector<double> _dynamic_array_statemonitor_2_t;
std::vector<double> _dynamic_array_statemonitor_t;

//////////////// dynamic arrays 2d /////////
DynamicArray2D<double> _dynamic_array_statemonitor_1_I_ext;
DynamicArray2D<double> _dynamic_array_statemonitor_2_V;
DynamicArray2D<double> _dynamic_array_statemonitor_V;

/////////////// static arrays /////////////
double * _static_array__array_ring_neurons_I_ext;
const int _num__static_array__array_ring_neurons_I_ext = 120;
double * _static_array__array_ring_neurons_I_ext_1;
const int _num__static_array__array_ring_neurons_I_ext_1 = 120;
int32_t * _static_array__array_statemonitor_1__indices;
const int _num__static_array__array_statemonitor_1__indices = 120;
int32_t * _static_array__array_statemonitor__indices;
const int _num__static_array__array_statemonitor__indices = 120;

//////////////// synapses /////////////////
// glob_inh2pool
SynapticPathway glob_inh2pool_pre(
    _dynamic_array_glob_inh2pool__synaptic_pre,
    0, 1);
// pool2glob_inh
SynapticPathway pool2glob_inh_pre(
    _dynamic_array_pool2glob_inh__synaptic_pre,
    0, 120);
// ring_synapses
SynapticPathway ring_synapses_pre(
    _dynamic_array_ring_synapses__synaptic_pre,
    0, 120);
// ring_synapses_asym
SynapticPathway ring_synapses_asym_pre(
    _dynamic_array_ring_synapses_asym__synaptic_pre,
    0, 120);

//////////////// clocks ///////////////////
Clock defaultclock;  // attributes will be set in run.cpp
Clock ring_neurons_run_regularly_clock;  // attributes will be set in run.cpp

// Profiling information for each code object
}

void _init_arrays()
{
    using namespace brian;

    // Arrays initialized to 0
    _array_defaultclock_dt = new double[1];
    
    for(int i=0; i<1; i++) _array_defaultclock_dt[i] = 0;

    _array_defaultclock_t = new double[1];
    
    for(int i=0; i<1; i++) _array_defaultclock_t[i] = 0;

    _array_defaultclock_timestep = new int64_t[1];
    
    for(int i=0; i<1; i++) _array_defaultclock_timestep[i] = 0;

    _array_glob_inh2pool_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_glob_inh2pool_N[i] = 0;

    _array_glob_inh_neuron__spikespace = new int32_t[2];
    
    for(int i=0; i<2; i++) _array_glob_inh_neuron__spikespace[i] = 0;

    _array_glob_inh_neuron_i = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_i[i] = 0;

    _array_glob_inh_neuron_I_ext = new double[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_I_ext[i] = 0;

    _array_glob_inh_neuron_I_syn = new double[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_I_syn[i] = 0;

    _array_glob_inh_neuron_I_vel = new double[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_I_vel[i] = 0;

    _array_glob_inh_neuron_lastspike = new double[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_lastspike[i] = 0;

    _array_glob_inh_neuron_not_refractory = new char[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_not_refractory[i] = 0;

    _array_glob_inh_neuron_V = new double[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_V[i] = 0;

    _array_pool2glob_inh_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_pool2glob_inh_N[i] = 0;

    _array_ring_neurons__spikespace = new int32_t[121];
    
    for(int i=0; i<121; i++) _array_ring_neurons__spikespace[i] = 0;

    _array_ring_neurons_i = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_i[i] = 0;

    _array_ring_neurons_I_ext = new double[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_I_ext[i] = 0;

    _array_ring_neurons_I_syn = new double[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_I_syn[i] = 0;

    _array_ring_neurons_I_vel = new double[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_I_vel[i] = 0;

    _array_ring_neurons_lastspike = new double[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_lastspike[i] = 0;

    _array_ring_neurons_not_refractory = new char[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_not_refractory[i] = 0;

    _array_ring_neurons_run_regularly_clock_dt = new double[1];
    
    for(int i=0; i<1; i++) _array_ring_neurons_run_regularly_clock_dt[i] = 0;

    _array_ring_neurons_run_regularly_clock_t = new double[1];
    
    for(int i=0; i<1; i++) _array_ring_neurons_run_regularly_clock_t[i] = 0;

    _array_ring_neurons_run_regularly_clock_timestep = new int64_t[1];
    
    for(int i=0; i<1; i++) _array_ring_neurons_run_regularly_clock_timestep[i] = 0;

    _array_ring_neurons_V = new double[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_V[i] = 0;

    _array_ring_synapses_asym_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_ring_synapses_asym_N[i] = 0;

    _array_ring_synapses_asym_vel_in = new double[1];
    
    for(int i=0; i<1; i++) _array_ring_synapses_asym_vel_in[i] = 0;

    _array_ring_synapses_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_ring_synapses_N[i] = 0;

    _array_spikemonitor_1__source_idx = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_spikemonitor_1__source_idx[i] = 0;

    _array_spikemonitor_1_count = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_spikemonitor_1_count[i] = 0;

    _array_spikemonitor_1_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_spikemonitor_1_N[i] = 0;

    _array_spikemonitor__source_idx = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_spikemonitor__source_idx[i] = 0;

    _array_spikemonitor_count = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_spikemonitor_count[i] = 0;

    _array_spikemonitor_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_spikemonitor_N[i] = 0;

    _array_statemonitor_1__indices = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_statemonitor_1__indices[i] = 0;

    _array_statemonitor_1_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_statemonitor_1_N[i] = 0;

    _array_statemonitor_2__indices = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_statemonitor_2__indices[i] = 0;

    _array_statemonitor_2_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_statemonitor_2_N[i] = 0;

    _array_statemonitor__indices = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_statemonitor__indices[i] = 0;

    _array_statemonitor_N = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_statemonitor_N[i] = 0;


    // Arrays initialized to an "arange"
    _array_glob_inh_neuron_i = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_glob_inh_neuron_i[i] = 0 + i;

    _array_ring_neurons_i = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_ring_neurons_i[i] = 0 + i;

    _array_spikemonitor_1__source_idx = new int32_t[1];
    
    for(int i=0; i<1; i++) _array_spikemonitor_1__source_idx[i] = 0 + i;

    _array_spikemonitor__source_idx = new int32_t[120];
    
    for(int i=0; i<120; i++) _array_spikemonitor__source_idx[i] = 0 + i;


    // static arrays
    _static_array__array_ring_neurons_I_ext = new double[120];
    _static_array__array_ring_neurons_I_ext_1 = new double[120];
    _static_array__array_statemonitor_1__indices = new int32_t[120];
    _static_array__array_statemonitor__indices = new int32_t[120];

    // Random number generator states
    std::random_device rd;
    for (int i=0; i<1; i++)
        _random_generators.push_back(RandomGenerator());
}

void _load_arrays()
{
    using namespace brian;

    ifstream f_static_array__array_ring_neurons_I_ext;
    f_static_array__array_ring_neurons_I_ext.open("static_arrays/_static_array__array_ring_neurons_I_ext", ios::in | ios::binary);
    if(f_static_array__array_ring_neurons_I_ext.is_open())
    {
        f_static_array__array_ring_neurons_I_ext.read(reinterpret_cast<char*>(_static_array__array_ring_neurons_I_ext), 120*sizeof(double));
    } else
    {
        std::cout << "Error opening static array _static_array__array_ring_neurons_I_ext." << endl;
    }
    ifstream f_static_array__array_ring_neurons_I_ext_1;
    f_static_array__array_ring_neurons_I_ext_1.open("static_arrays/_static_array__array_ring_neurons_I_ext_1", ios::in | ios::binary);
    if(f_static_array__array_ring_neurons_I_ext_1.is_open())
    {
        f_static_array__array_ring_neurons_I_ext_1.read(reinterpret_cast<char*>(_static_array__array_ring_neurons_I_ext_1), 120*sizeof(double));
    } else
    {
        std::cout << "Error opening static array _static_array__array_ring_neurons_I_ext_1." << endl;
    }
    ifstream f_static_array__array_statemonitor_1__indices;
    f_static_array__array_statemonitor_1__indices.open("static_arrays/_static_array__array_statemonitor_1__indices", ios::in | ios::binary);
    if(f_static_array__array_statemonitor_1__indices.is_open())
    {
        f_static_array__array_statemonitor_1__indices.read(reinterpret_cast<char*>(_static_array__array_statemonitor_1__indices), 120*sizeof(int32_t));
    } else
    {
        std::cout << "Error opening static array _static_array__array_statemonitor_1__indices." << endl;
    }
    ifstream f_static_array__array_statemonitor__indices;
    f_static_array__array_statemonitor__indices.open("static_arrays/_static_array__array_statemonitor__indices", ios::in | ios::binary);
    if(f_static_array__array_statemonitor__indices.is_open())
    {
        f_static_array__array_statemonitor__indices.read(reinterpret_cast<char*>(_static_array__array_statemonitor__indices), 120*sizeof(int32_t));
    } else
    {
        std::cout << "Error opening static array _static_array__array_statemonitor__indices." << endl;
    }
}

void _write_arrays()
{
    using namespace brian;

    ofstream outfile__array_defaultclock_dt;
    outfile__array_defaultclock_dt.open(results_dir + "_array_defaultclock_dt_1978099143", ios::binary | ios::out);
    if(outfile__array_defaultclock_dt.is_open())
    {
        outfile__array_defaultclock_dt.write(reinterpret_cast<char*>(_array_defaultclock_dt), 1*sizeof(_array_defaultclock_dt[0]));
        outfile__array_defaultclock_dt.close();
    } else
    {
        std::cout << "Error writing output file for _array_defaultclock_dt." << endl;
    }
    ofstream outfile__array_defaultclock_t;
    outfile__array_defaultclock_t.open(results_dir + "_array_defaultclock_t_2669362164", ios::binary | ios::out);
    if(outfile__array_defaultclock_t.is_open())
    {
        outfile__array_defaultclock_t.write(reinterpret_cast<char*>(_array_defaultclock_t), 1*sizeof(_array_defaultclock_t[0]));
        outfile__array_defaultclock_t.close();
    } else
    {
        std::cout << "Error writing output file for _array_defaultclock_t." << endl;
    }
    ofstream outfile__array_defaultclock_timestep;
    outfile__array_defaultclock_timestep.open(results_dir + "_array_defaultclock_timestep_144223508", ios::binary | ios::out);
    if(outfile__array_defaultclock_timestep.is_open())
    {
        outfile__array_defaultclock_timestep.write(reinterpret_cast<char*>(_array_defaultclock_timestep), 1*sizeof(_array_defaultclock_timestep[0]));
        outfile__array_defaultclock_timestep.close();
    } else
    {
        std::cout << "Error writing output file for _array_defaultclock_timestep." << endl;
    }
    ofstream outfile__array_glob_inh2pool_N;
    outfile__array_glob_inh2pool_N.open(results_dir + "_array_glob_inh2pool_N_3409106425", ios::binary | ios::out);
    if(outfile__array_glob_inh2pool_N.is_open())
    {
        outfile__array_glob_inh2pool_N.write(reinterpret_cast<char*>(_array_glob_inh2pool_N), 1*sizeof(_array_glob_inh2pool_N[0]));
        outfile__array_glob_inh2pool_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh2pool_N." << endl;
    }
    ofstream outfile__array_glob_inh_neuron__spikespace;
    outfile__array_glob_inh_neuron__spikespace.open(results_dir + "_array_glob_inh_neuron__spikespace_3377271825", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron__spikespace.is_open())
    {
        outfile__array_glob_inh_neuron__spikespace.write(reinterpret_cast<char*>(_array_glob_inh_neuron__spikespace), 2*sizeof(_array_glob_inh_neuron__spikespace[0]));
        outfile__array_glob_inh_neuron__spikespace.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron__spikespace." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_i;
    outfile__array_glob_inh_neuron_i.open(results_dir + "_array_glob_inh_neuron_i_2932183550", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_i.is_open())
    {
        outfile__array_glob_inh_neuron_i.write(reinterpret_cast<char*>(_array_glob_inh_neuron_i), 1*sizeof(_array_glob_inh_neuron_i[0]));
        outfile__array_glob_inh_neuron_i.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_i." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_I_ext;
    outfile__array_glob_inh_neuron_I_ext.open(results_dir + "_array_glob_inh_neuron_I_ext_2431827531", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_I_ext.is_open())
    {
        outfile__array_glob_inh_neuron_I_ext.write(reinterpret_cast<char*>(_array_glob_inh_neuron_I_ext), 1*sizeof(_array_glob_inh_neuron_I_ext[0]));
        outfile__array_glob_inh_neuron_I_ext.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_I_ext." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_I_syn;
    outfile__array_glob_inh_neuron_I_syn.open(results_dir + "_array_glob_inh_neuron_I_syn_1814079922", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_I_syn.is_open())
    {
        outfile__array_glob_inh_neuron_I_syn.write(reinterpret_cast<char*>(_array_glob_inh_neuron_I_syn), 1*sizeof(_array_glob_inh_neuron_I_syn[0]));
        outfile__array_glob_inh_neuron_I_syn.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_I_syn." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_I_vel;
    outfile__array_glob_inh_neuron_I_vel.open(results_dir + "_array_glob_inh_neuron_I_vel_1653757736", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_I_vel.is_open())
    {
        outfile__array_glob_inh_neuron_I_vel.write(reinterpret_cast<char*>(_array_glob_inh_neuron_I_vel), 1*sizeof(_array_glob_inh_neuron_I_vel[0]));
        outfile__array_glob_inh_neuron_I_vel.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_I_vel." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_lastspike;
    outfile__array_glob_inh_neuron_lastspike.open(results_dir + "_array_glob_inh_neuron_lastspike_2050066421", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_lastspike.is_open())
    {
        outfile__array_glob_inh_neuron_lastspike.write(reinterpret_cast<char*>(_array_glob_inh_neuron_lastspike), 1*sizeof(_array_glob_inh_neuron_lastspike[0]));
        outfile__array_glob_inh_neuron_lastspike.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_lastspike." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_not_refractory;
    outfile__array_glob_inh_neuron_not_refractory.open(results_dir + "_array_glob_inh_neuron_not_refractory_4166652008", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_not_refractory.is_open())
    {
        outfile__array_glob_inh_neuron_not_refractory.write(reinterpret_cast<char*>(_array_glob_inh_neuron_not_refractory), 1*sizeof(_array_glob_inh_neuron_not_refractory[0]));
        outfile__array_glob_inh_neuron_not_refractory.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_not_refractory." << endl;
    }
    ofstream outfile__array_glob_inh_neuron_V;
    outfile__array_glob_inh_neuron_V.open(results_dir + "_array_glob_inh_neuron_V_413383875", ios::binary | ios::out);
    if(outfile__array_glob_inh_neuron_V.is_open())
    {
        outfile__array_glob_inh_neuron_V.write(reinterpret_cast<char*>(_array_glob_inh_neuron_V), 1*sizeof(_array_glob_inh_neuron_V[0]));
        outfile__array_glob_inh_neuron_V.close();
    } else
    {
        std::cout << "Error writing output file for _array_glob_inh_neuron_V." << endl;
    }
    ofstream outfile__array_pool2glob_inh_N;
    outfile__array_pool2glob_inh_N.open(results_dir + "_array_pool2glob_inh_N_3311476023", ios::binary | ios::out);
    if(outfile__array_pool2glob_inh_N.is_open())
    {
        outfile__array_pool2glob_inh_N.write(reinterpret_cast<char*>(_array_pool2glob_inh_N), 1*sizeof(_array_pool2glob_inh_N[0]));
        outfile__array_pool2glob_inh_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_pool2glob_inh_N." << endl;
    }
    ofstream outfile__array_ring_neurons__spikespace;
    outfile__array_ring_neurons__spikespace.open(results_dir + "_array_ring_neurons__spikespace_2153503777", ios::binary | ios::out);
    if(outfile__array_ring_neurons__spikespace.is_open())
    {
        outfile__array_ring_neurons__spikespace.write(reinterpret_cast<char*>(_array_ring_neurons__spikespace), 121*sizeof(_array_ring_neurons__spikespace[0]));
        outfile__array_ring_neurons__spikespace.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons__spikespace." << endl;
    }
    ofstream outfile__array_ring_neurons_i;
    outfile__array_ring_neurons_i.open(results_dir + "_array_ring_neurons_i_226185105", ios::binary | ios::out);
    if(outfile__array_ring_neurons_i.is_open())
    {
        outfile__array_ring_neurons_i.write(reinterpret_cast<char*>(_array_ring_neurons_i), 120*sizeof(_array_ring_neurons_i[0]));
        outfile__array_ring_neurons_i.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_i." << endl;
    }
    ofstream outfile__array_ring_neurons_I_ext;
    outfile__array_ring_neurons_I_ext.open(results_dir + "_array_ring_neurons_I_ext_1094266944", ios::binary | ios::out);
    if(outfile__array_ring_neurons_I_ext.is_open())
    {
        outfile__array_ring_neurons_I_ext.write(reinterpret_cast<char*>(_array_ring_neurons_I_ext), 120*sizeof(_array_ring_neurons_I_ext[0]));
        outfile__array_ring_neurons_I_ext.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_I_ext." << endl;
    }
    ofstream outfile__array_ring_neurons_I_syn;
    outfile__array_ring_neurons_I_syn.open(results_dir + "_array_ring_neurons_I_syn_3186304953", ios::binary | ios::out);
    if(outfile__array_ring_neurons_I_syn.is_open())
    {
        outfile__array_ring_neurons_I_syn.write(reinterpret_cast<char*>(_array_ring_neurons_I_syn), 120*sizeof(_array_ring_neurons_I_syn[0]));
        outfile__array_ring_neurons_I_syn.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_I_syn." << endl;
    }
    ofstream outfile__array_ring_neurons_I_vel;
    outfile__array_ring_neurons_I_vel.open(results_dir + "_array_ring_neurons_I_vel_3009009955", ios::binary | ios::out);
    if(outfile__array_ring_neurons_I_vel.is_open())
    {
        outfile__array_ring_neurons_I_vel.write(reinterpret_cast<char*>(_array_ring_neurons_I_vel), 120*sizeof(_array_ring_neurons_I_vel[0]));
        outfile__array_ring_neurons_I_vel.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_I_vel." << endl;
    }
    ofstream outfile__array_ring_neurons_lastspike;
    outfile__array_ring_neurons_lastspike.open(results_dir + "_array_ring_neurons_lastspike_2671893177", ios::binary | ios::out);
    if(outfile__array_ring_neurons_lastspike.is_open())
    {
        outfile__array_ring_neurons_lastspike.write(reinterpret_cast<char*>(_array_ring_neurons_lastspike), 120*sizeof(_array_ring_neurons_lastspike[0]));
        outfile__array_ring_neurons_lastspike.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_lastspike." << endl;
    }
    ofstream outfile__array_ring_neurons_not_refractory;
    outfile__array_ring_neurons_not_refractory.open(results_dir + "_array_ring_neurons_not_refractory_734404006", ios::binary | ios::out);
    if(outfile__array_ring_neurons_not_refractory.is_open())
    {
        outfile__array_ring_neurons_not_refractory.write(reinterpret_cast<char*>(_array_ring_neurons_not_refractory), 120*sizeof(_array_ring_neurons_not_refractory[0]));
        outfile__array_ring_neurons_not_refractory.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_not_refractory." << endl;
    }
    ofstream outfile__array_ring_neurons_run_regularly_clock_dt;
    outfile__array_ring_neurons_run_regularly_clock_dt.open(results_dir + "_array_ring_neurons_run_regularly_clock_dt_2061134363", ios::binary | ios::out);
    if(outfile__array_ring_neurons_run_regularly_clock_dt.is_open())
    {
        outfile__array_ring_neurons_run_regularly_clock_dt.write(reinterpret_cast<char*>(_array_ring_neurons_run_regularly_clock_dt), 1*sizeof(_array_ring_neurons_run_regularly_clock_dt[0]));
        outfile__array_ring_neurons_run_regularly_clock_dt.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_run_regularly_clock_dt." << endl;
    }
    ofstream outfile__array_ring_neurons_run_regularly_clock_t;
    outfile__array_ring_neurons_run_regularly_clock_t.open(results_dir + "_array_ring_neurons_run_regularly_clock_t_2733495229", ios::binary | ios::out);
    if(outfile__array_ring_neurons_run_regularly_clock_t.is_open())
    {
        outfile__array_ring_neurons_run_regularly_clock_t.write(reinterpret_cast<char*>(_array_ring_neurons_run_regularly_clock_t), 1*sizeof(_array_ring_neurons_run_regularly_clock_t[0]));
        outfile__array_ring_neurons_run_regularly_clock_t.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_run_regularly_clock_t." << endl;
    }
    ofstream outfile__array_ring_neurons_run_regularly_clock_timestep;
    outfile__array_ring_neurons_run_regularly_clock_timestep.open(results_dir + "_array_ring_neurons_run_regularly_clock_timestep_3861479888", ios::binary | ios::out);
    if(outfile__array_ring_neurons_run_regularly_clock_timestep.is_open())
    {
        outfile__array_ring_neurons_run_regularly_clock_timestep.write(reinterpret_cast<char*>(_array_ring_neurons_run_regularly_clock_timestep), 1*sizeof(_array_ring_neurons_run_regularly_clock_timestep[0]));
        outfile__array_ring_neurons_run_regularly_clock_timestep.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_run_regularly_clock_timestep." << endl;
    }
    ofstream outfile__array_ring_neurons_V;
    outfile__array_ring_neurons_V.open(results_dir + "_array_ring_neurons_V_3139265196", ios::binary | ios::out);
    if(outfile__array_ring_neurons_V.is_open())
    {
        outfile__array_ring_neurons_V.write(reinterpret_cast<char*>(_array_ring_neurons_V), 120*sizeof(_array_ring_neurons_V[0]));
        outfile__array_ring_neurons_V.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_neurons_V." << endl;
    }
    ofstream outfile__array_ring_synapses_asym_N;
    outfile__array_ring_synapses_asym_N.open(results_dir + "_array_ring_synapses_asym_N_127222578", ios::binary | ios::out);
    if(outfile__array_ring_synapses_asym_N.is_open())
    {
        outfile__array_ring_synapses_asym_N.write(reinterpret_cast<char*>(_array_ring_synapses_asym_N), 1*sizeof(_array_ring_synapses_asym_N[0]));
        outfile__array_ring_synapses_asym_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_synapses_asym_N." << endl;
    }
    ofstream outfile__array_ring_synapses_asym_vel_in;
    outfile__array_ring_synapses_asym_vel_in.open(results_dir + "_array_ring_synapses_asym_vel_in_2435172238", ios::binary | ios::out);
    if(outfile__array_ring_synapses_asym_vel_in.is_open())
    {
        outfile__array_ring_synapses_asym_vel_in.write(reinterpret_cast<char*>(_array_ring_synapses_asym_vel_in), 1*sizeof(_array_ring_synapses_asym_vel_in[0]));
        outfile__array_ring_synapses_asym_vel_in.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_synapses_asym_vel_in." << endl;
    }
    ofstream outfile__array_ring_synapses_N;
    outfile__array_ring_synapses_N.open(results_dir + "_array_ring_synapses_N_2364116571", ios::binary | ios::out);
    if(outfile__array_ring_synapses_N.is_open())
    {
        outfile__array_ring_synapses_N.write(reinterpret_cast<char*>(_array_ring_synapses_N), 1*sizeof(_array_ring_synapses_N[0]));
        outfile__array_ring_synapses_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_ring_synapses_N." << endl;
    }
    ofstream outfile__array_spikemonitor_1__source_idx;
    outfile__array_spikemonitor_1__source_idx.open(results_dir + "_array_spikemonitor_1__source_idx_3609292218", ios::binary | ios::out);
    if(outfile__array_spikemonitor_1__source_idx.is_open())
    {
        outfile__array_spikemonitor_1__source_idx.write(reinterpret_cast<char*>(_array_spikemonitor_1__source_idx), 1*sizeof(_array_spikemonitor_1__source_idx[0]));
        outfile__array_spikemonitor_1__source_idx.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor_1__source_idx." << endl;
    }
    ofstream outfile__array_spikemonitor_1_count;
    outfile__array_spikemonitor_1_count.open(results_dir + "_array_spikemonitor_1_count_3862916462", ios::binary | ios::out);
    if(outfile__array_spikemonitor_1_count.is_open())
    {
        outfile__array_spikemonitor_1_count.write(reinterpret_cast<char*>(_array_spikemonitor_1_count), 1*sizeof(_array_spikemonitor_1_count[0]));
        outfile__array_spikemonitor_1_count.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor_1_count." << endl;
    }
    ofstream outfile__array_spikemonitor_1_N;
    outfile__array_spikemonitor_1_N.open(results_dir + "_array_spikemonitor_1_N_2390248205", ios::binary | ios::out);
    if(outfile__array_spikemonitor_1_N.is_open())
    {
        outfile__array_spikemonitor_1_N.write(reinterpret_cast<char*>(_array_spikemonitor_1_N), 1*sizeof(_array_spikemonitor_1_N[0]));
        outfile__array_spikemonitor_1_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor_1_N." << endl;
    }
    ofstream outfile__array_spikemonitor__source_idx;
    outfile__array_spikemonitor__source_idx.open(results_dir + "_array_spikemonitor__source_idx_1477951789", ios::binary | ios::out);
    if(outfile__array_spikemonitor__source_idx.is_open())
    {
        outfile__array_spikemonitor__source_idx.write(reinterpret_cast<char*>(_array_spikemonitor__source_idx), 120*sizeof(_array_spikemonitor__source_idx[0]));
        outfile__array_spikemonitor__source_idx.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor__source_idx." << endl;
    }
    ofstream outfile__array_spikemonitor_count;
    outfile__array_spikemonitor_count.open(results_dir + "_array_spikemonitor_count_598337445", ios::binary | ios::out);
    if(outfile__array_spikemonitor_count.is_open())
    {
        outfile__array_spikemonitor_count.write(reinterpret_cast<char*>(_array_spikemonitor_count), 120*sizeof(_array_spikemonitor_count[0]));
        outfile__array_spikemonitor_count.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor_count." << endl;
    }
    ofstream outfile__array_spikemonitor_N;
    outfile__array_spikemonitor_N.open(results_dir + "_array_spikemonitor_N_225734567", ios::binary | ios::out);
    if(outfile__array_spikemonitor_N.is_open())
    {
        outfile__array_spikemonitor_N.write(reinterpret_cast<char*>(_array_spikemonitor_N), 1*sizeof(_array_spikemonitor_N[0]));
        outfile__array_spikemonitor_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_spikemonitor_N." << endl;
    }
    ofstream outfile__array_statemonitor_1__indices;
    outfile__array_statemonitor_1__indices.open(results_dir + "_array_statemonitor_1__indices_2504039125", ios::binary | ios::out);
    if(outfile__array_statemonitor_1__indices.is_open())
    {
        outfile__array_statemonitor_1__indices.write(reinterpret_cast<char*>(_array_statemonitor_1__indices), 120*sizeof(_array_statemonitor_1__indices[0]));
        outfile__array_statemonitor_1__indices.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor_1__indices." << endl;
    }
    ofstream outfile__array_statemonitor_1_N;
    outfile__array_statemonitor_1_N.open(results_dir + "_array_statemonitor_1_N_2754233271", ios::binary | ios::out);
    if(outfile__array_statemonitor_1_N.is_open())
    {
        outfile__array_statemonitor_1_N.write(reinterpret_cast<char*>(_array_statemonitor_1_N), 1*sizeof(_array_statemonitor_1_N[0]));
        outfile__array_statemonitor_1_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor_1_N." << endl;
    }
    ofstream outfile__array_statemonitor_2__indices;
    outfile__array_statemonitor_2__indices.open(results_dir + "_array_statemonitor_2__indices_2121736662", ios::binary | ios::out);
    if(outfile__array_statemonitor_2__indices.is_open())
    {
        outfile__array_statemonitor_2__indices.write(reinterpret_cast<char*>(_array_statemonitor_2__indices), 1*sizeof(_array_statemonitor_2__indices[0]));
        outfile__array_statemonitor_2__indices.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor_2__indices." << endl;
    }
    ofstream outfile__array_statemonitor_2_N;
    outfile__array_statemonitor_2_N.open(results_dir + "_array_statemonitor_2_N_2792160750", ios::binary | ios::out);
    if(outfile__array_statemonitor_2_N.is_open())
    {
        outfile__array_statemonitor_2_N.write(reinterpret_cast<char*>(_array_statemonitor_2_N), 1*sizeof(_array_statemonitor_2_N[0]));
        outfile__array_statemonitor_2_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor_2_N." << endl;
    }
    ofstream outfile__array_statemonitor__indices;
    outfile__array_statemonitor__indices.open(results_dir + "_array_statemonitor__indices_2854283999", ios::binary | ios::out);
    if(outfile__array_statemonitor__indices.is_open())
    {
        outfile__array_statemonitor__indices.write(reinterpret_cast<char*>(_array_statemonitor__indices), 120*sizeof(_array_statemonitor__indices[0]));
        outfile__array_statemonitor__indices.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor__indices." << endl;
    }
    ofstream outfile__array_statemonitor_N;
    outfile__array_statemonitor_N.open(results_dir + "_array_statemonitor_N_4140778434", ios::binary | ios::out);
    if(outfile__array_statemonitor_N.is_open())
    {
        outfile__array_statemonitor_N.write(reinterpret_cast<char*>(_array_statemonitor_N), 1*sizeof(_array_statemonitor_N[0]));
        outfile__array_statemonitor_N.close();
    } else
    {
        std::cout << "Error writing output file for _array_statemonitor_N." << endl;
    }

    ofstream outfile__dynamic_array_glob_inh2pool__synaptic_post;
    outfile__dynamic_array_glob_inh2pool__synaptic_post.open(results_dir + "_dynamic_array_glob_inh2pool__synaptic_post_4203706731", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool__synaptic_post.is_open())
    {
        if (! _dynamic_array_glob_inh2pool__synaptic_post.empty() )
        {
            outfile__dynamic_array_glob_inh2pool__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool__synaptic_post[0]), _dynamic_array_glob_inh2pool__synaptic_post.size()*sizeof(_dynamic_array_glob_inh2pool__synaptic_post[0]));
            outfile__dynamic_array_glob_inh2pool__synaptic_post.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool__synaptic_post." << endl;
    }
    ofstream outfile__dynamic_array_glob_inh2pool__synaptic_pre;
    outfile__dynamic_array_glob_inh2pool__synaptic_pre.open(results_dir + "_dynamic_array_glob_inh2pool__synaptic_pre_2224464129", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool__synaptic_pre.is_open())
    {
        if (! _dynamic_array_glob_inh2pool__synaptic_pre.empty() )
        {
            outfile__dynamic_array_glob_inh2pool__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool__synaptic_pre[0]), _dynamic_array_glob_inh2pool__synaptic_pre.size()*sizeof(_dynamic_array_glob_inh2pool__synaptic_pre[0]));
            outfile__dynamic_array_glob_inh2pool__synaptic_pre.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool__synaptic_pre." << endl;
    }
    ofstream outfile__dynamic_array_glob_inh2pool_delay;
    outfile__dynamic_array_glob_inh2pool_delay.open(results_dir + "_dynamic_array_glob_inh2pool_delay_738209", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool_delay.is_open())
    {
        if (! _dynamic_array_glob_inh2pool_delay.empty() )
        {
            outfile__dynamic_array_glob_inh2pool_delay.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool_delay[0]), _dynamic_array_glob_inh2pool_delay.size()*sizeof(_dynamic_array_glob_inh2pool_delay[0]));
            outfile__dynamic_array_glob_inh2pool_delay.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool_delay." << endl;
    }
    ofstream outfile__dynamic_array_glob_inh2pool_N_incoming;
    outfile__dynamic_array_glob_inh2pool_N_incoming.open(results_dir + "_dynamic_array_glob_inh2pool_N_incoming_1284788755", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool_N_incoming.is_open())
    {
        if (! _dynamic_array_glob_inh2pool_N_incoming.empty() )
        {
            outfile__dynamic_array_glob_inh2pool_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool_N_incoming[0]), _dynamic_array_glob_inh2pool_N_incoming.size()*sizeof(_dynamic_array_glob_inh2pool_N_incoming[0]));
            outfile__dynamic_array_glob_inh2pool_N_incoming.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool_N_incoming." << endl;
    }
    ofstream outfile__dynamic_array_glob_inh2pool_N_outgoing;
    outfile__dynamic_array_glob_inh2pool_N_outgoing.open(results_dir + "_dynamic_array_glob_inh2pool_N_outgoing_1804083913", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool_N_outgoing.is_open())
    {
        if (! _dynamic_array_glob_inh2pool_N_outgoing.empty() )
        {
            outfile__dynamic_array_glob_inh2pool_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool_N_outgoing[0]), _dynamic_array_glob_inh2pool_N_outgoing.size()*sizeof(_dynamic_array_glob_inh2pool_N_outgoing[0]));
            outfile__dynamic_array_glob_inh2pool_N_outgoing.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool_N_outgoing." << endl;
    }
    ofstream outfile__dynamic_array_glob_inh2pool_w_inh;
    outfile__dynamic_array_glob_inh2pool_w_inh.open(results_dir + "_dynamic_array_glob_inh2pool_w_inh_1396590816", ios::binary | ios::out);
    if(outfile__dynamic_array_glob_inh2pool_w_inh.is_open())
    {
        if (! _dynamic_array_glob_inh2pool_w_inh.empty() )
        {
            outfile__dynamic_array_glob_inh2pool_w_inh.write(reinterpret_cast<char*>(&_dynamic_array_glob_inh2pool_w_inh[0]), _dynamic_array_glob_inh2pool_w_inh.size()*sizeof(_dynamic_array_glob_inh2pool_w_inh[0]));
            outfile__dynamic_array_glob_inh2pool_w_inh.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_glob_inh2pool_w_inh." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh__synaptic_post;
    outfile__dynamic_array_pool2glob_inh__synaptic_post.open(results_dir + "_dynamic_array_pool2glob_inh__synaptic_post_3031688223", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh__synaptic_post.is_open())
    {
        if (! _dynamic_array_pool2glob_inh__synaptic_post.empty() )
        {
            outfile__dynamic_array_pool2glob_inh__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh__synaptic_post[0]), _dynamic_array_pool2glob_inh__synaptic_post.size()*sizeof(_dynamic_array_pool2glob_inh__synaptic_post[0]));
            outfile__dynamic_array_pool2glob_inh__synaptic_post.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh__synaptic_post." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh__synaptic_pre;
    outfile__dynamic_array_pool2glob_inh__synaptic_pre.open(results_dir + "_dynamic_array_pool2glob_inh__synaptic_pre_3163062755", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh__synaptic_pre.is_open())
    {
        if (! _dynamic_array_pool2glob_inh__synaptic_pre.empty() )
        {
            outfile__dynamic_array_pool2glob_inh__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh__synaptic_pre[0]), _dynamic_array_pool2glob_inh__synaptic_pre.size()*sizeof(_dynamic_array_pool2glob_inh__synaptic_pre[0]));
            outfile__dynamic_array_pool2glob_inh__synaptic_pre.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh__synaptic_pre." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh_delay;
    outfile__dynamic_array_pool2glob_inh_delay.open(results_dir + "_dynamic_array_pool2glob_inh_delay_2131443452", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh_delay.is_open())
    {
        if (! _dynamic_array_pool2glob_inh_delay.empty() )
        {
            outfile__dynamic_array_pool2glob_inh_delay.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh_delay[0]), _dynamic_array_pool2glob_inh_delay.size()*sizeof(_dynamic_array_pool2glob_inh_delay[0]));
            outfile__dynamic_array_pool2glob_inh_delay.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh_delay." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh_N_incoming;
    outfile__dynamic_array_pool2glob_inh_N_incoming.open(results_dir + "_dynamic_array_pool2glob_inh_N_incoming_3185918993", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh_N_incoming.is_open())
    {
        if (! _dynamic_array_pool2glob_inh_N_incoming.empty() )
        {
            outfile__dynamic_array_pool2glob_inh_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh_N_incoming[0]), _dynamic_array_pool2glob_inh_N_incoming.size()*sizeof(_dynamic_array_pool2glob_inh_N_incoming[0]));
            outfile__dynamic_array_pool2glob_inh_N_incoming.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh_N_incoming." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh_N_outgoing;
    outfile__dynamic_array_pool2glob_inh_N_outgoing.open(results_dir + "_dynamic_array_pool2glob_inh_N_outgoing_2600023243", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh_N_outgoing.is_open())
    {
        if (! _dynamic_array_pool2glob_inh_N_outgoing.empty() )
        {
            outfile__dynamic_array_pool2glob_inh_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh_N_outgoing[0]), _dynamic_array_pool2glob_inh_N_outgoing.size()*sizeof(_dynamic_array_pool2glob_inh_N_outgoing[0]));
            outfile__dynamic_array_pool2glob_inh_N_outgoing.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh_N_outgoing." << endl;
    }
    ofstream outfile__dynamic_array_pool2glob_inh_w_exc;
    outfile__dynamic_array_pool2glob_inh_w_exc.open(results_dir + "_dynamic_array_pool2glob_inh_w_exc_2926485638", ios::binary | ios::out);
    if(outfile__dynamic_array_pool2glob_inh_w_exc.is_open())
    {
        if (! _dynamic_array_pool2glob_inh_w_exc.empty() )
        {
            outfile__dynamic_array_pool2glob_inh_w_exc.write(reinterpret_cast<char*>(&_dynamic_array_pool2glob_inh_w_exc[0]), _dynamic_array_pool2glob_inh_w_exc.size()*sizeof(_dynamic_array_pool2glob_inh_w_exc[0]));
            outfile__dynamic_array_pool2glob_inh_w_exc.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_pool2glob_inh_w_exc." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses__synaptic_post;
    outfile__dynamic_array_ring_synapses__synaptic_post.open(results_dir + "_dynamic_array_ring_synapses__synaptic_post_2486579174", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses__synaptic_post.is_open())
    {
        if (! _dynamic_array_ring_synapses__synaptic_post.empty() )
        {
            outfile__dynamic_array_ring_synapses__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses__synaptic_post[0]), _dynamic_array_ring_synapses__synaptic_post.size()*sizeof(_dynamic_array_ring_synapses__synaptic_post[0]));
            outfile__dynamic_array_ring_synapses__synaptic_post.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses__synaptic_post." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses__synaptic_pre;
    outfile__dynamic_array_ring_synapses__synaptic_pre.open(results_dir + "_dynamic_array_ring_synapses__synaptic_pre_1455868822", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses__synaptic_pre.is_open())
    {
        if (! _dynamic_array_ring_synapses__synaptic_pre.empty() )
        {
            outfile__dynamic_array_ring_synapses__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses__synaptic_pre[0]), _dynamic_array_ring_synapses__synaptic_pre.size()*sizeof(_dynamic_array_ring_synapses__synaptic_pre[0]));
            outfile__dynamic_array_ring_synapses__synaptic_pre.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses__synaptic_pre." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym__synaptic_post;
    outfile__dynamic_array_ring_synapses_asym__synaptic_post.open(results_dir + "_dynamic_array_ring_synapses_asym__synaptic_post_1872696763", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym__synaptic_post.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym__synaptic_post.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym__synaptic_post[0]), _dynamic_array_ring_synapses_asym__synaptic_post.size()*sizeof(_dynamic_array_ring_synapses_asym__synaptic_post[0]));
            outfile__dynamic_array_ring_synapses_asym__synaptic_post.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym__synaptic_post." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym__synaptic_pre;
    outfile__dynamic_array_ring_synapses_asym__synaptic_pre.open(results_dir + "_dynamic_array_ring_synapses_asym__synaptic_pre_733017033", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym__synaptic_pre.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym__synaptic_pre.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym__synaptic_pre[0]), _dynamic_array_ring_synapses_asym__synaptic_pre.size()*sizeof(_dynamic_array_ring_synapses_asym__synaptic_pre[0]));
            outfile__dynamic_array_ring_synapses_asym__synaptic_pre.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym__synaptic_pre." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym_delay;
    outfile__dynamic_array_ring_synapses_asym_delay.open(results_dir + "_dynamic_array_ring_synapses_asym_delay_408110513", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym_delay.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym_delay.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym_delay.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym_delay[0]), _dynamic_array_ring_synapses_asym_delay.size()*sizeof(_dynamic_array_ring_synapses_asym_delay[0]));
            outfile__dynamic_array_ring_synapses_asym_delay.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym_delay." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym_N_incoming;
    outfile__dynamic_array_ring_synapses_asym_N_incoming.open(results_dir + "_dynamic_array_ring_synapses_asym_N_incoming_3920330012", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym_N_incoming.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym_N_incoming.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym_N_incoming[0]), _dynamic_array_ring_synapses_asym_N_incoming.size()*sizeof(_dynamic_array_ring_synapses_asym_N_incoming[0]));
            outfile__dynamic_array_ring_synapses_asym_N_incoming.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym_N_incoming." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym_N_outgoing;
    outfile__dynamic_array_ring_synapses_asym_N_outgoing.open(results_dir + "_dynamic_array_ring_synapses_asym_N_outgoing_3468103110", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym_N_outgoing.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym_N_outgoing.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym_N_outgoing[0]), _dynamic_array_ring_synapses_asym_N_outgoing.size()*sizeof(_dynamic_array_ring_synapses_asym_N_outgoing[0]));
            outfile__dynamic_array_ring_synapses_asym_N_outgoing.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym_N_outgoing." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_asym_w_asym;
    outfile__dynamic_array_ring_synapses_asym_w_asym.open(results_dir + "_dynamic_array_ring_synapses_asym_w_asym_3731119590", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_asym_w_asym.is_open())
    {
        if (! _dynamic_array_ring_synapses_asym_w_asym.empty() )
        {
            outfile__dynamic_array_ring_synapses_asym_w_asym.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_asym_w_asym[0]), _dynamic_array_ring_synapses_asym_w_asym.size()*sizeof(_dynamic_array_ring_synapses_asym_w_asym[0]));
            outfile__dynamic_array_ring_synapses_asym_w_asym.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_asym_w_asym." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_delay;
    outfile__dynamic_array_ring_synapses_delay.open(results_dir + "_dynamic_array_ring_synapses_delay_234134425", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_delay.is_open())
    {
        if (! _dynamic_array_ring_synapses_delay.empty() )
        {
            outfile__dynamic_array_ring_synapses_delay.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_delay[0]), _dynamic_array_ring_synapses_delay.size()*sizeof(_dynamic_array_ring_synapses_delay[0]));
            outfile__dynamic_array_ring_synapses_delay.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_delay." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_N_incoming;
    outfile__dynamic_array_ring_synapses_N_incoming.open(results_dir + "_dynamic_array_ring_synapses_N_incoming_890468994", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_N_incoming.is_open())
    {
        if (! _dynamic_array_ring_synapses_N_incoming.empty() )
        {
            outfile__dynamic_array_ring_synapses_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_N_incoming[0]), _dynamic_array_ring_synapses_N_incoming.size()*sizeof(_dynamic_array_ring_synapses_N_incoming[0]));
            outfile__dynamic_array_ring_synapses_N_incoming.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_N_incoming." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_N_outgoing;
    outfile__dynamic_array_ring_synapses_N_outgoing.open(results_dir + "_dynamic_array_ring_synapses_N_outgoing_302975576", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_N_outgoing.is_open())
    {
        if (! _dynamic_array_ring_synapses_N_outgoing.empty() )
        {
            outfile__dynamic_array_ring_synapses_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_N_outgoing[0]), _dynamic_array_ring_synapses_N_outgoing.size()*sizeof(_dynamic_array_ring_synapses_N_outgoing[0]));
            outfile__dynamic_array_ring_synapses_N_outgoing.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_N_outgoing." << endl;
    }
    ofstream outfile__dynamic_array_ring_synapses_w;
    outfile__dynamic_array_ring_synapses_w.open(results_dir + "_dynamic_array_ring_synapses_w_1784118959", ios::binary | ios::out);
    if(outfile__dynamic_array_ring_synapses_w.is_open())
    {
        if (! _dynamic_array_ring_synapses_w.empty() )
        {
            outfile__dynamic_array_ring_synapses_w.write(reinterpret_cast<char*>(&_dynamic_array_ring_synapses_w[0]), _dynamic_array_ring_synapses_w.size()*sizeof(_dynamic_array_ring_synapses_w[0]));
            outfile__dynamic_array_ring_synapses_w.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_ring_synapses_w." << endl;
    }
    ofstream outfile__dynamic_array_spikemonitor_1_i;
    outfile__dynamic_array_spikemonitor_1_i.open(results_dir + "_dynamic_array_spikemonitor_1_i_2680224553", ios::binary | ios::out);
    if(outfile__dynamic_array_spikemonitor_1_i.is_open())
    {
        if (! _dynamic_array_spikemonitor_1_i.empty() )
        {
            outfile__dynamic_array_spikemonitor_1_i.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_1_i[0]), _dynamic_array_spikemonitor_1_i.size()*sizeof(_dynamic_array_spikemonitor_1_i[0]));
            outfile__dynamic_array_spikemonitor_1_i.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_spikemonitor_1_i." << endl;
    }
    ofstream outfile__dynamic_array_spikemonitor_1_t;
    outfile__dynamic_array_spikemonitor_1_t.open(results_dir + "_dynamic_array_spikemonitor_1_t_4240873456", ios::binary | ios::out);
    if(outfile__dynamic_array_spikemonitor_1_t.is_open())
    {
        if (! _dynamic_array_spikemonitor_1_t.empty() )
        {
            outfile__dynamic_array_spikemonitor_1_t.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_1_t[0]), _dynamic_array_spikemonitor_1_t.size()*sizeof(_dynamic_array_spikemonitor_1_t[0]));
            outfile__dynamic_array_spikemonitor_1_t.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_spikemonitor_1_t." << endl;
    }
    ofstream outfile__dynamic_array_spikemonitor_i;
    outfile__dynamic_array_spikemonitor_i.open(results_dir + "_dynamic_array_spikemonitor_i_1976709050", ios::binary | ios::out);
    if(outfile__dynamic_array_spikemonitor_i.is_open())
    {
        if (! _dynamic_array_spikemonitor_i.empty() )
        {
            outfile__dynamic_array_spikemonitor_i.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_i[0]), _dynamic_array_spikemonitor_i.size()*sizeof(_dynamic_array_spikemonitor_i[0]));
            outfile__dynamic_array_spikemonitor_i.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_spikemonitor_i." << endl;
    }
    ofstream outfile__dynamic_array_spikemonitor_t;
    outfile__dynamic_array_spikemonitor_t.open(results_dir + "_dynamic_array_spikemonitor_t_383009635", ios::binary | ios::out);
    if(outfile__dynamic_array_spikemonitor_t.is_open())
    {
        if (! _dynamic_array_spikemonitor_t.empty() )
        {
            outfile__dynamic_array_spikemonitor_t.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_t[0]), _dynamic_array_spikemonitor_t.size()*sizeof(_dynamic_array_spikemonitor_t[0]));
            outfile__dynamic_array_spikemonitor_t.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_spikemonitor_t." << endl;
    }
    ofstream outfile__dynamic_array_statemonitor_1_t;
    outfile__dynamic_array_statemonitor_1_t.open(results_dir + "_dynamic_array_statemonitor_1_t_3600064330", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_1_t.is_open())
    {
        if (! _dynamic_array_statemonitor_1_t.empty() )
        {
            outfile__dynamic_array_statemonitor_1_t.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_1_t[0]), _dynamic_array_statemonitor_1_t.size()*sizeof(_dynamic_array_statemonitor_1_t[0]));
            outfile__dynamic_array_statemonitor_1_t.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_1_t." << endl;
    }
    ofstream outfile__dynamic_array_statemonitor_2_t;
    outfile__dynamic_array_statemonitor_2_t.open(results_dir + "_dynamic_array_statemonitor_2_t_3570540819", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_2_t.is_open())
    {
        if (! _dynamic_array_statemonitor_2_t.empty() )
        {
            outfile__dynamic_array_statemonitor_2_t.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_2_t[0]), _dynamic_array_statemonitor_2_t.size()*sizeof(_dynamic_array_statemonitor_2_t[0]));
            outfile__dynamic_array_statemonitor_2_t.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_2_t." << endl;
    }
    ofstream outfile__dynamic_array_statemonitor_t;
    outfile__dynamic_array_statemonitor_t.open(results_dir + "_dynamic_array_statemonitor_t_3983503110", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_t.is_open())
    {
        if (! _dynamic_array_statemonitor_t.empty() )
        {
            outfile__dynamic_array_statemonitor_t.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_t[0]), _dynamic_array_statemonitor_t.size()*sizeof(_dynamic_array_statemonitor_t[0]));
            outfile__dynamic_array_statemonitor_t.close();
        }
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_t." << endl;
    }

    ofstream outfile__dynamic_array_statemonitor_1_I_ext;
    outfile__dynamic_array_statemonitor_1_I_ext.open(results_dir + "_dynamic_array_statemonitor_1_I_ext_1836223652", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_1_I_ext.is_open())
    {
        for (int n=0; n<_dynamic_array_statemonitor_1_I_ext.n; n++)
        {
            if (! _dynamic_array_statemonitor_1_I_ext(n).empty())
            {
                outfile__dynamic_array_statemonitor_1_I_ext.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_1_I_ext(n, 0)), _dynamic_array_statemonitor_1_I_ext.m*sizeof(_dynamic_array_statemonitor_1_I_ext(0, 0)));
            }
        }
        outfile__dynamic_array_statemonitor_1_I_ext.close();
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_1_I_ext." << endl;
    }
    ofstream outfile__dynamic_array_statemonitor_2_V;
    outfile__dynamic_array_statemonitor_2_V.open(results_dir + "_dynamic_array_statemonitor_2_V_28467447", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_2_V.is_open())
    {
        for (int n=0; n<_dynamic_array_statemonitor_2_V.n; n++)
        {
            if (! _dynamic_array_statemonitor_2_V(n).empty())
            {
                outfile__dynamic_array_statemonitor_2_V.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_2_V(n, 0)), _dynamic_array_statemonitor_2_V.m*sizeof(_dynamic_array_statemonitor_2_V(0, 0)));
            }
        }
        outfile__dynamic_array_statemonitor_2_V.close();
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_2_V." << endl;
    }
    ofstream outfile__dynamic_array_statemonitor_V;
    outfile__dynamic_array_statemonitor_V.open(results_dir + "_dynamic_array_statemonitor_V_940519138", ios::binary | ios::out);
    if(outfile__dynamic_array_statemonitor_V.is_open())
    {
        for (int n=0; n<_dynamic_array_statemonitor_V.n; n++)
        {
            if (! _dynamic_array_statemonitor_V(n).empty())
            {
                outfile__dynamic_array_statemonitor_V.write(reinterpret_cast<char*>(&_dynamic_array_statemonitor_V(n, 0)), _dynamic_array_statemonitor_V.m*sizeof(_dynamic_array_statemonitor_V(0, 0)));
            }
        }
        outfile__dynamic_array_statemonitor_V.close();
    } else
    {
        std::cout << "Error writing output file for _dynamic_array_statemonitor_V." << endl;
    }
    // Write last run info to disk
    ofstream outfile_last_run_info;
    outfile_last_run_info.open(results_dir + "last_run_info.txt", ios::out);
    if(outfile_last_run_info.is_open())
    {
        outfile_last_run_info << (Network::_last_run_time) << " " << (Network::_last_run_completed_fraction) << std::endl;
        outfile_last_run_info.close();
    } else
    {
        std::cout << "Error writing last run info to file." << std::endl;
    }
}

void _dealloc_arrays()
{
    using namespace brian;


    // static arrays
    if(_static_array__array_ring_neurons_I_ext!=0)
    {
        delete [] _static_array__array_ring_neurons_I_ext;
        _static_array__array_ring_neurons_I_ext = 0;
    }
    if(_static_array__array_ring_neurons_I_ext_1!=0)
    {
        delete [] _static_array__array_ring_neurons_I_ext_1;
        _static_array__array_ring_neurons_I_ext_1 = 0;
    }
    if(_static_array__array_statemonitor_1__indices!=0)
    {
        delete [] _static_array__array_statemonitor_1__indices;
        _static_array__array_statemonitor_1__indices = 0;
    }
    if(_static_array__array_statemonitor__indices!=0)
    {
        delete [] _static_array__array_statemonitor__indices;
        _static_array__array_statemonitor__indices = 0;
    }
}

