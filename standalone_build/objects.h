
#ifndef _BRIAN_OBJECTS_H
#define _BRIAN_OBJECTS_H

#include "synapses_classes.h"
#include "brianlib/clocks.h"
#include "brianlib/dynamic_array.h"
#include "brianlib/stdint_compat.h"
#include "network.h"
#include<random>
#include<vector>


namespace brian {

extern std::string results_dir;

class RandomGenerator {
    private:
        std::mt19937 gen;
        double stored_gauss;
        bool has_stored_gauss = false;
    public:
        RandomGenerator() {
            seed();
        }
        void seed() {
            std::random_device rd;
            gen.seed(rd());
            has_stored_gauss = false;
        }
        void seed(unsigned long seed) {
            gen.seed(seed);
            has_stored_gauss = false;
        }
        double rand() {
            /* shifts : 67108864 = 0x4000000, 9007199254740992 = 0x20000000000000 */
            const long a = gen() >> 5;
            const long b = gen() >> 6;
            return (a * 67108864.0 + b) / 9007199254740992.0;
        }

        double randn() {
            if (has_stored_gauss) {
                const double tmp = stored_gauss;
                has_stored_gauss = false;
                return tmp;
            }
            else {
                double f, x1, x2, r2;

                do {
                    x1 = 2.0*rand() - 1.0;
                    x2 = 2.0*rand() - 1.0;
                    r2 = x1*x1 + x2*x2;
                }
                while (r2 >= 1.0 || r2 == 0.0);

                /* Box-Muller transform */
                f = sqrt(-2.0*log(r2)/r2);
                /* Keep for next call */
                stored_gauss = f*x1;
                has_stored_gauss = true;
                return f*x2;
            }
        }
};

// In OpenMP we need one state per thread
extern std::vector< RandomGenerator > _random_generators;

//////////////// clocks ///////////////////
extern Clock defaultclock;
extern Clock ring_neurons_run_regularly_clock;

//////////////// networks /////////////////
extern Network network;



void set_variable_by_name(std::string, std::string);

//////////////// dynamic arrays ///////////
extern std::vector<int32_t> _dynamic_array_glob_inh2pool__synaptic_post;
extern std::vector<int32_t> _dynamic_array_glob_inh2pool__synaptic_pre;
extern std::vector<double> _dynamic_array_glob_inh2pool_delay;
extern std::vector<int32_t> _dynamic_array_glob_inh2pool_N_incoming;
extern std::vector<int32_t> _dynamic_array_glob_inh2pool_N_outgoing;
extern std::vector<double> _dynamic_array_glob_inh2pool_w_inh;
extern std::vector<int32_t> _dynamic_array_pool2glob_inh__synaptic_post;
extern std::vector<int32_t> _dynamic_array_pool2glob_inh__synaptic_pre;
extern std::vector<double> _dynamic_array_pool2glob_inh_delay;
extern std::vector<int32_t> _dynamic_array_pool2glob_inh_N_incoming;
extern std::vector<int32_t> _dynamic_array_pool2glob_inh_N_outgoing;
extern std::vector<double> _dynamic_array_pool2glob_inh_w_exc;
extern std::vector<int32_t> _dynamic_array_ring_synapses__synaptic_post;
extern std::vector<int32_t> _dynamic_array_ring_synapses__synaptic_pre;
extern std::vector<int32_t> _dynamic_array_ring_synapses_asym__synaptic_post;
extern std::vector<int32_t> _dynamic_array_ring_synapses_asym__synaptic_pre;
extern std::vector<double> _dynamic_array_ring_synapses_asym_delay;
extern std::vector<int32_t> _dynamic_array_ring_synapses_asym_N_incoming;
extern std::vector<int32_t> _dynamic_array_ring_synapses_asym_N_outgoing;
extern std::vector<double> _dynamic_array_ring_synapses_asym_w_asym;
extern std::vector<double> _dynamic_array_ring_synapses_delay;
extern std::vector<int32_t> _dynamic_array_ring_synapses_N_incoming;
extern std::vector<int32_t> _dynamic_array_ring_synapses_N_outgoing;
extern std::vector<double> _dynamic_array_ring_synapses_w;
extern std::vector<int32_t> _dynamic_array_spikemonitor_1_i;
extern std::vector<double> _dynamic_array_spikemonitor_1_t;
extern std::vector<int32_t> _dynamic_array_spikemonitor_i;
extern std::vector<double> _dynamic_array_spikemonitor_t;
extern std::vector<double> _dynamic_array_statemonitor_1_t;
extern std::vector<double> _dynamic_array_statemonitor_2_t;
extern std::vector<double> _dynamic_array_statemonitor_t;

//////////////// arrays ///////////////////
extern double *_array_defaultclock_dt;
extern const int _num__array_defaultclock_dt;
extern double *_array_defaultclock_t;
extern const int _num__array_defaultclock_t;
extern int64_t *_array_defaultclock_timestep;
extern const int _num__array_defaultclock_timestep;
extern int32_t *_array_glob_inh2pool_N;
extern const int _num__array_glob_inh2pool_N;
extern int32_t *_array_glob_inh_neuron__spikespace;
extern const int _num__array_glob_inh_neuron__spikespace;
extern int32_t *_array_glob_inh_neuron_i;
extern const int _num__array_glob_inh_neuron_i;
extern double *_array_glob_inh_neuron_I_ext;
extern const int _num__array_glob_inh_neuron_I_ext;
extern double *_array_glob_inh_neuron_I_syn;
extern const int _num__array_glob_inh_neuron_I_syn;
extern double *_array_glob_inh_neuron_I_vel;
extern const int _num__array_glob_inh_neuron_I_vel;
extern double *_array_glob_inh_neuron_lastspike;
extern const int _num__array_glob_inh_neuron_lastspike;
extern char *_array_glob_inh_neuron_not_refractory;
extern const int _num__array_glob_inh_neuron_not_refractory;
extern double *_array_glob_inh_neuron_V;
extern const int _num__array_glob_inh_neuron_V;
extern int32_t *_array_pool2glob_inh_N;
extern const int _num__array_pool2glob_inh_N;
extern int32_t *_array_ring_neurons__spikespace;
extern const int _num__array_ring_neurons__spikespace;
extern int32_t *_array_ring_neurons_i;
extern const int _num__array_ring_neurons_i;
extern double *_array_ring_neurons_I_ext;
extern const int _num__array_ring_neurons_I_ext;
extern double *_array_ring_neurons_I_syn;
extern const int _num__array_ring_neurons_I_syn;
extern double *_array_ring_neurons_I_vel;
extern const int _num__array_ring_neurons_I_vel;
extern double *_array_ring_neurons_lastspike;
extern const int _num__array_ring_neurons_lastspike;
extern char *_array_ring_neurons_not_refractory;
extern const int _num__array_ring_neurons_not_refractory;
extern double *_array_ring_neurons_run_regularly_clock_dt;
extern const int _num__array_ring_neurons_run_regularly_clock_dt;
extern double *_array_ring_neurons_run_regularly_clock_t;
extern const int _num__array_ring_neurons_run_regularly_clock_t;
extern int64_t *_array_ring_neurons_run_regularly_clock_timestep;
extern const int _num__array_ring_neurons_run_regularly_clock_timestep;
extern double *_array_ring_neurons_V;
extern const int _num__array_ring_neurons_V;
extern int32_t *_array_ring_synapses_asym_N;
extern const int _num__array_ring_synapses_asym_N;
extern double *_array_ring_synapses_asym_vel_in;
extern const int _num__array_ring_synapses_asym_vel_in;
extern int32_t *_array_ring_synapses_N;
extern const int _num__array_ring_synapses_N;
extern int32_t *_array_spikemonitor_1__source_idx;
extern const int _num__array_spikemonitor_1__source_idx;
extern int32_t *_array_spikemonitor_1_count;
extern const int _num__array_spikemonitor_1_count;
extern int32_t *_array_spikemonitor_1_N;
extern const int _num__array_spikemonitor_1_N;
extern int32_t *_array_spikemonitor__source_idx;
extern const int _num__array_spikemonitor__source_idx;
extern int32_t *_array_spikemonitor_count;
extern const int _num__array_spikemonitor_count;
extern int32_t *_array_spikemonitor_N;
extern const int _num__array_spikemonitor_N;
extern int32_t *_array_statemonitor_1__indices;
extern const int _num__array_statemonitor_1__indices;
extern double *_array_statemonitor_1_I_ext;
extern const int _num__array_statemonitor_1_I_ext;
extern int32_t *_array_statemonitor_1_N;
extern const int _num__array_statemonitor_1_N;
extern int32_t *_array_statemonitor_2__indices;
extern const int _num__array_statemonitor_2__indices;
extern int32_t *_array_statemonitor_2_N;
extern const int _num__array_statemonitor_2_N;
extern double *_array_statemonitor_2_V;
extern const int _num__array_statemonitor_2_V;
extern int32_t *_array_statemonitor__indices;
extern const int _num__array_statemonitor__indices;
extern int32_t *_array_statemonitor_N;
extern const int _num__array_statemonitor_N;
extern double *_array_statemonitor_V;
extern const int _num__array_statemonitor_V;

//////////////// dynamic arrays 2d /////////
extern DynamicArray2D<double> _dynamic_array_statemonitor_1_I_ext;
extern DynamicArray2D<double> _dynamic_array_statemonitor_2_V;
extern DynamicArray2D<double> _dynamic_array_statemonitor_V;

/////////////// static arrays /////////////
extern double *_static_array__array_ring_neurons_I_ext;
extern const int _num__static_array__array_ring_neurons_I_ext;
extern double *_static_array__array_ring_neurons_I_ext_1;
extern const int _num__static_array__array_ring_neurons_I_ext_1;
extern int32_t *_static_array__array_statemonitor_1__indices;
extern const int _num__static_array__array_statemonitor_1__indices;
extern int32_t *_static_array__array_statemonitor__indices;
extern const int _num__static_array__array_statemonitor__indices;

//////////////// synapses /////////////////
// glob_inh2pool
extern SynapticPathway glob_inh2pool_pre;
// pool2glob_inh
extern SynapticPathway pool2glob_inh_pre;
// ring_synapses
extern SynapticPathway ring_synapses_pre;
// ring_synapses_asym
extern SynapticPathway ring_synapses_asym_pre;

// Profiling information for each code object
}

void _init_arrays();
void _load_arrays();
void _write_arrays();
void _dealloc_arrays();

#endif


