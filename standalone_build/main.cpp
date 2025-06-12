#include <stdlib.h>
#include "objects.h"
#include <ctime>
#include <time.h>

#include "run.h"
#include "brianlib/common_math.h"

#include "code_objects/glob_inh2pool_pre_codeobject.h"
#include "code_objects/glob_inh2pool_pre_codeobject_1.h"
#include "code_objects/glob_inh2pool_pre_codeobject_2.h"
#include "code_objects/glob_inh2pool_pre_codeobject_3.h"
#include "code_objects/glob_inh2pool_pre_push_spikes.h"
#include "code_objects/before_run_glob_inh2pool_pre_push_spikes.h"
#include "code_objects/before_run_glob_inh2pool_pre_push_spikes.h"
#include "code_objects/before_run_glob_inh2pool_pre_push_spikes.h"
#include "code_objects/before_run_glob_inh2pool_pre_push_spikes.h"
#include "code_objects/glob_inh2pool_synapses_create_generator_codeobject.h"
#include "code_objects/glob_inh_neuron_spike_resetter_codeobject.h"
#include "code_objects/glob_inh_neuron_spike_resetter_codeobject_1.h"
#include "code_objects/glob_inh_neuron_spike_resetter_codeobject_2.h"
#include "code_objects/glob_inh_neuron_spike_resetter_codeobject_3.h"
#include "code_objects/glob_inh_neuron_spike_thresholder_codeobject.h"
#include "code_objects/after_run_glob_inh_neuron_spike_thresholder_codeobject.h"
#include "code_objects/glob_inh_neuron_spike_thresholder_codeobject_1.h"
#include "code_objects/after_run_glob_inh_neuron_spike_thresholder_codeobject_1.h"
#include "code_objects/glob_inh_neuron_spike_thresholder_codeobject_2.h"
#include "code_objects/after_run_glob_inh_neuron_spike_thresholder_codeobject_2.h"
#include "code_objects/glob_inh_neuron_spike_thresholder_codeobject_3.h"
#include "code_objects/after_run_glob_inh_neuron_spike_thresholder_codeobject_3.h"
#include "code_objects/glob_inh_neuron_stateupdater_codeobject.h"
#include "code_objects/glob_inh_neuron_stateupdater_codeobject_1.h"
#include "code_objects/glob_inh_neuron_stateupdater_codeobject_2.h"
#include "code_objects/glob_inh_neuron_stateupdater_codeobject_3.h"
#include "code_objects/pool2glob_inh_pre_codeobject.h"
#include "code_objects/pool2glob_inh_pre_codeobject_1.h"
#include "code_objects/pool2glob_inh_pre_codeobject_2.h"
#include "code_objects/pool2glob_inh_pre_codeobject_3.h"
#include "code_objects/pool2glob_inh_pre_push_spikes.h"
#include "code_objects/before_run_pool2glob_inh_pre_push_spikes.h"
#include "code_objects/before_run_pool2glob_inh_pre_push_spikes.h"
#include "code_objects/before_run_pool2glob_inh_pre_push_spikes.h"
#include "code_objects/before_run_pool2glob_inh_pre_push_spikes.h"
#include "code_objects/pool2glob_inh_synapses_create_generator_codeobject.h"
#include "code_objects/ring_neurons_run_regularly_codeobject.h"
#include "code_objects/ring_neurons_run_regularly_codeobject_1.h"
#include "code_objects/ring_neurons_run_regularly_codeobject_2.h"
#include "code_objects/ring_neurons_run_regularly_codeobject_3.h"
#include "code_objects/ring_neurons_spike_resetter_codeobject.h"
#include "code_objects/ring_neurons_spike_resetter_codeobject_1.h"
#include "code_objects/ring_neurons_spike_resetter_codeobject_2.h"
#include "code_objects/ring_neurons_spike_resetter_codeobject_3.h"
#include "code_objects/ring_neurons_spike_thresholder_codeobject.h"
#include "code_objects/after_run_ring_neurons_spike_thresholder_codeobject.h"
#include "code_objects/ring_neurons_spike_thresholder_codeobject_1.h"
#include "code_objects/after_run_ring_neurons_spike_thresholder_codeobject_1.h"
#include "code_objects/ring_neurons_spike_thresholder_codeobject_2.h"
#include "code_objects/after_run_ring_neurons_spike_thresholder_codeobject_2.h"
#include "code_objects/ring_neurons_spike_thresholder_codeobject_3.h"
#include "code_objects/after_run_ring_neurons_spike_thresholder_codeobject_3.h"
#include "code_objects/ring_neurons_stateupdater_codeobject.h"
#include "code_objects/ring_neurons_stateupdater_codeobject_1.h"
#include "code_objects/ring_neurons_stateupdater_codeobject_2.h"
#include "code_objects/ring_neurons_stateupdater_codeobject_3.h"
#include "code_objects/ring_synapses_asym_group_variable_set_conditional_codeobject.h"
#include "code_objects/ring_synapses_asym_pre_codeobject.h"
#include "code_objects/ring_synapses_asym_pre_codeobject_1.h"
#include "code_objects/ring_synapses_asym_pre_codeobject_2.h"
#include "code_objects/ring_synapses_asym_pre_codeobject_3.h"
#include "code_objects/ring_synapses_asym_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_asym_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_asym_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_asym_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_asym_pre_push_spikes.h"
#include "code_objects/ring_synapses_asym_synapses_create_generator_codeobject.h"
#include "code_objects/ring_synapses_group_variable_set_conditional_codeobject.h"
#include "code_objects/ring_synapses_pre_codeobject.h"
#include "code_objects/ring_synapses_pre_codeobject_1.h"
#include "code_objects/ring_synapses_pre_codeobject_2.h"
#include "code_objects/ring_synapses_pre_codeobject_3.h"
#include "code_objects/ring_synapses_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_pre_push_spikes.h"
#include "code_objects/before_run_ring_synapses_pre_push_spikes.h"
#include "code_objects/ring_synapses_synapses_create_generator_codeobject.h"
#include "code_objects/spikemonitor_1_codeobject.h"
#include "code_objects/spikemonitor_1_codeobject_1.h"
#include "code_objects/spikemonitor_1_codeobject_2.h"
#include "code_objects/spikemonitor_1_codeobject_3.h"
#include "code_objects/spikemonitor_codeobject.h"
#include "code_objects/spikemonitor_codeobject_1.h"
#include "code_objects/spikemonitor_codeobject_2.h"
#include "code_objects/spikemonitor_codeobject_3.h"
#include "code_objects/statemonitor_1_codeobject.h"
#include "code_objects/statemonitor_1_codeobject_1.h"
#include "code_objects/statemonitor_1_codeobject_2.h"
#include "code_objects/statemonitor_1_codeobject_3.h"
#include "code_objects/statemonitor_2_codeobject.h"
#include "code_objects/statemonitor_2_codeobject_1.h"
#include "code_objects/statemonitor_2_codeobject_2.h"
#include "code_objects/statemonitor_2_codeobject_3.h"
#include "code_objects/statemonitor_codeobject.h"
#include "code_objects/statemonitor_codeobject_1.h"
#include "code_objects/statemonitor_codeobject_2.h"
#include "code_objects/statemonitor_codeobject_3.h"


#include <iostream>
#include <fstream>
#include <string>



void set_from_command_line(const std::vector<std::string> args)
{
    for (const auto& arg : args) {
		// Split into two parts
		size_t equal_sign = arg.find("=");
		auto name = arg.substr(0, equal_sign);
		auto value = arg.substr(equal_sign + 1, arg.length());
		brian::set_variable_by_name(name, value);
	}
}
int main(int argc, char **argv)
{
	std::random_device _rd;
	std::vector<std::string> args(argv + 1, argv + argc);
	if (args.size() >=2 && args[0] == "--results_dir")
	{
		brian::results_dir = args[1];
		#ifdef DEBUG
		std::cout << "Setting results dir to '" << brian::results_dir << "'" << std::endl;
		#endif
		args.erase(args.begin(), args.begin()+2);
	}
        

	brian_start();
        

	{
		using namespace brian;

		
                
        _array_defaultclock_dt[0] = 0.0001;
        _array_defaultclock_dt[0] = 0.0001;
        _array_defaultclock_dt[0] = 0.0001;
        _array_defaultclock_dt[0] = 0.0001;
        
                        
                        for(int i=0; i<_num__array_ring_neurons_lastspike; i++)
                        {
                            _array_ring_neurons_lastspike[i] = - 10000.0;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_ring_neurons_not_refractory; i++)
                        {
                            _array_ring_neurons_not_refractory[i] = true;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_ring_neurons_V; i++)
                        {
                            _array_ring_neurons_V[i] = - 0.08;
                        }
                        
        _run_ring_synapses_synapses_create_generator_codeobject();
        _run_ring_synapses_group_variable_set_conditional_codeobject();
        _run_ring_synapses_asym_synapses_create_generator_codeobject();
        _run_ring_synapses_asym_group_variable_set_conditional_codeobject();
        _array_ring_synapses_asym_vel_in[0] = 0.0;
        _array_glob_inh_neuron_lastspike[0] = - 10000.0;
        _array_glob_inh_neuron_not_refractory[0] = true;
        _array_glob_inh_neuron_V[0] = - 0.08;
        _run_glob_inh2pool_synapses_create_generator_codeobject();
        
                        
                        for(int i=0; i<_dynamic_array_glob_inh2pool_w_inh.size(); i++)
                        {
                            _dynamic_array_glob_inh2pool_w_inh[i] = - 0.000555;
                        }
                        
        _run_pool2glob_inh_synapses_create_generator_codeobject();
        
                        
                        for(int i=0; i<_dynamic_array_pool2glob_inh_w_exc.size(); i++)
                        {
                            _dynamic_array_pool2glob_inh_w_exc[i] = 0.000555;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_ring_neurons_I_ext; i++)
                        {
                            _array_ring_neurons_I_ext[i] = _static_array__array_ring_neurons_I_ext[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_ring_neurons_I_vel; i++)
                        {
                            _array_ring_neurons_I_vel[i] = 0.0;
                        }
                        
        _array_ring_neurons_run_regularly_clock_dt[0] = 0.0001;
        _array_ring_neurons_run_regularly_clock_dt[0] = 0.0001;
        
                        
                        for(int i=0; i<_num__array_statemonitor__indices; i++)
                        {
                            _array_statemonitor__indices[i] = _static_array__array_statemonitor__indices[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_statemonitor_1__indices; i++)
                        {
                            _array_statemonitor_1__indices[i] = _static_array__array_statemonitor_1__indices[i];
                        }
                        
        _array_statemonitor_2__indices[0] = 0;
        _array_defaultclock_timestep[0] = 0;
        _array_defaultclock_t[0] = 0.0;
        _array_ring_neurons_run_regularly_clock_timestep[0] = 0;
        _array_ring_neurons_run_regularly_clock_t[0] = 0.0;
        _before_run_glob_inh2pool_pre_push_spikes();
        _before_run_pool2glob_inh_pre_push_spikes();
        _before_run_ring_synapses_asym_pre_push_spikes();
        _before_run_ring_synapses_pre_push_spikes();
        network.clear();
        network.add(&ring_neurons_run_regularly_clock, _run_ring_neurons_run_regularly_codeobject);
        network.add(&defaultclock, _run_statemonitor_codeobject);
        network.add(&defaultclock, _run_statemonitor_1_codeobject);
        network.add(&defaultclock, _run_statemonitor_2_codeobject);
        network.add(&defaultclock, _run_glob_inh_neuron_stateupdater_codeobject);
        network.add(&defaultclock, _run_ring_neurons_stateupdater_codeobject);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_thresholder_codeobject);
        network.add(&defaultclock, _run_ring_neurons_spike_thresholder_codeobject);
        network.add(&defaultclock, _run_spikemonitor_codeobject);
        network.add(&defaultclock, _run_spikemonitor_1_codeobject);
        network.add(&defaultclock, _run_glob_inh2pool_pre_push_spikes);
        network.add(&defaultclock, _run_glob_inh2pool_pre_codeobject);
        network.add(&defaultclock, _run_pool2glob_inh_pre_push_spikes);
        network.add(&defaultclock, _run_pool2glob_inh_pre_codeobject);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_codeobject);
        network.add(&defaultclock, _run_ring_synapses_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_pre_codeobject);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_resetter_codeobject);
        network.add(&defaultclock, _run_ring_neurons_spike_resetter_codeobject);
        set_from_command_line(args);
        network.run(0.5, NULL, 10.0);
        _after_run_glob_inh_neuron_spike_thresholder_codeobject();
        _after_run_ring_neurons_spike_thresholder_codeobject();
        
                        
                        for(int i=0; i<_num__array_ring_neurons_I_ext; i++)
                        {
                            _array_ring_neurons_I_ext[i] = _static_array__array_ring_neurons_I_ext_1[i];
                        }
                        
        _array_defaultclock_timestep[0] = 5000;
        _array_defaultclock_t[0] = 0.5;
        _array_ring_neurons_run_regularly_clock_timestep[0] = 5000;
        _array_ring_neurons_run_regularly_clock_t[0] = 0.5;
        _before_run_glob_inh2pool_pre_push_spikes();
        _before_run_pool2glob_inh_pre_push_spikes();
        _before_run_ring_synapses_asym_pre_push_spikes();
        _before_run_ring_synapses_pre_push_spikes();
        network.clear();
        network.add(&ring_neurons_run_regularly_clock, _run_ring_neurons_run_regularly_codeobject_1);
        network.add(&defaultclock, _run_statemonitor_codeobject_1);
        network.add(&defaultclock, _run_statemonitor_1_codeobject_1);
        network.add(&defaultclock, _run_statemonitor_2_codeobject_1);
        network.add(&defaultclock, _run_glob_inh_neuron_stateupdater_codeobject_1);
        network.add(&defaultclock, _run_ring_neurons_stateupdater_codeobject_1);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_thresholder_codeobject_1);
        network.add(&defaultclock, _run_ring_neurons_spike_thresholder_codeobject_1);
        network.add(&defaultclock, _run_spikemonitor_codeobject_1);
        network.add(&defaultclock, _run_spikemonitor_1_codeobject_1);
        network.add(&defaultclock, _run_glob_inh2pool_pre_push_spikes);
        network.add(&defaultclock, _run_glob_inh2pool_pre_codeobject_1);
        network.add(&defaultclock, _run_pool2glob_inh_pre_push_spikes);
        network.add(&defaultclock, _run_pool2glob_inh_pre_codeobject_1);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_codeobject_1);
        network.add(&defaultclock, _run_ring_synapses_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_pre_codeobject_1);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_resetter_codeobject_1);
        network.add(&defaultclock, _run_ring_neurons_spike_resetter_codeobject_1);
        network.run(0.5, NULL, 10.0);
        _after_run_glob_inh_neuron_spike_thresholder_codeobject_1();
        _after_run_ring_neurons_spike_thresholder_codeobject_1();
        _array_ring_synapses_asym_vel_in[0] = 0.0;
        _array_defaultclock_timestep[0] = 10000;
        _array_defaultclock_t[0] = 1.0;
        _array_ring_neurons_run_regularly_clock_timestep[0] = 10000;
        _array_ring_neurons_run_regularly_clock_t[0] = 1.0;
        _before_run_glob_inh2pool_pre_push_spikes();
        _before_run_pool2glob_inh_pre_push_spikes();
        _before_run_ring_synapses_asym_pre_push_spikes();
        _before_run_ring_synapses_pre_push_spikes();
        network.clear();
        network.add(&ring_neurons_run_regularly_clock, _run_ring_neurons_run_regularly_codeobject_2);
        network.add(&defaultclock, _run_statemonitor_codeobject_2);
        network.add(&defaultclock, _run_statemonitor_1_codeobject_2);
        network.add(&defaultclock, _run_statemonitor_2_codeobject_2);
        network.add(&defaultclock, _run_glob_inh_neuron_stateupdater_codeobject_2);
        network.add(&defaultclock, _run_ring_neurons_stateupdater_codeobject_2);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_thresholder_codeobject_2);
        network.add(&defaultclock, _run_ring_neurons_spike_thresholder_codeobject_2);
        network.add(&defaultclock, _run_spikemonitor_codeobject_2);
        network.add(&defaultclock, _run_spikemonitor_1_codeobject_2);
        network.add(&defaultclock, _run_glob_inh2pool_pre_push_spikes);
        network.add(&defaultclock, _run_glob_inh2pool_pre_codeobject_2);
        network.add(&defaultclock, _run_pool2glob_inh_pre_push_spikes);
        network.add(&defaultclock, _run_pool2glob_inh_pre_codeobject_2);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_codeobject_2);
        network.add(&defaultclock, _run_ring_synapses_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_pre_codeobject_2);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_resetter_codeobject_2);
        network.add(&defaultclock, _run_ring_neurons_spike_resetter_codeobject_2);
        network.run(0.5, NULL, 10.0);
        _after_run_glob_inh_neuron_spike_thresholder_codeobject_2();
        _after_run_ring_neurons_spike_thresholder_codeobject_2();
        _array_ring_synapses_asym_vel_in[0] = 0.0;
        _array_defaultclock_timestep[0] = 15000;
        _array_defaultclock_t[0] = 1.5;
        _array_ring_neurons_run_regularly_clock_timestep[0] = 15000;
        _array_ring_neurons_run_regularly_clock_t[0] = 1.5;
        _before_run_glob_inh2pool_pre_push_spikes();
        _before_run_pool2glob_inh_pre_push_spikes();
        _before_run_ring_synapses_asym_pre_push_spikes();
        _before_run_ring_synapses_pre_push_spikes();
        network.clear();
        network.add(&ring_neurons_run_regularly_clock, _run_ring_neurons_run_regularly_codeobject_3);
        network.add(&defaultclock, _run_statemonitor_codeobject_3);
        network.add(&defaultclock, _run_statemonitor_1_codeobject_3);
        network.add(&defaultclock, _run_statemonitor_2_codeobject_3);
        network.add(&defaultclock, _run_glob_inh_neuron_stateupdater_codeobject_3);
        network.add(&defaultclock, _run_ring_neurons_stateupdater_codeobject_3);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_thresholder_codeobject_3);
        network.add(&defaultclock, _run_ring_neurons_spike_thresholder_codeobject_3);
        network.add(&defaultclock, _run_spikemonitor_codeobject_3);
        network.add(&defaultclock, _run_spikemonitor_1_codeobject_3);
        network.add(&defaultclock, _run_glob_inh2pool_pre_push_spikes);
        network.add(&defaultclock, _run_glob_inh2pool_pre_codeobject_3);
        network.add(&defaultclock, _run_pool2glob_inh_pre_push_spikes);
        network.add(&defaultclock, _run_pool2glob_inh_pre_codeobject_3);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_asym_pre_codeobject_3);
        network.add(&defaultclock, _run_ring_synapses_pre_push_spikes);
        network.add(&defaultclock, _run_ring_synapses_pre_codeobject_3);
        network.add(&defaultclock, _run_glob_inh_neuron_spike_resetter_codeobject_3);
        network.add(&defaultclock, _run_ring_neurons_spike_resetter_codeobject_3);
        network.run(0.5, NULL, 10.0);
        _after_run_glob_inh_neuron_spike_thresholder_codeobject_3();
        _after_run_ring_neurons_spike_thresholder_codeobject_3();
        #ifdef DEBUG
        _debugmsg_spikemonitor_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_1_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_glob_inh2pool_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_pool2glob_inh_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_asym_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_1_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_glob_inh2pool_pre_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_pool2glob_inh_pre_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_asym_pre_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_pre_codeobject_1();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_1_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_glob_inh2pool_pre_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_pool2glob_inh_pre_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_asym_pre_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_pre_codeobject_2();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_codeobject_3();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_1_codeobject_3();
        #endif
        
        #ifdef DEBUG
        _debugmsg_glob_inh2pool_pre_codeobject_3();
        #endif
        
        #ifdef DEBUG
        _debugmsg_pool2glob_inh_pre_codeobject_3();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_asym_pre_codeobject_3();
        #endif
        
        #ifdef DEBUG
        _debugmsg_ring_synapses_pre_codeobject_3();
        #endif

	}
        

	brian_end();
        

	return 0;
}