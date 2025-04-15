import itertools
import pandas as pd
from tqdm import tqdm
import multiprocessing as mp
from brian2 import *  # Brian2 must be imported for the simulation

# Import the simulation function from your model file
from optimization_model import opt_ring_attractor  # your simulation function
# Also import any utility functions if needed (e.g., for computing firing rates, etc.)
from utils import *

# Define the parameter grid for sigma_exc, sigma_inh, g_exc, and g_inh.
# These are the only parameters we are searching over.
sigma_exc_range = np.linspace(0.05, 0.2, 5)   # excitatory spread
sigma_inh_range = np.linspace(0.1, 0.3, 5)      # inhibitory spread
g_exc_range   = np.linspace(0.5, 1.0, 5)        # excitatory gain
g_inh_range   = np.linspace(-1.0, -0.3, 5)      # inhibitory gain

# Fixed parameters for the simulation (not searched over)
fixed_params = {
    'tau': 10,           # in our simulation, run_ring_attractor converts this to ms.
    'sigma_noise': 1,    # similarly converted to mV inside run_ring_attractor.
}

# Prepare list of parameter combinations (each is a 4-tuple).
param_grid = list(itertools.product(sigma_exc_range, sigma_inh_range, g_exc_range, g_inh_range))
total_runs = len(param_grid)

def worker_run(params_tuple):
    """
    Worker function for a single simulation run on one set of parameters.
    Returns a dictionary with the parameters and performance metrics.
    """
    sigma_exc, sigma_inh, g_exc, g_inh = params_tuple
    # Build the full parameter dictionary. tau and sigma_noise are fixed.
    params = fixed_params.copy()
    params.update({
        'sigma_exc': sigma_exc,
        'sigma_inh': sigma_inh,
        'g_exc': g_exc,
        'g_inh': g_inh
    })
    
    try:
        # Run the simulation.
        # opt_ring_attractor returns: (GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude)
        GT_center, GT_input, out_rates, out_pva_angle, out_pva_magnitude = opt_ring_attractor(params)
        
        # Compute the circular standard deviation (spread) from the PVA magnitude.
        circular_std = np.sqrt(-2 * np.log(out_pva_magnitude + 1e-8))
        
        # Compute the center error and the confidence weighted center error (CWCE).
        center_err, cwce = conf_weighted_CE(out_pva_angle, GT_center, out_pva_magnitude)
        
        # Compute the angular Z-score:
        # This expresses the misalignment (center_err) in units of the circular standard deviation,
        # analogous to a z-score in linear statistics.
        angular_Zscore = center_err / circular_std
        
        # Compute the NMSE between the observed firing rates and the ideal Gaussian profile.
        nmse = compute_nmse_normalized(out_rates, GT_input, norm_type='max')
        
        # Combine the errors into one composite score.
        # Adjust weights to prioritize center accuracy if desired (here 50% for center error, 50% for NMSE).
        w_center = 0.3
        w_Zscore = 0.2
        w_nmse = 0.5
        composite_error = w_center * cwce + w_Zscore * angular_Zscore + w_nmse * nmse
        
        return {
            'sigma_exc': sigma_exc,
            'sigma_inh': sigma_inh,
            'g_exc': g_exc,
            'g_inh': g_inh,
            'center_error': float(center_err),
            'pva_magnitude': float(out_pva_magnitude),
            'circular_std': float(circular_std),
            'cwce': float(cwce),
            'angular_Zscore': float(angular_Zscore),
            'nmse': float(nmse),
            'composite_error': float(composite_error),
            'error_message': np.nan
        }
    except Exception as e:
        # If an error occurs, capture it for this parameter set.
        return {
            'sigma_exc': sigma_exc,
            'sigma_inh': sigma_inh,
            'g_exc': g_exc,
            'g_inh': g_inh,
            'center_error': np.nan,
            'pva_magnitude': np.nan,
            'circular_std': np.nan,
            'cwce': np.nan,
            'angular_Zscore': np.nan,
            'nmse': np.nan,
            'composite_error': np.nan,
            'error_message': str(e)
        }

if __name__ == '__main__':
    num_proc = mp.cpu_count()   # Adjust the number of worker processes based on your system
    results = []
    
    # Use Pool.imap_unordered with tqdm for progress tracking.
    with mp.Pool(processes=num_proc) as pool:
        for res in tqdm(pool.imap_unordered(worker_run, param_grid), total=total_runs, desc="Grid Search"):
            results.append(res)
    
    
    # Convert results to a pandas DataFrame for easier sorting and saving.
    results_df = pd.DataFrame(results)
    # Save the complete results to a CSV file.
    results_df.to_csv("optimization_results.csv", index=False)
    
    
    # Results Analysis
    # If there are any errors, you might want to filter them out for selecting the best parameters.
    valid_results = results_df[~results_df['composite_error'].isna()]
    
    if not valid_results.empty:
        sortBy = 'composite_error'
        # Sort the DataFrame based on composite_error (lower is better).
        best_result = valid_results.sort_values(by=[sortBy], ascending=[True]).iloc[0]
        print("Best parameter set found sorted by " + sortBy + ":")
        print(best_result)
    else:
        print("No valid simulation results found.")
    

