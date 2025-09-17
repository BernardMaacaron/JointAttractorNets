import numpy as np
from brian2 import *
import pandas as pd
from multiprocessing import Pool, cpu_count
import time
import matplotlib.pyplot as plt
from matplotlib import contour
from scipy.interpolate import interpn

# Global parameters
N = 120  # Number of neurons

def freq2current(freq, tau, tau_ref, Vth, Vreset, Vrest):
    """Convert firing frequency to input current for LIF neurons."""
    T = 1/freq
    k = exp((T-tau_ref)/tau)
    deltaTh = (Vth - Vrest)
    deltaReset = (Vreset - Vrest)

    Iext = (k*deltaTh - deltaReset)/(k-1)
    return Iext

def current2freq(Iext, tau, tau_ref, Vth, Vreset, Vrest):
    """Calculate firing rate of a LIF neuron given input current."""
    numerator = Iext + Vreset - Vrest
    denominator = Iext + Vth - Vrest
    if denominator <= 0:
        raise ValueError("Invalid parameters: denominator must be positive.")
    
    T = tau * np.log(numerator / denominator) + tau_ref
    return 1 / T

def computeOptimalJe(numNeurons=120):
    """
    Compute the optimal excitatory weight based on the number of active neurons.
    
    Parameters:
    -----------
    numNeurons : int
        Number of neurons in the network
        
    Returns:
    --------
    JE_opt : ndarray
        Optimal excitatory weight values
    JE_inv : ndarray
        Inverse of optimal excitatory weight values
    Nact : ndarray
        Range of active neuron counts
    """
    Nact = np.linspace(2, numNeurons-2, numNeurons-3)
    n_tilde = Nact - numNeurons/2
    deltaTheta = 2*pi/numNeurons

    JE_inv = 1/4 + (n_tilde+sin(n_tilde*deltaTheta)/sin(deltaTheta))/(2*numNeurons)
    JE_opt = 1/JE_inv
    return JE_opt, JE_inv, Nact

def _process_single_point(args):
    """
    Helper function to process a single (psi, w) point for parallelization.
    
    Parameters:
    -----------
    args : tuple
        (psi_val, w_val, theta_j, N) where:
        - psi_val: Bump phase value
        - w_val: Bump width value
        - theta_j: Array of neuron positions
        - N: Number of neurons
    
    Returns:
    --------
    tuple
        (f_0, f_even, f_odd) for this specific point
    """
    psi_val, w_val, theta_j, N = args
    
    # Compute circular distance for each neuron to the bump center
    theta_diff = np.mod(theta_j - psi_val + np.pi, 2*np.pi) - np.pi
    
    # Identify active neurons (those within the bump)
    active_mask = np.abs(theta_diff) <= w_val/2
    
    # Skip if no active neurons
    num_active = np.sum(active_mask)
    if num_active == 0:
        return 0.0, 0.0, 0.0
    
    # Calculate the activity term for active neurons: (cos(θ_k - ψ) - cos(w/2))
    cos_diff = np.cos(theta_j[active_mask] - psi_val) - np.cos(w_val/2)
    
    # f_0: Average of (cos(θ_k - ψ) - cos(w/2)) for active neurons
    f_0 = np.sum(cos_diff) / N
    
    # f_even: Average of (cos(θ_k - ψ) - cos(w/2)) * cos(θ_k - ψ) for active neurons
    cos_terms = cos_diff * np.cos(theta_j[active_mask] - psi_val)
    f_even = np.sum(cos_terms) / N
    
    # f_odd: Average of (cos(θ_k - ψ) - cos(w/2)) * sin(θ_k - ψ) for active neurons
    sin_terms = cos_diff * np.sin(theta_j[active_mask] - psi_val)
    f_odd = np.sum(sin_terms) / N
    
    return f_0, f_even, f_odd

def calculate_basis_functions(psi, w, N, parallel=True, n_workers=None):
    """
    Calculate the basis functions f_0, f_even, and f_odd for the given parameters.
    
    Parameters:
    -----------
    psi : float or array-like
        Bump center position(s) (phase values). Can be a scalar, grid, or flattened array.
    w : float or array-like
        Bump width(s). Must be the same shape as psi if both are arrays.
    N : int
        Number of neurons in the network.
    parallel : bool, optional
        Whether to use parallel processing. Default is True.
    n_workers : int, optional
        Number of worker processes to use. If None, uses number of CPU cores.
        
    Returns:
    --------
    tuple
        (f_0, f_even, f_odd) - Scalar values if inputs are scalar, otherwise arrays of the same shape
    """
    # Convert scalar inputs to arrays if needed
    scalar_input = np.isscalar(psi) and np.isscalar(w)
    if scalar_input:
        psi = np.array([psi])
        w = np.array([w])
    
    # Generate neuron positions (equally spaced around the circle)
    theta_j = np.linspace(0, 2*np.pi, N, endpoint=False)
    
    # Prepare inputs for processing
    original_shape = psi.shape
    psi_flat = psi.flatten()
    w_flat = w.flatten()
    n_points = len(psi_flat)

    # Initialize output arrays
    f_0_flat = np.zeros(n_points)
    f_even_flat = np.zeros(n_points)
    f_odd_flat = np.zeros(n_points)
    
    if parallel and n_points > 100:  # Only use parallel for many points
        # Prepare arguments for parallel processing
        args_list = [(psi_flat[i], w_flat[i], theta_j, N) for i in range(n_points)]
        
        # Determine number of workers
        if n_workers is None:
            n_workers = max(1, cpu_count() - 1)  # Leave one CPU free
        
        # Process in parallel
        with Pool(processes=n_workers) as pool:
            results = pool.map(_process_single_point, args_list)
            
        # Unpack results
        for i, (f0, fe, fo) in enumerate(results):
            f_0_flat[i] = f0
            f_even_flat[i] = fe
            f_odd_flat[i] = fo
    else:
        # Sequential processing
        for i in range(n_points):
            psi_val = psi_flat[i]
            w_val = w_flat[i]
            
            # Compute circular distance for each neuron to the bump center
            theta_diff = np.mod(theta_j - psi_val + np.pi, 2*np.pi) - np.pi
            
            # Identify active neurons (those within the bump)
            active_mask = np.abs(theta_diff) <= w_val/2
            
            # Skip if no active neurons
            num_active = np.sum(active_mask)
            if num_active == 0:
                continue
            
            # Calculate the activity term for active neurons: (cos(θ_k - ψ) - cos(w/2))
            cos_diff = np.cos(theta_j[active_mask] - psi_val) - np.cos(w_val/2)
            
            # f_0: Average of (cos(θ_k - ψ) - cos(w/2)) for active neurons
            f_0_flat[i] = np.sum(cos_diff) / N
            
            # f_even: Average of (cos(θ_k - ψ) - cos(w/2)) * cos(θ_k - ψ) for active neurons
            cos_terms = cos_diff * np.cos(theta_j[active_mask] - psi_val)
            f_even_flat[i] = np.sum(cos_terms) / N
            
            # f_odd: Average of (cos(θ_k - ψ) - cos(w/2)) * sin(θ_k - ψ) for active neurons
            sin_terms = cos_diff * np.sin(theta_j[active_mask] - psi_val)
            f_odd_flat[i] = np.sum(sin_terms) / N
    
    # Reshape results back to original shape or return scalar
    f_0 = f_0_flat.reshape(original_shape)
    f_even = f_even_flat.reshape(original_shape)
    f_odd = f_odd_flat.reshape(original_shape)
    
    # Return scalar values if inputs were scalars
    if scalar_input:
        f_0 = f_0[0]
        f_even = f_even[0]
        f_odd = f_odd[0]
    
    return f_0, f_even, f_odd


def find_contour_points(N, f_even_grid, psi_grid, w_grid, je_target, f_0_grid=None, f_odd_grid=None,
                        return_type='dataframe', visualize=False, interpolate=False):
    """
    Find points along the contour where f_even = 1/je_target.
    
    Parameters:
    -----------
    N : int
        Number of neurons in the network
    f_even_grid : ndarray
        2D array containing f_even values at grid points
    psi_grid : ndarray
        2D meshgrid of psi values
    w_grid : ndarray
        2D meshgrid of width values
    je_target : float
        Target Je value to find contour for (will find where f_even = 1/je_target)
    f_0_grid : ndarray, optional
        2D array containing f_0 values at grid points (for interpolation)
    f_odd_grid : ndarray, optional
        2D array containing f_odd values at grid points (for interpolation)
    return_type : str, optional
        'dataframe' for pandas DataFrame, 'arrays' for (psi, width) arrays
    visualize : bool, optional
        Whether to plot the contour
    interpolate : bool, optional
        Whether to use interpolation for f_0 and f_odd values
  
    Returns:
    --------
    contour_points : DataFrame or tuple
        Either a DataFrame with psi and width columns, or a tuple of (psi, width) arrays
    """
    # Create a figure for the contour calculation
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    # Compute the contour lines at the specific level 1/je_target
    contour_level = 1/je_target
    
    # Draw contour
    contour_set = ax.contour(psi_grid, w_grid, f_even_grid, levels=[contour_level], colors='r', linewidths=2)
    
    # Extract contour data
    all_contour_points = []
    
    # Get all the contour segments
    for i in range(len(contour_set.allsegs)):
        for segment in contour_set.allsegs[i]:
            if len(segment) > 0:
                psi_points = segment[:, 0]
                width_points = segment[:, 1]
                
                # Append to our list of points
                for j in range(len(psi_points)):
                    all_contour_points.append((psi_points[j], width_points[j]))
    
    # If no contour points were found
    if not all_contour_points:
        raise ValueError("No contour points found for the specified je_target.")
        if return_type == 'dataframe':
            return pd.DataFrame(columns=['psi', 'width'])
        else:
            return np.array([]), np.array([])
    
    # Convert to arrays
    contour_points = np.array(all_contour_points)
    psi_contour = contour_points[:, 0]
    width_contour = contour_points[:, 1]
    
    # Interpolate f_0 and f_odd values if grids are provided
    f_0_values = None
    f_odd_values = None
    
    if f_0_grid is not None and f_odd_grid is not None and interpolate:
        try:
            # Extract the 1D coordinates from the meshgrid for interpolation
            psi_1d = psi_grid[0, :]  # First row contains all psi values
            w_1d = w_grid[:, 0]      # First column contains all w values

            # Create interpolation points
            points = (w_1d, psi_1d)
            xi = np.column_stack((width_contour, psi_contour))

            # Interpolate values
            f_0_values = interpn(points, f_0_grid.T, xi, method='linear', bounds_error=False)
            f_odd_values = interpn(points, f_odd_grid.T, xi, method='linear', bounds_error=False)
        except Exception as e:
            pass
    else:
        f_0_values, _, f_odd_values = calculate_basis_functions(psi_contour, width_contour, N)

    # If visualization is requested, finalize the plot
    if visualize:
        plt.show()
    else:
        plt.close(fig)
        
    # Return the result in the requested format
    if return_type == 'dataframe':
        df = pd.DataFrame({
            'psi': psi_contour,
            'width': width_contour
        })
        
        # Add interpolated values if available
        if f_0_values is not None:
            df['f_0'] = f_0_values
            df['f_odd'] = f_odd_values
        
        return df
    else:
        if f_0_values is not None:
            return psi_contour, width_contour, f_0_values, f_odd_values
        else:
            return psi_contour, width_contour


def computeJi(psi_contour, width_contour, je_target, f_0_contour, A, cff, N):
    """
    Calculate inhibitory weights (Ji) from contour points for given parameters.
    
    Parameters:
    -----------
    psi_contour : ndarray
        Array of psi values on the contour
    width_contour : ndarray
        Array of width values on the contour
    je_target : float
        Target Je value used for the contour
    f_0_contour : ndarray
        Array of f_0 values on the contour
    A : float
        Target amplitude parameter
    cff : float
        Baseline parameter
    N : int
        Number of neurons
        
    Returns:
    --------
    Ji : float
        Optimal inhibitory connection strength
    Ji_upper_bound : float
        Upper bound for Ji to ensure stability
    """
    # Calculate Ji needed for desired amplitude
    ratio = cff / A
    Ji_values = ((ratio - 1) * np.cos(width_contour/2) - ratio) / f_0_contour

    # Choose minimum value as in original code
    Ji = np.min(Ji_values)
    
    # Check stability bound
    Ji_upper_bound = np.min(-np.cos(width_contour/2) / f_0_contour)
    
    return Ji, Ji_upper_bound


def optimizeMatrixGains(numNeurons, Nact=None, cff=1.0, A=0.2):
    """
    Calculate optimal matrix gains (JE and JI) for a ring attractor network.
    
    Parameters:
    -----------
    numNeurons : int
        Number of neurons in the network
    Nact : int, optional
        Number of active neurons, defaults to numNeurons//2
    cff : float, optional
        Baseline parameter, defaults to 1.0
    A : float, optional
        Target amplitude parameter, defaults to 0.2
        
    Returns:
    --------
    JE_chosen : float
        Optimal excitatory connection strength
    JI_chosen : float
        Optimal inhibitory connection strength
    """
    # Default Nact to half the neurons if not specified
    if Nact is None:
        Nact = numNeurons // 2
        
    # Compute optimal Je
    JE_opt, _, Nact_range = computeOptimalJe(numNeurons=numNeurons)
    
    # Find the closest Nact value in the range
    idx = np.abs(Nact_range - Nact).argmin()
    JE_chosen = JE_opt[idx]
    
    # Create sample grids
    psi_samples = np.linspace(0, 2*np.pi, 10*numNeurons, endpoint=False)
    w_samples = np.linspace(2*np.pi/numNeurons, 2*(numNeurons-1)*np.pi/numNeurons, 10*numNeurons, endpoint=False)
    psi_grid, w_grid = np.meshgrid(psi_samples, w_samples)
    
    # Calculate basis functions on grid
    f_0_grid, f_even_grid, f_odd_grid = calculate_basis_functions(psi_grid, w_grid, numNeurons)
    
    # Find contour points
    contour_df = find_contour_points(numNeurons, f_even_grid, psi_grid, w_grid, je_target=JE_chosen,
                                     f_0_grid=f_0_grid, f_odd_grid=f_odd_grid,
                                     return_type='dataframe', visualize=False)
    
    # Compute optimal Ji
    JI_chosen, _ = computeJi(
        psi_contour=contour_df['psi'], 
        width_contour=contour_df['width'],
        je_target=JE_chosen, 
        f_0_contour=contour_df['f_0'],
        A=A, cff=cff, N=numNeurons
    )
    
    return JE_chosen, JI_chosen


def main():
    """
    Main function to execute the optimization algorithm.
    """
    JE_chosen, JI_chosen = optimizeMatrixGains(N)


if __name__ == "__main__":
    main()