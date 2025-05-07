
import numpy as np
import itertools
import time
import pickle
import os
from datetime import datetime
from gridSearch_DynapseRA import woker_run

def run_grid_search():
    """
    Run a grid search across parameter sets and evaluate network performance.
    Both coarse (0-7) and fine (0-255) values are tunable.
    """
    # Define parameter ranges for grid search
    # Core 1 parameters (global inhibitory population)
    PS_WEIGHT_EXC_S_N_c1_coarse_range = [5, 6, 7]           # NMDA weight coarse
    PS_WEIGHT_EXC_S_N_c1_fine_range = [30, 80, 130]         # NMDA weight fine
    NPDPIE_THR_S_P_c1_coarse_range = [3, 4, 5]              # NMDA gain coarse
    NPDPIE_THR_S_P_c1_fine_range = [50, 120, 200]           # NMDA gain fine
    
    # Core 3 parameters (ring populations)
    PS_WEIGHT_EXC_F_N_c3_coarse_range = [5, 6, 7]           # AMPA weight coarse
    PS_WEIGHT_EXC_F_N_c3_fine_range = [20, 80, 150]         # AMPA weight fine
    PS_WEIGHT_EXC_S_N_c3_coarse_range = [5, 6, 7]           # NMDA weight coarse
    PS_WEIGHT_EXC_S_N_c3_fine_range = [40, 100, 180]        # NMDA weight fine
    PS_WEIGHT_INH_S_N_c3_coarse_range = [5, 6, 7]           # GABA B weight coarse
    PS_WEIGHT_INH_S_N_c3_fine_range = [50, 120, 200]        # GABA B weight fine
    NPDPIE_THR_F_P_c3_coarse_range = [3, 4, 5]              # AMPA gain coarse
    NPDPIE_THR_F_P_c3_fine_range = [50, 120, 190]           # AMPA gain fine
    NPDPIE_THR_S_P_c3_coarse_range = [3, 4, 5]              # NMDA gain coarse
    NPDPIE_THR_S_P_c3_fine_range = [50, 120, 190]           # NMDA gain fine
    NPDPII_THR_S_P_c3_coarse_range = [3, 4, 5]              # GABA B gain coarse
    NPDPII_THR_S_P_c3_fine_range = [50, 120, 190]           # GABA B gain fine
    
    # Create all parameter combinations
    param_ranges = [
        PS_WEIGHT_EXC_S_N_c1_coarse_range,   # params_tuple[0]
        PS_WEIGHT_EXC_S_N_c1_fine_range,     # params_tuple[1]
        NPDPIE_THR_S_P_c1_coarse_range,      # params_tuple[2]
        NPDPIE_THR_S_P_c1_fine_range,        # params_tuple[3]
        PS_WEIGHT_EXC_F_N_c3_coarse_range,   # params_tuple[4]
        PS_WEIGHT_EXC_F_N_c3_fine_range,     # params_tuple[5]
        PS_WEIGHT_EXC_S_N_c3_coarse_range,   # params_tuple[6]
        PS_WEIGHT_EXC_S_N_c3_fine_range,     # params_tuple[7]
        PS_WEIGHT_INH_S_N_c3_coarse_range,   # params_tuple[8]
        PS_WEIGHT_INH_S_N_c3_fine_range,     # params_tuple[9]
        NPDPIE_THR_F_P_c3_coarse_range,      # params_tuple[10]
        NPDPIE_THR_F_P_c3_fine_range,        # params_tuple[11]
        NPDPIE_THR_S_P_c3_coarse_range,      # params_tuple[12]
        NPDPIE_THR_S_P_c3_fine_range,        # params_tuple[13]
        NPDPII_THR_S_P_c3_coarse_range,      # params_tuple[14]
        NPDPII_THR_S_P_c3_fine_range         # params_tuple[15]
    ]
    
    # Generate all combinations of parameters
    param_combinations = list(itertools.product(*param_ranges))
        
    # Create a results directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"grid_search_results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save parameter ranges for reference
    with open(f"{results_dir}/param_ranges.pkl", "wb") as f:
        pickle.dump(param_ranges, f)
    
    # Store results for each parameter combination
    results = []
    
    # Loop through all parameter combinations
    for i, params_tuple in enumerate(param_combinations):
        print(f"Running parameter set {i+1}/{len(param_combinations)}: {params_tuple}")
        start_time = time.time()
        
        try:
            # Run the model with current parameter set
            spike_id, spike_t = woker_run(params_tuple)
            
            # Calculate some metrics to evaluate this parameter set
            # Example metrics: neuron activity, bump stability, etc.
            # You can customize these based on what you want to measure
            
            # Number of spikes per neuron
            neuron_ids = np.unique(spike_id)
            spike_counts = {neuron_id: np.sum(spike_id == neuron_id) for neuron_id in neuron_ids}
            
            # Save the result for this parameter set
            result = {
                'params': params_tuple,
                'spike_id': spike_id,
                'spike_t': spike_t,
                'spike_counts': spike_counts,
                'runtime': time.time() - start_time
            }
            
            results.append(result)
            
            # Save individual result to avoid losing everything if the process crashes
            with open(f"{results_dir}/param_set_{i}.pkl", "wb") as f:
                pickle.dump(result, f)
                
            print(f"  Completed in {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            print(f"  Error with parameter set {params_tuple}: {e}")
            # Save the error information
            with open(f"{results_dir}/param_set_{i}_error.txt", "w") as f:
                f.write(f"Error with parameter set {params_tuple}: {e}")
    
    # Save all results together
    with open(f"{results_dir}/all_results.pkl", "wb") as f:
        pickle.dump(results, f)
    
    print(f"Grid search completed. Results saved to {results_dir}")
    return results_dir

if __name__ == "__main__":
    results_dir = run_grid_search()
