import os
import itertools
import pandas as pd
from tqdm import tqdm
import multiprocessing as mp
from brian2 import *  # Brian2 must be imported for the simulation

# Import the simulation function from your model file
from optimization_model import opt_ring_attractor  # your simulation function
# Also import any utility functions if needed (e.g., for computing firing rates, etc.)
from utils import *

# Set the connectivity profile to optimize
# Options: 'mexican_hat', 'cosine'
connectivity_profile = 'cosine'  # Change this to 'cosine' to optimize the cosine profile

# Define the parameter grids based on the connectivity profile
if connectivity_profile == 'mexican_hat':
    # Mexican hat profile parameters
    sigma_exc_range = np.linspace(0.05, 0.2, 5)   # excitatory spread
    sigma_inh_range = np.linspace(0.1, 0.3, 5)    # inhibitory spread
    g_exc_range   = np.linspace(0.5, 1.0, 5)*mV      # excitatory gain
    g_inh_range   = np.linspace(-1.0, -0.3, 5)*mV    # inhibitory gain
    
    # Prepare list of parameter combinations (each is a 4-tuple).
    param_grid = list(itertools.product(sigma_exc_range, sigma_inh_range, g_exc_range, g_inh_range))
    
elif connectivity_profile == 'cosine':
    # Cosine profile parameters - optimize g_cosine, glob_inh, and w_inh
    g_cosine_range = np.linspace(0.01, 0.1, 50)*mV   # cosine gain with smaller scale
    glob_inh_range = [True, False]                # global inhibition flag
    w_inh_range = np.linspace(-2.0, -0.5, 500)*mV    # global inhibition weight
    
    # Create parameter grid with conditional logic
    param_grid = []
    for g in g_cosine_range:
        # Without global inhibition (just g_cosine)
        param_grid.append((g, False, None))
        # With global inhibition (g_cosine, True, and each w_inh value)
        for w in w_inh_range:
            param_grid.append((g, True, w))
else:
    raise ValueError("Unsupported connectivity profile. Choose 'mexican_hat' or 'cosine'.")


total_runs = len(param_grid)

# Fixed parameters for the simulation (not searched over)
fixed_params = {
    'tau': 10,           # in our simulation, run_ring_attractor converts this to ms.
    'sigma_noise': 1,    # similarly converted to mV inside run_ring_attractor.
    'syn_profile': connectivity_profile,  # Set the connectivity profile
}



def worker_run(params_tuple):
    """
    Worker function for a single simulation run on one set of parameters.
    Returns a dictionary with the parameters and performance metrics.
    """
    # Build the full parameter dictionary based on connectivity profile
    params = fixed_params.copy()

    if connectivity_profile == 'mexican_hat':
        sigma_exc, sigma_inh, g_exc, g_inh = params_tuple
        params.update({
            'sigma_exc': sigma_exc,
            'sigma_inh': sigma_inh,
            'g_exc': g_exc,
            'g_inh': g_inh
        })
    elif connectivity_profile == 'cosine':
        # Three parameters being optimized: g_cosine, glob_inh, and w_inh (if glob_inh is True)
        g_cosine, glob_inh, w_inh = params_tuple
        params.update({
            'g_cosine': g_cosine,
            'glob_inh': glob_inh
        })
        # Only add w_inh if global inhibition is enabled
        if glob_inh:
            params.update({'w_inh': w_inh})
        
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
        # Adjust weights to prioritize center accuracy if desired
        w_center = 0.3
        w_Zscore = 0.2
        w_nmse = 0.5
        composite_error = w_center * cwce + w_Zscore * angular_Zscore + w_nmse * nmse
        
        # Create result dictionary with profile-specific parameters
        result = {
            'composite_error': float(composite_error),
            'center_error': float(center_err),
            'pva_magnitude': float(out_pva_magnitude),
            'circular_std': float(circular_std),
            'cwce': float(cwce),
            'angular_Zscore': float(angular_Zscore),
            'nmse': float(nmse),
            'error_message': np.nan
        }
        
        # Add profile-specific parameters to results
        if connectivity_profile == 'mexican_hat':
            result.update({
                'sigma_exc': sigma_exc,
                'sigma_inh': sigma_inh,
                'g_exc': g_exc,
                'g_inh': g_inh
            })
        elif connectivity_profile == 'cosine':
            result.update({
                'g_cosine': g_cosine,
                'glob_inh': glob_inh,
                'w_inh': w_inh if glob_inh else np.nan
            })
            
        return result
    
    except Exception as e:
        # Create error result with profile-specific parameters
        result = {
            'center_error': np.nan,
            'pva_magnitude': np.nan,
            'circular_std': np.nan,
            'cwce': np.nan,
            'angular_Zscore': np.nan,
            'nmse': np.nan,
            'composite_error': np.nan,
            'error_message': str(e)
        }
        
        # Add profile-specific parameters to error results
        if connectivity_profile == 'mexican_hat':
            result.update({
                'sigma_exc': sigma_exc,
                'sigma_inh': sigma_inh,
                'g_exc': g_exc,
                'g_inh': g_inh
            })
        elif connectivity_profile == 'cosine':
            result.update({
                'g_cosine': g_cosine,
                'glob_inh': glob_inh,
                'w_inh': w_inh if glob_inh else np.nan
            })
            
        return result

if __name__ == '__main__':
    print(f"Starting grid search optimization for {connectivity_profile} connectivity profile")
    print(f"Total parameter combinations to evaluate: {total_runs}")
    
    num_proc = mp.cpu_count()   # Adjust the number of worker processes based on your system
    results = []
    
    # Use Pool.imap_unordered with tqdm for progress tracking.
    with mp.Pool(processes=num_proc) as pool:
        for res in tqdm(pool.imap_unordered(worker_run, param_grid), total=total_runs, desc="Grid Search"):
            results.append(res)
    
    # Convert results to a pandas DataFrame for easier sorting and saving.
    results_df = pd.DataFrame(results)
    
    # Create folder for results if it doesn't exist.
    output_folder = "Optimization Results"
    os.makedirs(output_folder, exist_ok=True)
    
    # Save the complete results to a CSV file with profile name in the filename inside the folder
    results_filename = os.path.join(output_folder, f"optimization_results_{connectivity_profile}.csv")
    results_df.to_csv(results_filename, index=False)
    print(f"Results saved to {results_filename}")
    
    # Results Analysis
    # If there are any errors, you might want to filter them out for selecting the best parameters.
    valid_results = results_df[~results_df['composite_error'].isna()]
    
    if not valid_results.empty:
        sortBy = 'composite_error'
        # Sort the DataFrame based on composite_error (lower is better).
        best_result = valid_results.sort_values(by=[sortBy], ascending=[True]).iloc[0]
        print(f"Best parameter set found for {connectivity_profile} profile (sorted by {sortBy}):")
        print(best_result)
    else:
        print("No valid simulation results found.")
