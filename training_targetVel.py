
import os
os.environ['BRIAN2_LOG_LEVEL'] = 'ERROR'
# from ring_attractor import RingAttractor
# from gaussian_input_generator import Gaussian_Input_Generator
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pandas.plotting import parallel_coordinates
import seaborn as sns
import pandas as pd
import warnings
import sys
from brian2 import *
# from gaussian_editor import GuassianEditor
# from plot_generator import PlotGenerator
import threading
from collections import deque
import time
import socket
# from gp_model import VelocityAlphaModel, get_model_path, train_and_save_model
warnings.filterwarnings('ignore')

nsm_path = os.path.join(os.path.dirname(__file__), 'Neuron and Synapse Models')
sys.path.append(nsm_path)
from ringAttractorClass import RingAttractor
from ringAttractorClassBoundaries import  BoundedRingAttractor
from ringAttractorClassExtended import FaithfulBoundedRingAttractor
from neuronModels import LIF_xi_vel_eq,LIF_synapticDecay_xi_vel_eq

tools_path = os.path.join(os.path.dirname(__file__), 'Tools')
sys.path.append(tools_path)
from utils import computeInstRate, computePVA,computePVATT
from plottingTools import raster_plot

import glob
from multiprocessing import Pool, cpu_count
from scipy.optimize import minimize_scalar, minimize
from tqdm import tqdm

warnings.filterwarnings('ignore')

def round_velocity(velocity):
    """Round velocity according to the specified rules:
       7.1 -> 7, 7.4 -> 7.5, 7.6 -> 7.5, 7.8 -> 8
    """
    base = int(velocity)
    fraction = abs(velocity) - abs(base)
    
    if fraction < 0.25:
        return base
    elif fraction < 0.75:
        return base + 0.5 * np.sign(velocity)
    else:
        return base + 1.0 * np.sign(velocity)

def load_trajectory_data(file_path):
    """Load trajectory data from a text file (velocity only)."""
    data = pd.read_csv(file_path, comment='#', delim_whitespace=True, 
                       names=['time', 'position', 'velocity', 'acceleration'])
    # Round velocities according to our rule
    data['rounded_velocity'] = data['velocity'].apply(round_velocity)
    return data


def runSimulation(ringAttractor, device = None, dt=0.1*ms,
                    inputParams = None, inputType='Uniform',
                    velInput = 0.0, runTime=50*ms, plot=False, flag=True,
                    velocity_vector=None,training=False):
    
    
    if device == 'cpp_standalone':
        device.reinit()
        device.activate()
        set_device(device, build_on_run=False)

    # Define simulation parameters
    defaultclock.dt = dt
    
    # Define Inputs

    I0 = inputParams.get('I0', 0) * mV
    targetPosition = inputParams.get('targetPosition', 0) # Consider this is in degrees

    # Calculate external input based on input type
    I_ext_array = np.zeros(ringAttractor.numNeurons) * mV
    if inputType == 'Gaussian':
        # Original Gaussian input
        stimulus_center = np.deg2rad(targetPosition) % (2*np.pi)  # Convert degrees to radians
        stimulus_width = 0.5  # width in radians

        d = np.arctan2(np.sin(ringAttractor.positions - stimulus_center), np.cos(ringAttractor.positions - stimulus_center))
        I_ext_array += I0 * np.exp(-(d**2) / (2 * stimulus_width**2))
    
    elif inputType == 'Uniform':
        # Equal input to all neurons
        I_ext_array += np.ones(ringAttractor.numNeurons) * I0

        target_index = ringAttractor._get_neuron_index(targetPosition, in_degrees=True)
        if flag:
            I_ext_array[target_index] += inputParams.get('I_target', 1.0)*mV

    ringAttractor.ring_pool.I_ext = I_ext_array

    # Define Monitors
    ringAttractor.spikeMonitor = SpikeMonitor(ringAttractor.ring_pool)
    localObjects = [ringAttractor.spikeMonitor]
    net = Network(ringAttractor.BrianObjects + localObjects)

    # 1. Initialization: run 50ms with velocity OFF
    if flag:
        ringAttractor.ring_pool.I_ext = I_ext_array
        ringAttractor.ring_synapses_asym.vel_in = velInput
        ringAttractor.ring_synapses_asym.vel_on = False
        net.run(50*ms)
        I_ext_array[target_index] -= inputParams.get('I_target', 1.0)*mV
         

    ringAttractor.ring_pool.I_ext = I_ext_array
    net.run(50*ms)
    # 2. Main simulation: for each entry in velocity_vector, run 50ms with correct sign
    pva_angle_vec = []
    pva_magnitude_vec = []
    if training:
        if len(velocity_vector) > 800:
            velocity_vector=velocity_vector[:800]
        if len(velocity_vector) < 800 and len(velocity_vector) > 400:
            velocity_vector = velocity_vector[:400]
        if len(velocity_vector) < 400:
            velocity_vector = velocity_vector[:200]

    if velocity_vector is not None:
        for v in velocity_vector:
            # Set velocity input sign
            if v >= 0:
                ringAttractor.ring_synapses_asym.vel_in = -(velInput)
            else:
                ringAttractor.ring_synapses_asym.vel_in = (velInput)
            ringAttractor.ring_synapses_asym.vel_on = True
            net.run(50*ms)
            # firingRates = computeInstRate(ringAttractor.spikeMonitor, ringAttractor.numNeurons, meanISI = True)
            # pva_angle, pva_magnitude = computePVA(firingRates, ringAttractor.positions)
            # pva_angle_vec.append(pva_angle)
            # pva_magnitude_vec.append(pva_magnitude)
        simTime = 100*ms + len(velocity_vector)*50*ms
        pva_angle, time_windows = computePVATT(ringAttractor.spikeMonitor, ringAttractor.positions,simTime,120, 50*ms,50*ms)
        if not training:
            print('FINISHED')
            plt.figure()
            ax = plt.gca()
            raster_plot(ringAttractor.spikeMonitor, ax=ax, stim_periods=(0*second, 50*ms),
                stim_display_method='highlight', duration=simTime, num_neurons=120, y_axisFull=True)
            plt.savefig("raster_plot.png")
            plt.show(block=True)  # Force the plot window to block execution until closed

  
    else:
        # fallback: run once for runTime
        ringAttractor.ring_synapses_asym.vel_in = velInput
        ringAttractor.ring_synapses_asym.vel_on = True
        net.run(runTime)
        firingRates = computeInstRate(ringAttractor.spikeMonitor, ringAttractor.numNeurons, meanISI = True)
        pva_angle, pva_magnitude = computePVA(firingRates, ringAttractor.positions)
        # pva_angle_vec.append(pva_angle-np.deg2rad(44)) # Remove offset of 44 degrees
        pva_angle_vec.append(pva_angle)
        pva_magnitude_vec.append(pva_magnitude)
        simTime = runTime + 50*ms

    if device == 'cpp_standalone':
        device.build(directory = 'internalSim_build', compile=True, run=True, debug=False, clean=False)

    if plot:
        raster_plot(ringAttractor.spikeMonitor,duration=simTime, num_neurons=ringAttractor.numNeurons, y_axisFull=True)

    return pva_angle, pva_magnitude_vec
    

def simulate_with_trajectory(data, target_velocity, alpha_value, initial_position=None, duration=None, training=False):
    """
    Simulate the ring attractor using a trajectory from data file (velocity only).
    Args:
        data: DataFrame with time, position, velocity columns
        target_velocity: The target velocity for this trajectory (from filename)
        alpha_value: Alpha parameter for velocity
        initial_position: Starting position (if None, use first position from data)
        duration: How many timesteps to use (if None, use all data)
    Returns:
        error: Mean squared error between bump and ground truth
        bump_positions: List of bump positions during simulation
        gt_positions: List of ground truth positions during simulation
    """
    tv = target_velocity
    # Use the full velocity vector for ground truth
    velocity_vector = data['velocity'].iloc[:].values
    position_vector = data['position'].iloc[:].values
    # Use the first position as the initial target position
    initial_target_position = position_vector[0]
    # neuron_eq = Equations(LIF_xi_vel_eq, tau=10*ms, V_rest=-70*mV, sigma_noise=0.0*mV)
    neuron_eq = Equations(LIF_synapticDecay_xi_vel_eq, tau=10*ms, V_rest=-70*mV, sigma_noise=0.0*mV,tau_s=10*ms)
    
    limit_joint=np.deg2rad(88)
    limit_neuron=np.round((limit_joint*120)/(2*np.pi))
    ring = FaithfulBoundedRingAttractor(neuron_eq, w_sub=-10.333033268750986*mV, g_cosine=10.333033257636599*mV, limit_neuron=None)
    # ring= FaithfulBoundedRingAttractor(neuron_eq,  
    #                     w_sub=-0.33478*mV,
    #                     g_cosine=0.33496*mV,
    #                     limit_neuron=None)
    
    # ring = RingAttractor(neuron_eq,  
    #                     syn_profile='cosine',
    #                     autapse=True,
    #                     glob_inh=True, w_inh=-0.555*mV,
    #                     g_cosine=0.1*mV)
    # ring = BoundedRingAttractor(neuron_eq,  
    #                         syn_profile='cosine',
    #                         autapse=True,
    #                         glob_inh=True, w_inh=-0.555*mV,
    #                         g_cosine=0.1*mV,
    #                         limit_neuron=limit_neuron)
    ring.ring_pool.run_regularly('V = clip(V, -80*mV, inf*volt)', dt=0.1*ms)
    dt = 0.1*ms
    # inputParams = {'I0': 80.00, 'targetPosition': initial_target_position+44, 'I_target': 10.0}
    inputParams = {'I0': 80.00, 'targetPosition': initial_target_position, 'I_target': 10.0}
    alpha_value = 0.0013
    velocityInput = alpha_value * tv 
    # Run the simulation once for the whole trajectory
    pva_angle_vec, pva_magnitude_vec = runSimulation(
        ringAttractor=ring, device=None, dt=dt,
        inputParams=inputParams, inputType='Uniform',
        velInput=velocityInput, runTime=50*ms, plot=False, flag=True,
        velocity_vector=velocity_vector,training=training)

    # Convert pva_angle_vec to degrees for output, but keep radians for error calculation
    bump_positions = np.rad2deg(pva_angle_vec)
    
    # Ensure gt_positions has the same length as bump_positions
    if len(pva_angle_vec) > 0:
        gt_positions = position_vector[:len(pva_angle_vec)]
    else:
        gt_positions = position_vector

    # Calculate error (circular distance) for each segment
    errors = []
    for pva_angle, gt_pos in zip(pva_angle_vec, position_vector):
        gt_pos_rad = np.deg2rad(gt_pos)
        error = min(
            abs(pva_angle - gt_pos_rad),
            2 * np.pi - abs(pva_angle - gt_pos_rad)
        )
        if np.rad2deg(error) <= 1.5:
            error = 0.0
        errors.append(error**2)
    mse = np.mean(errors) if errors else float('inf')
    return mse, bump_positions, gt_positions

def find_optimal_alpha_for_trajectory(data_file, duration=None):
    """
    Find the optimal alpha for a given trajectory data file.
    
    Args:
        data_file: Path to the trajectory data file
        duration: How many timesteps to use (if None, use all data)
        
    Returns:
        rounded_velocities: Unique rounded velocities in the trajectory
        optimal_alpha: Best alpha value for the entire trajectory
        mse: Mean squared error with optimal alpha
        data: Original trajectory data
    """
    print(f"Processing file: {data_file}")
    
    # Load trajectory data
    data = load_trajectory_data(data_file)
    
    if duration is None:
        duration = len(data)
    else:
        duration = min(duration, len(data))
    
    # Define objective function for optimization
    def objective_function(alpha):
        mse, _, _ = simulate_with_trajectory(data, alpha, duration=duration)
        return mse
    
    # Find optimal alpha using bounded optimization
    result = minimize_scalar(
        objective_function,
        bounds=(0.0, 1.0),
        method='bounded',
        options={'maxiter': 20}
    )
    
    optimal_alpha = result.x
    
    # Get final metrics with optimal alpha
    mse, bump_pos, gt_pos = simulate_with_trajectory(data, optimal_alpha, duration=duration)
    
    # Extract unique rounded velocities
    rounded_velocities = data['rounded_velocity'].unique()
    
    return rounded_velocities, optimal_alpha, mse, data, bump_pos, gt_pos

def optimize_alpha_beta_for_velocity_sequential(velocity_segments):
    """Sequential optimization for each velocity to avoid multiprocessing issues with Brian2"""
    results = []
    
    for velocity, trajectory_segments in tqdm(velocity_segments.items(), desc="Optimizing velocities"):
        # Define objective function for this velocity
        def objective_function(params):
            alpha, beta = params
            total_mse = 0
            total_weight = 0
            for segment in trajectory_segments:
                mse, _, _ = simulate_with_trajectory(segment, alpha, beta)
                segment_weight = len(segment)
                total_mse += mse * segment_weight
                total_weight += segment_weight
            return total_mse / total_weight if total_weight > 0 else float('inf')
        
        # Initial guess
        initial_guess = [0.13, 0.05]  # Starting alpha and beta values
        
        # Bounds for parameters
        bounds = [(0.0, 1.0), (-1.0, 1.0)]  # bounds for alpha and beta
        
        # Optimize alpha and beta for this velocity
        result = minimize(
            objective_function,
            initial_guess,
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 20}
        )
        
        optimal_alpha, optimal_beta = result.x
        mse = objective_function(result.x)
        
        results.append((velocity, optimal_alpha, optimal_beta, mse, len(trajectory_segments)))
    
    return results

def optimize_alpha_for_velocity(args):
    """Helper function for parallel processing to optimize only alpha (velocity only, with target_velocity)"""
    target_velocity, trajectory_segments,training = args
    def objective_function(alpha):
        total_mse = 0
        total_weight = 0
        for segment in trajectory_segments:
            mse, _, _ = simulate_with_trajectory(segment, target_velocity, alpha,training=training)
            segment_weight = len(segment)
            total_mse += mse * segment_weight
            total_weight += segment_weight
        return total_mse / total_weight if total_weight > 0 else float('inf')
    result = minimize_scalar(
        objective_function,
        bounds=(-5.0, 5.0),
        method='bounded',
        options={'maxiter': 20}
    )
    optimal_alpha = result.x
    mse = objective_function(optimal_alpha)
    return target_velocity, optimal_alpha, mse, len(trajectory_segments)



def train_from_trajectory_files(folder_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia", output_dir="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/Images/Mujoco_training_onlyVelocity",duration=None,training=True):
    """
    Train g(v) function from trajectory files (velocity only).
    Args:
        folder_path: Path to folder containing trajectory files
        output_dir: Directory to save output files
        duration: How many timesteps to use from each file (if None, use all)
    Returns:
        velocity_data: DataFrame with velocity -> optimal alpha mapping
    """
    import re
    os.makedirs(output_dir, exist_ok=True)
    file_pattern = os.path.join(folder_path, "*.txt")
    trajectory_files = glob.glob(file_pattern)
    if not trajectory_files:
        print("No trajectory files found.")
        return None
    print(f"Found {len(trajectory_files)} trajectory files")
    optimization_args = []
    for file_path in trajectory_files:
        # Extract target velocity from filename (e.g., run_1.9.txt -> 1.9)
        base = os.path.basename(file_path)
        match = re.search(r'([-+]?[0-9]*\.?[0-9]+)', base)
        if match:
            target_velocity = float(match.group(1))
        else:
            print(f"Could not extract velocity from filename: {base}, skipping.")
            continue
        data = load_trajectory_data(file_path)
        optimization_args.append((target_velocity, [data],training))
    print(f"Optimizing alpha for {len(optimization_args)} target velocities...")
    with Pool(processes=cpu_count()) as pool:
        optimization_results = list(tqdm(
            pool.imap(optimize_alpha_for_velocity, optimization_args),
            total=len(optimization_args)
        ))
    velocity_data = pd.DataFrame(
        optimization_results, 
        columns=['velocity', 'optimal_alpha', 'mse', 'num_segments']
    )
    velocity_data = velocity_data.sort_values('velocity')
    # Duplicate rows for negative velocities to show symmetry
    velocity_data_sym = velocity_data.copy()
    velocity_data_sym['velocity'] = -velocity_data_sym['velocity']
    velocity_data_sym['v_times_alpha'] = velocity_data_sym['velocity'] * velocity_data_sym['optimal_alpha']
    velocity_data['v_times_alpha'] = velocity_data['velocity'] * velocity_data['optimal_alpha']
    velocity_data_plot = pd.concat([velocity_data, velocity_data_sym], ignore_index=True).sort_values('velocity')
    csv_path = os.path.join(output_dir, "velocity_alpha_mapping.csv")
    velocity_data.to_csv(csv_path, index=False)
    print(f"Velocity to alpha mapping saved to {csv_path}")
    # Plot only velocity and alpha (no acceleration)
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plt.scatter(velocity_data_plot['velocity'], velocity_data_plot['optimal_alpha'], 
                s=velocity_data_plot['num_segments']*10, alpha=0.7)
    plt.xlabel('Target Velocity (deg/s)')
    plt.ylabel('Optimal Alpha')
    plt.title('Alpha Function from Trajectory Data (Symmetric)')
    plt.grid(True)
    plt.subplot(2, 1, 2)
    plt.scatter(velocity_data_plot['velocity'], velocity_data_plot['v_times_alpha'], 
                s=velocity_data_plot['num_segments']*10, alpha=0.7)
    plt.xlabel('Target Velocity (deg/s)')
    plt.ylabel('v * alpha (deg/s)')
    plt.title('Effective Input to Network (v * alpha, Symmetric)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "g_v_function_and_product.png"))
    plt.figure(figsize=(10, 6))
    plt.scatter(velocity_data_plot['velocity'], velocity_data_plot['optimal_alpha'], 
                s=velocity_data_plot['num_segments']*10, alpha=0.7)
    plt.xlabel('Target Velocity (deg/s)')
    plt.ylabel('Optimal Alpha')
    plt.title('Alpha Function from Trajectory Data (Symmetric)')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "g_v_function.png"))
    plt.figure(figsize=(10, 6))
    plt.scatter(velocity_data_plot['velocity'], velocity_data_plot['v_times_alpha'], 
                s=velocity_data_plot['num_segments']*10, alpha=0.7)
    plt.xlabel('Target Velocity (deg/s)')
    plt.ylabel('v * alpha (deg/s)')
    plt.title('Effective Input to Network (v * alpha, Symmetric)')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "v_times_g_v_function.png"))
    return velocity_data

def validate_trajectory_with_gv(data_file, velocity_data):
    """
    Validate a trajectory using the learned g(v) function.
    
    Args:
        data_file: Path to trajectory data file
        velocity_data: DataFrame with velocity -> optimal alpha mapping
    
    Returns:
        mse: Mean squared error using g(v) function
        bump_pos: Bump positions during simulation
        gt_pos: Ground truth positions
    """
    # Load trajectory data
    data = load_trajectory_data(data_file)
    # Extract target velocity from filename (for symmetry)
    import re, os

    base = os.path.basename(data_file)
    match = re.search(r'([-+]?[0-9]*\.?[0-9]+)', base)
    if match:
        target_velocity = float(match.group(1))
    else:
        target_velocity = data['velocity'].iloc[0] if len(data) > 0 else 0.0

    # Find closest velocity in mapping (allow for symmetry)
    vmap = velocity_data.copy()
    vmap['abs_velocity'] = vmap['velocity'].abs()
    abs_target = abs(target_velocity)
    if abs_target in vmap['abs_velocity'].values:
        alpha = vmap.loc[vmap['abs_velocity'] == abs_target, 'optimal_alpha'].iloc[0]
    else:
        closest_idx = (vmap['abs_velocity'] - abs_target).abs().idxmin()
        alpha = vmap.loc[closest_idx, 'optimal_alpha']

    # Use the full trajectory and trained alpha for this velocity
    mse, bump_positions, gt_positions = simulate_with_trajectory(
        data, target_velocity, alpha)
    return mse, bump_positions, gt_positions

def validate_all_trajectories(folder_path="./capocaccia", output_dir="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/Images/Mujoco_training_withoutSymmetry", velocity_data=None):
    """
    Validate all trajectories using the learned g(v) function.
    
    Args:
        folder_path: Path to folder containing trajectory files
        velocity_data: DataFrame with velocity -> optimal alpha mapping
                       (if None, load from csv)
    
    Returns:
        validation_results: DataFrame with validation metrics for each file
    """
    if velocity_data is None:
        try:
            velocity_data = pd.read_csv("/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_no_boundary/target_velocity_training/velocity_alpha_mapping.csv")
        except FileNotFoundError:
            raise ValueError("velocity_alpha_mapping.csv not found. Run training first.")

    # Find all trajectory files
    file_pattern = os.path.join(folder_path, "*.txt")
    trajectory_files = glob.glob(file_pattern)

    validation_results = []
    os.makedirs(output_dir, exist_ok=True)

    for file_path in trajectory_files:
        try:
            mse, bump_pos, gt_pos = validate_trajectory_with_gv(file_path, velocity_data)
            bump_pos=bump_pos[2:]
            # bump_pos = bump_pos - 44
            bump_pos = ((bump_pos + 180) % 360) - 180
            df = pd.DataFrame({'gt_pos': gt_pos, 'bump_pos': bump_pos})
            #save to csv
            df.to_csv(os.path.join(output_dir, f"gv_validation_{os.path.basename(file_path)}"), index=False)
            
            # Store validation results
            validation_results.append({
                'file': os.path.basename(file_path),
                'mse': mse
            })

            # Plot validation
            plt.figure(figsize=(10, 6))
            plt.plot(gt_pos, label='Ground Truth', linewidth=2)
            plt.plot(bump_pos, label='Bump Position', linestyle='--', linewidth=2)
            plt.title(f"Validation: {os.path.basename(file_path)}, MSE: {mse:.6f}")
            plt.xlabel('Segment')
            plt.ylabel('Position (deg)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"gv_validation_{os.path.basename(file_path).split('.')[0]}.png"))
            plt.close()

        except Exception as e:
            print(f"Error validating file {file_path}: {e}")

    # Save validation results
    validation_df = pd.DataFrame(validation_results)
    validation_df.to_csv(os.path.join(output_dir, "validation_results.csv"), index=False)
    print("Validation results saved to validation_results.csv")

    return validation_df

def plot_comparison(path1, path2, path3, path4):
    """Plot comparison between four validation result files with rescaled x-axis."""
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from scipy import interpolate
    
    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    df3 = pd.read_csv(path3)
    df4 = pd.read_csv(path4)
    
    # Use df3 and df4 length as reference (they should have the same length)
    reference_length = max(len(df3), len(df4))
    
    # df1 and df2 should extend 100ms (2 timesteps) beyond df3/df4
    extended_length = reference_length + 2  # Add 100ms = 2 timesteps at 50ms each
    
    # Create x-axis for reference data (df3, df4) - convert to milliseconds (50ms per timestep)
    x_reference = np.arange(reference_length) * 50
    
    # Create extended x-axis for df1 and df2 data
    x_extended = np.arange(extended_length) * 50
    
    # Function to rescale data to match target length
    def rescale_data(data, target_length):
        if len(data) == target_length:
            return data
        # Create interpolation function
        old_x = np.linspace(0, target_length-1, len(data))
        new_x = np.linspace(0, target_length-1, target_length)
        interpolator = interpolate.interp1d(old_x, data, kind='linear', 
                                          bounds_error=False, fill_value='extrapolate')
        return interpolator(new_x)
    
    # Rescale df1 and df2 data to extended length (reference + 100ms)
    df1_gt_rescaled = rescale_data(df1['gt_pos'].values, extended_length)
    df1_bump_rescaled = rescale_data(df1['bump_pos'].values, extended_length)
    df2_bump_rescaled = rescale_data(df2['bump_pos'].values, extended_length)

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot with rescaled x-axis - df1/df2 extend 100ms beyond df3/df4
    ax.plot(x_extended, df1_gt_rescaled, linewidth=2, linestyle='--')
    ax.plot(x_extended, df1_bump_rescaled, linewidth=2, linestyle='--', color='red')
    ax.plot(x_extended, df2_bump_rescaled, linewidth=2, linestyle='--', color='orange')
    ax.plot(x_reference, df3['gt_pos'], linewidth=2, linestyle='-', color='C0')
    ax.plot(x_reference, df3['bump_pos'], linewidth=2, linestyle='-', color='red')
    ax.plot(x_reference, df4['bump_pos'], linewidth=2, linestyle='-', color='orange')

    # Add upper and lower boundary lines at ±44 degrees
    ax.axhline(y=44, color='blue', linestyle='--', linewidth=2, alpha=0.8)
    ax.axhline(y=-44, color='blue', linestyle='--', linewidth=2, alpha=0.8)
    
    # Add boundary labels aligned to start from 5ms
    ax.text(5, 46, 'Upper boundary', ha='left', va='bottom', 
            fontsize=16, color='blue')
    ax.text(5, -46, 'Lower boundary', ha='left', va='top', 
            fontsize=16, color='blue')
    
    # ax.set_title(f"Comparison of Validation Results", weight='bold')
    ax.set_xlabel('Time (ms)', fontsize=18)
    ax.set_ylabel('Position (deg)', fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.set_ylim([-90, 90])
    ax.legend(fontsize=16)
    ax.grid(True)
    
    # Add text boxes to distinguish scenarios
    ax.text(0.02, 0.98, 'Dashed lines: Limited motion data', transform=ax.transAxes, 
            fontsize=16, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.text(0.02, 0.90, 'Solid lines: Wide motion data', transform=ax.transAxes, 
            fontsize=16, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.8))

    # Add top subplot for velocity step function
    divider = make_axes_locatable(ax)
    tax = divider.append_axes("top", size="15%", pad=0.3)

    # Create target velocity step function based on ground truth direction changes
    gt_pos = df1_gt_rescaled  # Use rescaled data
    
    # Find direction changes in ground truth (zero crossings of derivative)
    gt_diff = np.diff(gt_pos)
    
    # Smooth the derivative to avoid noise
    from scipy.ndimage import uniform_filter1d
    gt_diff_smooth = uniform_filter1d(gt_diff, size=3)
    
    # Find zero crossings (derivative sign changes)
    direction_changes = [0]  # Always start at t=0
    
    # Look for sign changes in smoothed derivative
    for i in range(1, len(gt_diff_smooth)-1):
        if gt_diff_smooth[i-1] * gt_diff_smooth[i+1] < 0:  # Sign change detected
            # Make sure we don't add changes too close together
            if len(direction_changes) == 0 or i - direction_changes[-1] > 10:
                direction_changes.append(i)
    
    # Create step function for velocity
    time_extended = []
    vel_extended = []
    
    for idx, change_point in enumerate(direction_changes):
        vel_amplitude = 60.0 if idx % 2 == 0 else -60.0  # Alternate +60, -60, +60, -60...
        
        # Add vertical transition at direction change - convert to milliseconds
        time_extended.extend([change_point * 50, change_point * 50])
        if idx == 0:
            vel_extended.extend([0, vel_amplitude])  # Start from 0 for first step
        else:
            prev_amplitude = -vel_amplitude  # Previous amplitude (opposite sign)
            vel_extended.extend([prev_amplitude, vel_amplitude])
        
        # Continue at this level until next change (or end)
        if idx < len(direction_changes) - 1:
            next_change = direction_changes[idx + 1]
            time_extended.append(next_change * 50)
            vel_extended.append(vel_amplitude)
        else:
            # Last segment - extend to end
            time_extended.append((len(gt_pos) - 1) * 50)
            vel_extended.append(vel_amplitude)
    
    # Convert to numpy arrays
    time_extended = np.array(time_extended)
    vel_extended = np.array(vel_extended)
    
    # Calculate velocity from dashed ground truth (df1_gt_rescaled) 
    # Extract plateau values and create step function
    velocities = []
    
    # Calculate velocity between consecutive points (50ms apart)
    for i in range(len(df1_gt_rescaled) - 1):
        pos_diff = df1_gt_rescaled[i + 1] - df1_gt_rescaled[i]
        # Handle circular wrapping for position differences > 180 degrees
        if pos_diff > 180:
            pos_diff -= 360
        elif pos_diff < -180:
            pos_diff += 360
        
        # Convert to velocity (deg/s): position_diff / time_diff
        velocity = pos_diff / 0.05  # 50ms = 0.05s
        velocities.append(velocity)
    
    # Find max and min velocities from calculated dashed velocities
    if len(velocities) > 0:
        max_velocity = max(velocities)
        min_velocity = min(velocities)
    else:
        max_velocity = 40.0
        min_velocity = -40.0
    
    # Create simple dashed step function alternating between max/min values
    # Use the same direction changes as the solid step function
    dashed_vel_extended = []
    dashed_time_extended = []
    
    for idx, change_point in enumerate(direction_changes):
        vel_amplitude = max_velocity if idx % 2 == 0 else min_velocity  # Alternate max/min
        
        # Add vertical transition at direction change - convert to milliseconds
        dashed_time_extended.extend([change_point * 50, change_point * 50])
        if idx == 0:
            dashed_vel_extended.extend([0, vel_amplitude])  # Start from 0 for first step
        else:
            prev_amplitude = min_velocity if vel_amplitude == max_velocity else max_velocity  # Previous amplitude (opposite)
            dashed_vel_extended.extend([prev_amplitude, vel_amplitude])
        
        # Continue at this level until next change (or end)
        if idx < len(direction_changes) - 1:
            next_change = direction_changes[idx + 1]
            dashed_time_extended.append(next_change * 50)
            dashed_vel_extended.append(vel_amplitude)
        else:
            # Last segment - extend to end
            dashed_time_extended.append((len(gt_pos) - 1) * 50)
            dashed_vel_extended.append(vel_amplitude)
    
    # Convert to numpy arrays
    dashed_time_extended = np.array(dashed_time_extended)
    dashed_vel_extended = np.array(dashed_vel_extended)
    
    # Plot solid step function (original)
    tax.plot(time_extended, vel_extended, linewidth=2, color='green', linestyle='-', label='Wide motion velocity')
    
    # Plot dashed step function (from dashed ground truth)
    tax.plot(dashed_time_extended, dashed_vel_extended, linewidth=2, color='green', linestyle='--', alpha=0.7, label='Limited motion velocity')
    
    tax.set_ylabel('Velocity\n(deg/s)', fontsize=16)
    tax.set_ylim([-70, 70])
    tax.tick_params(axis='y', which='major', labelsize=14)
    tax.grid(True)
    tax.set_xlim(ax.get_xlim())

    plt.tight_layout()
    plt.savefig("gv_validation_comparison_compressed.png")
    plt.show()

def analyze_tracking_performance(path1, path2, path3=None, path4=None, save_results=True):
    """
    Analyze tracking performance between bounded and unbounded models.
    
    Args:
        path1: Path to bounded model results (limited motion data)
        path2: Path to unbounded model results (limited motion data)
        path3: Path to bounded model results (wide motion data) - optional
        path4: Path to unbounded model results (wide motion data) - optional
        save_results: Whether to save statistical results to file
    
    Returns:
        stats_results: Dictionary containing all statistical analysis results
    """
    from scipy import stats
    from scipy.signal import find_peaks
    import matplotlib.pyplot as plt
    
    # Load data
    df1 = pd.read_csv(path1)  # Bounded model (limited motion)
    df2 = pd.read_csv(path2)  # Unbounded model (limited motion)
    
    # Optional wide motion data
    df3 = pd.read_csv(path3) if path3 else None
    df4 = pd.read_csv(path4) if path4 else None
    
    def circular_error(predicted, ground_truth):
        """Calculate circular error between predicted and ground truth positions."""
        error = predicted - ground_truth
        # Handle circular wraparound
        error = ((error + 180) % 360) - 180
        return np.abs(error)
    
    def detect_movement_phases(gt_positions, min_distance=5):
        """Detect up/down movement phases based on ground truth positions."""
        # Find peaks and troughs
        peaks, _ = find_peaks(gt_positions, distance=min_distance)
        troughs, _ = find_peaks(-gt_positions, distance=min_distance)
        
        # Combine and sort all turning points
        turning_points = np.sort(np.concatenate([peaks, troughs]))
        
        # Create phases: each phase is between consecutive turning points
        phases = []
        for i in range(len(turning_points) - 1):
            start_idx = turning_points[i]
            end_idx = turning_points[i + 1]
            phase_type = 'up' if gt_positions[end_idx] > gt_positions[start_idx] else 'down'
            phases.append({
                'start': start_idx,
                'end': end_idx,
                'type': phase_type,
                'start_pos': gt_positions[start_idx],
                'end_pos': gt_positions[end_idx]
            })
        
        return phases
    
    def analyze_dataset(bounded_df, unbounded_df, dataset_name):
        """Analyze a single dataset (limited or wide motion)."""
        results = {'dataset': dataset_name}
        
        # Calculate circular errors
        bounded_errors = circular_error(bounded_df['bump_pos'].values, bounded_df['gt_pos'].values)
        unbounded_errors = circular_error(unbounded_df['bump_pos'].values, unbounded_df['gt_pos'].values)
        
        # Overall statistics
        results['bounded_mean_error'] = np.mean(bounded_errors)
        results['bounded_std_error'] = np.std(bounded_errors)
        results['unbounded_mean_error'] = np.mean(unbounded_errors)
        results['unbounded_std_error'] = np.std(unbounded_errors)
        
        # Statistical tests
        # Paired t-test
        t_stat, t_pvalue = stats.ttest_rel(bounded_errors, unbounded_errors)
        results['ttest_statistic'] = t_stat
        results['ttest_pvalue'] = t_pvalue
        
        # Wilcoxon signed-rank test (non-parametric alternative)
        wilcoxon_stat, wilcoxon_pvalue = stats.wilcoxon(bounded_errors, unbounded_errors)
        results['wilcoxon_statistic'] = wilcoxon_stat
        results['wilcoxon_pvalue'] = wilcoxon_pvalue
        
        # Detect movement phases
        phases = detect_movement_phases(bounded_df['gt_pos'].values)
        results['num_phases'] = len(phases)
        
        # Phase-wise analysis
        phase_results = []
        for i, phase in enumerate(phases):
            start, end = phase['start'], phase['end']
            
            phase_bounded_errors = bounded_errors[start:end+1]
            phase_unbounded_errors = unbounded_errors[start:end+1]
            
            if len(phase_bounded_errors) > 1:  # Need at least 2 points for comparison
                phase_result = {
                    'phase_index': i,
                    'phase_type': phase['type'],
                    'duration': end - start + 1,
                    'bounded_mean_error': np.mean(phase_bounded_errors),
                    'unbounded_mean_error': np.mean(phase_unbounded_errors),
                    'error_difference': np.mean(phase_bounded_errors) - np.mean(phase_unbounded_errors)
                }
                
                # Statistical test for this phase (if enough data points)
                if len(phase_bounded_errors) >= 3:
                    try:
                        phase_t_stat, phase_t_pvalue = stats.ttest_rel(phase_bounded_errors, phase_unbounded_errors)
                        phase_result['phase_ttest_pvalue'] = phase_t_pvalue
                    except:
                        phase_result['phase_ttest_pvalue'] = np.nan
                else:
                    phase_result['phase_ttest_pvalue'] = np.nan
                
                phase_results.append(phase_result)
        
        results['phase_analysis'] = phase_results
        
        # Time window analysis (fixed windows)
        window_size = 20  # 20 timesteps = 1 second at 50ms per timestep
        window_results = []
        
        for start_idx in range(0, len(bounded_errors), window_size):
            end_idx = min(start_idx + window_size, len(bounded_errors))
            
            window_bounded_errors = bounded_errors[start_idx:end_idx]
            window_unbounded_errors = unbounded_errors[start_idx:end_idx]
            
            if len(window_bounded_errors) >= 3:  # Minimum data for meaningful comparison
                window_result = {
                    'window_start_ms': start_idx * 50,
                    'window_end_ms': end_idx * 50,
                    'bounded_mean_error': np.mean(window_bounded_errors),
                    'unbounded_mean_error': np.mean(window_unbounded_errors),
                    'error_difference': np.mean(window_bounded_errors) - np.mean(window_unbounded_errors)
                }
                window_results.append(window_result)
        
        results['window_analysis'] = window_results
        
        return results
    
    # Analyze both datasets
    stats_results = {}
    
    # Limited motion data analysis
    limited_results = analyze_dataset(df1, df2, 'limited_motion')
    stats_results['limited_motion'] = limited_results
    
    # Wide motion data analysis (if provided)
    if df3 is not None and df4 is not None:
        wide_results = analyze_dataset(df3, df4, 'wide_motion')
        stats_results['wide_motion'] = wide_results
    
    # Print summary results
    print("=== TRACKING PERFORMANCE ANALYSIS ===\n")
    
    for dataset_name, results in stats_results.items():
        print(f"--- {dataset_name.upper()} DATASET ---")
        print(f"Bounded model mean error: {results['bounded_mean_error']:.3f}° ± {results['bounded_std_error']:.3f}°")
        print(f"Unbounded model mean error: {results['unbounded_mean_error']:.3f}° ± {results['unbounded_std_error']:.3f}°")
        print(f"Error difference (bounded - unbounded): {results['bounded_mean_error'] - results['unbounded_mean_error']:.3f}°")
        print(f"Paired t-test p-value: {results['ttest_pvalue']:.6f}")
        print(f"Wilcoxon test p-value: {results['wilcoxon_pvalue']:.6f}")
        print(f"Number of movement phases detected: {results['num_phases']}")
        
        # Phase-wise summary
        if results['phase_analysis']:
            up_phases = [p for p in results['phase_analysis'] if p['phase_type'] == 'up']
            down_phases = [p for p in results['phase_analysis'] if p['phase_type'] == 'down']
            
            if up_phases:
                up_error_diff = np.mean([p['error_difference'] for p in up_phases])
                print(f"Up phases - average error difference: {up_error_diff:.3f}°")
            
            if down_phases:
                down_error_diff = np.mean([p['error_difference'] for p in down_phases])
                print(f"Down phases - average error difference: {down_error_diff:.3f}°")
        
        print()
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    dataset_names = list(stats_results.keys())
    for idx, (dataset_name, results) in enumerate(stats_results.items()):
        row = idx
        
        # Plot 1: Error comparison over time windows
        ax1 = axes[row, 0]
        windows = results['window_analysis']
        if windows:
            window_times = [w['window_start_ms'] for w in windows]
            bounded_errors = [w['bounded_mean_error'] for w in windows]
            unbounded_errors = [w['unbounded_mean_error'] for w in windows]
            
            ax1.plot(window_times, bounded_errors, 'r-', label='Bounded', linewidth=2)
            ax1.plot(window_times, unbounded_errors, 'orange', label='Unbounded', linewidth=2)
            ax1.set_xlabel('Time (ms)')
            ax1.set_ylabel('Mean Error (°)')
            ax1.set_title(f'{dataset_name.title()}: Error Over Time Windows')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Plot 2: Phase-wise comparison
        ax2 = axes[row, 1]
        phases = results['phase_analysis']
        if phases:
            phase_indices = [p['phase_index'] for p in phases]
            bounded_phase_errors = [p['bounded_mean_error'] for p in phases]
            unbounded_phase_errors = [p['unbounded_mean_error'] for p in phases]
            
            x_pos = np.arange(len(phase_indices))
            width = 0.35
            
            ax2.bar(x_pos - width/2, bounded_phase_errors, width, label='Bounded', color='red', alpha=0.7)
            ax2.bar(x_pos + width/2, unbounded_phase_errors, width, label='Unbounded', color='orange', alpha=0.7)
            
            ax2.set_xlabel('Movement Phase')
            ax2.set_ylabel('Mean Error (°)')
            ax2.set_title(f'{dataset_name.title()}: Error by Movement Phase')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels([f"{p['phase_type']}\n{p['phase_index']}" for p in phases], rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save results if requested
    if save_results:
        # Save detailed results to JSON
        import json
        with open('tracking_performance_analysis.json', 'w') as f:
            # Convert numpy types to regular Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, dict):
                    return {key: convert_numpy(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                return obj
            
            json.dump(convert_numpy(stats_results), f, indent=2)
        
        # Save summary CSV
        summary_data = []
        for dataset_name, results in stats_results.items():
            summary_data.append({
                'dataset': dataset_name,
                'bounded_mean_error': results['bounded_mean_error'],
                'bounded_std_error': results['bounded_std_error'],
                'unbounded_mean_error': results['unbounded_mean_error'],
                'unbounded_std_error': results['unbounded_std_error'],
                'error_difference': results['bounded_mean_error'] - results['unbounded_mean_error'],
                'ttest_pvalue': results['ttest_pvalue'],
                'wilcoxon_pvalue': results['wilcoxon_pvalue'],
                'num_phases': results['num_phases']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('tracking_performance_summary.csv', index=False)
        
        plt.savefig('tracking_performance_analysis.png', dpi=300, bbox_inches='tight')
        print("Results saved to:")
        print("- tracking_performance_analysis.json (detailed results)")
        print("- tracking_performance_summary.csv (summary table)")
        print("- tracking_performance_analysis.png (visualization)")
    
    plt.show()
    
    return stats_results

def change_velocity_offline(v, theta):
    """
    Brian2 implementation recreating the exact same behavior as sim_capocaccia_changeVelocity_offline.
    
    Args:
        v: Velocity amplitude parameter (used in sinusoidal velocity profile)
        theta: Initial angle position in degrees
    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable
   
    # Initialize Brian2 ring attractor (equivalent to the hardcoded one)
    neuron_eq = Equations(LIF_synapticDecay_xi_vel_eq, tau=10*ms, V_rest=-70*mV, sigma_noise=0.0*mV, tau_s=10*ms)
    ring = FaithfulBoundedRingAttractor(neuron_eq, w_sub=-10.333033268750986*mV, g_cosine=10.333033257636599*mV, limit_neuron=None)
    # ring = FaithfulBoundedRingAttractor(neuron_eq, w_sub=-82.1212*mV, g_cosine=82.8283*mV, limit_neuron=None)

    ring.ring_pool.run_regularly('V = clip(V, -80*mV, inf*volt)', dt=0.1*ms)
    
    # Set up simulation parameters
    dt = 0.1*ms
    defaultclock.dt = dt
    total_time_steps = 900  # 900 time steps = 900ms total
    simulation_time = total_time_steps * 1*ms  # 900ms total
    
    # Use same input parameters as other functions
    inputParams = {'I0': 80.00, 'targetPosition': theta, 'I_target': 10.0}
    
    # Calculate external input based on uniform input type (same as runSimulation)
    I_ext_array = np.zeros(ring.numNeurons) * mV
    I_ext_array += np.ones(ring.numNeurons) * inputParams['I0'] * mV  # Uniform input to all neurons
    
    # Add boost to target neuron
    target_index = ring._get_neuron_index(inputParams['targetPosition'], in_degrees=True)
    I_ext_array[target_index] += inputParams['I_target'] * mV
    
    # Store initial input for plotting
    initial_cue = I_ext_array / mV  # Convert back to dimensionless for plotting
    
    # Track data for plotting
    ground_truth_positions = []
    velocity_profile = []
    
    # Current position tracker
    current_position = theta
    
    # Setup monitors
    ring.spikeMonitor = SpikeMonitor(ring.ring_pool)
    state_monitor = StateMonitor(ring.ring_pool, 'V', record=True)
    
    localObjects = [ring.spikeMonitor, state_monitor]
    net = Network(ring.BrianObjects + localObjects)
    
    # 1. Initialization: run 50ms with velocity OFF and input ON
    ring.ring_pool.I_ext = I_ext_array
    ring.ring_synapses_asym.vel_in = 0
    ring.ring_synapses_asym.vel_on = False
    
    # Track the first 50ms with velocity = 0
    for _ in range(50):
        net.run(1*ms)
        velocity_profile.append(0)
        ground_truth_positions.append(current_position)
    
    # Remove target boost after initialization
    I_ext_array[target_index] -= inputParams['I_target'] * mV
    ring.ring_pool.I_ext = I_ext_array
    
    # Track the next 50ms with velocity = 0
    for _ in range(50):
        net.run(1*ms)
        velocity_profile.append(0)
        ground_truth_positions.append(current_position)
    
    # 2. Main simulation: run the full trajectory with velocity changes
    # Create velocity vector for the remaining simulation
    remaining_steps = total_time_steps - 100  # Already ran 100ms (2*50ms)
    
    for j in range(100, 900):  # Run until 900ms to get full 900 time points
        # Define acceleration and deceleration phases (same as original)
        accel_start = 180  # Start acceleration 20ms before main velocity phase
        accel_end = 200    # End acceleration at main velocity phase start
        decel_start = 780  # Start deceleration 20ms before velocity phase end
        decel_end = 800    # End deceleration at main velocity phase end
        
        # Calculate velocity based on phase
        if accel_start <= j < accel_end:
            # Acceleration phase: smooth transition from 0 to target velocity
            progress = (j - accel_start) / (accel_end - accel_start)  # 0 to 1
            # Use smooth sigmoid-like transition
            smooth_factor = 3 * progress**2 - 2 * progress**3  # smooth step function
            target_velocity = np.sin(j/200) * 2
            velocity = target_velocity * smooth_factor
            
        elif 200 <= j < 780:
            # Main velocity phase: normal sinusoidal velocity
            velocity = np.sin(j/200) * 2
            
        elif decel_start <= j < decel_end:
            # Deceleration phase: smooth transition from target velocity to 0
            progress = (j - decel_start) / (decel_end - decel_start)  # 0 to 1
            # Use smooth sigmoid-like transition (reverse)
            smooth_factor = 1 - (3 * progress**2 - 2 * progress**3)  # smooth step function (inverted)
            target_velocity = np.sin(j/200) * 2
            velocity = target_velocity * smooth_factor
            
        else:
            # No movement phase
            velocity = 0
        
        # Update position for ground truth tracking
        current_position -= velocity
        current_position = current_position % 360
        ground_truth_positions.append(current_position)
        velocity_profile.append(velocity)
        
        # Apply velocity to the network
        if velocity != 0:
            # Calculate alpha using the same functions as original
            if velocity > 0:
                alpha = 0.16*10 # Fixed alpha for positive velocities
            else:
                alpha = - 0.16*10 # Fixed alpha for negative velocities
            
            # Set velocity input with correct sign (same as runSimulation)
            velocity_input = alpha * velocity
            if velocity >= 0:
                ring.ring_synapses_asym.vel_in = velocity_input
            else:
                ring.ring_synapses_asym.vel_in = -velocity_input
            ring.ring_synapses_asym.vel_on = True
        else:
            ring.ring_synapses_asym.vel_in = 0
            ring.ring_synapses_asym.vel_on = False
        
        # Run one time step (1ms)
        net.run(1*ms)
    
    # Create the exact same plot as the original function
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create divider for axes with more spacing
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("left", size="12%", pad=0.3)
    rax = divider.append_axes("right", size="12%", pad=0.3)
    tax = divider.append_axes("top", size="18%", pad=0.3)
    
    # Create manual raster plot with millisecond x-axis
    total_sim_time = 900*ms  # 900 time steps * 1ms = 900ms
    
    # Get spike data
    spike_times_ms = np.array(ring.spikeMonitor.t / ms)
    spike_neurons_idx = np.array(ring.spikeMonitor.i)
    
    # Plot spikes as scatter plot with even bigger and bolder black markers
    ax.scatter(spike_times_ms, spike_neurons_idx, s=6.0, c='black', marker='|', linewidths=2.0)
    ax.set_xlim(0, 900)  # Set x-axis from 0 to 900 ms
    ax.set_ylim(0, ring.numNeurons)
    
    # Add square highlighting the time window for firing rate computation (600-650 ms)
    time_start_ms, time_end_ms = 600, 650
    rect = plt.Rectangle((time_start_ms, 0), time_end_ms - time_start_ms, ring.numNeurons, 
                        linewidth=2, edgecolor='red', facecolor='red', alpha=0.1)
    ax.add_patch(rect)
    
    # Add box highlighting the input period (0-100 ms) in dark orange
    input_start_ms, input_end_ms = 0, 100
    input_rect = plt.Rectangle((input_start_ms, 0), input_end_ms - input_start_ms, ring.numNeurons, 
                              linewidth=3, edgecolor='darkorange', facecolor='darkorange', alpha=0.1)
    ax.add_patch(input_rect)
    
    # Plot ground truth as blue scatter points starting from 0ms
    time_points_ms = np.arange(len(ground_truth_positions))  # Start from 0ms
    # Convert ground truth positions to pixel coordinates (0-120 range)
    gt_pixels = np.array(ground_truth_positions) * ring.numNeurons / 360
    ax.scatter(time_points_ms, gt_pixels, c='C0', s=10, label='Ground Truth', alpha=0.8)
    
    # Add a dummy plot for spikes legend entry
    ax.scatter([], [], c='black', s=20, marker='s', label='Spikes')
    
    # Set up main axis with bold text (removed y-axis title)
    ax.set_xlabel("Time (ms)", fontsize=18)
    ax.legend(fontsize=16)
    ax.grid(True)
    
    # Remove y-axis ticks and labels from main raster plot
    ax.set_yticks([])
    ax.set_yticklabels([])
    # Ensure x-axis labels are visible and properly sized
    ax.tick_params(axis='x', labelsize=16, colors='black')
    
    # Plot velocity profile on top axis starting from 0ms
    velocity_time_ms = np.arange(len(velocity_profile))  # Start from 0ms
    tax.plot(velocity_time_ms, velocity_profile, 'g-', linewidth=3, label='Velocity')
    tax.set_ylabel("Velocity\n(deg/ms)", fontsize=16)
    tax.set_xlim(0, 900)  # Match main plot x-limits
    tax.set_xticklabels([])  # Remove x-axis labels for cleaner look
    tax.grid(True)
    # Add y-axis labels for velocity
    tax.tick_params(axis='y', labelsize=14)
    # Ensure velocity plot is visible
    if len(velocity_profile) > 0:
        y_margin = (max(velocity_profile) - min(velocity_profile)) * 0.1
        tax.set_ylim(min(velocity_profile) - y_margin, max(velocity_profile) + y_margin)
    
    # Compute and plot firing rate profile on right axis (600-650 ms)
    spike_times_ms = np.array(ring.spikeMonitor.t / ms)
    spike_neurons_idx = np.array(ring.spikeMonitor.i)
    
    # Filter spikes in the time window
    time_mask = (spike_times_ms >= time_start_ms) & (spike_times_ms <= time_end_ms)
    firing_rate = np.zeros(ring.numNeurons)
    for neuron_idx in range(ring.numNeurons):
        neuron_spikes = np.sum((spike_neurons_idx[time_mask] == neuron_idx))
        firing_rate[neuron_idx] = neuron_spikes / ((time_end_ms - time_start_ms) * 1e-3)  # Convert to Hz
    
    # Plot firing rate profile with bold text
    angle_positions = np.linspace(0, ring.numNeurons, len(firing_rate))  # Normal orientation: 0 to 120
    rax.plot(firing_rate, angle_positions, 'r-', linewidth=2)
    rax.set_xlabel("Firing\nRate (Hz)", fontsize=16)
    rax.set_ylim(0, ring.numNeurons)
    # Remove y-axis ticks and labels from firing rate plot
    rax.set_yticks([])
    rax.set_yticklabels([])
    rax.tick_params(axis='x', labelsize=14)
    rax.grid(True)
    
    # Plot initial input cue on left axis - fix the conversion and make visible
    angle_axis = np.linspace(0, 360, len(initial_cue))
    # Convert to milliamps properly - initial_cue is in volts, convert to mA
    initial_cue_ma = initial_cue  # Convert from A to mA
    # Plot with correct orientation (0° at bottom, 360° at top)
    cax.plot(initial_cue_ma, np.linspace(0, ring.numNeurons, len(initial_cue)), color='darkorange', linewidth=3)
    cax.set_xlabel("Input Current\n(mA)", fontsize=16)
    # Set appropriate x-axis limits - fix the scale issue
    cax.set_xlim(np.min(initial_cue_ma)-10, np.max(initial_cue_ma)+5)  # Scale back to reasonable range
    cax.set_ylim(0, ring.numNeurons)
    
    # Set y-axis ticks to show angles with 0° at bottom
    angle_ticks = np.arange(0, ring.numNeurons + 1, 20)
    angle_labels = [int(tick * 360 / ring.numNeurons) for tick in angle_ticks]
    cax.set_yticks(angle_ticks)
    cax.set_yticklabels(angle_labels)
    cax.tick_params(axis='y', labelsize=14)
    cax.tick_params(axis='x', labelsize=14)
    # Add y-axis title "Angle (degree)" on the left with bold text and larger size
    cax.set_ylabel("Angle (degree)", fontsize=20)
    cax.invert_xaxis()
    cax.grid(True)
    
    plt.tight_layout()
    plt.savefig('brian2_prova.png') 
    plt.show()
    
    return ground_truth_positions, velocity_profile, ring.spikeMonitor

if __name__ == "__main__":
    # Define output directory for acceleration-aware training
    output_dir = "/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_no_boundary/target_velocity_training"
    
    # Train g(v) and h(a) functions from trajectory files
    # velocity_data = train_from_trajectory_files(
    #     folder_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck",
    #     output_dir=output_dir,
    #     training=True
    # )
    
    # Validate all trajectories using learned g(v) and h(a)
    # validation_results = validate_all_trajectories(
    #     folder_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck",
    #     output_dir=output_dir,
    #     velocity_data=None
    # )

    path1="/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_boundary/target_velocity_training/gv_validation_compressed_run_60.0.txt"
    path2="/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_no_boundary/target_velocity_training/gv_validation_compressed_run_60.0.txt"
    path3="/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_boundary/target_velocity_training/gv_validation_run_60.0.txt"
    path4="/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_no_boundary/target_velocity_training/gv_validation_run_60.0.txt"
    plot_comparison(path1=path1,path2=path2, path3=path3,path4=path4)
    
    # Perform statistical analysis comparing bounded vs unbounded models
    stats_results = analyze_tracking_performance(
        path1=path1,  # Bounded model (limited motion)
        path2=path2,  # Unbounded model (limited motion)
        path3=path3,  # Bounded model (wide motion)
        path4=path4,  # Unbounded model (wide motion)
        save_results=True
    )
    
    change_velocity_offline(v=2, theta=90)
    
    print("Training and validation with acceleration complete!")
