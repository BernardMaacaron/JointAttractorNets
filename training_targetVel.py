
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
from neuronModels import LIF_xi_vel_eq

tools_path = os.path.join(os.path.dirname(__file__), 'Tools')
sys.path.append(tools_path)
from utils import computeInstRate, computePVA
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

    # 2. Main simulation: for each entry in velocity_vector, run 50ms with correct sign
    pva_angle_vec = []
    pva_magnitude_vec = []
    if training:
        velocity_vector=velocity_vector[:200]
    if velocity_vector is not None:
        for v in velocity_vector:
            # Set velocity input sign
            if v >= 0:
                ringAttractor.ring_synapses_asym.vel_in = (velInput)
            else:
                ringAttractor.ring_synapses_asym.vel_in = -(velInput)
            ringAttractor.ring_synapses_asym.vel_on = True
            net.run(50*ms)
            firingRates = computeInstRate(ringAttractor.spikeMonitor, ringAttractor.numNeurons, meanISI = True)
            pva_angle, pva_magnitude = computePVA(firingRates, ringAttractor.positions)
            pva_angle_vec.append(pva_angle)
            pva_magnitude_vec.append(pva_magnitude)
        simTime = 50*ms + len(velocity_vector)*50*ms
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
        pva_angle_vec.append(pva_angle-np.deg2rad(44)) # Remove offset of 44 degrees
        # pva_angle_vec.append(pva_angle)
        pva_magnitude_vec.append(pva_magnitude)
        simTime = runTime + 50*ms

    if device == 'cpp_standalone':
        device.build(directory = 'internalSim_build', compile=True, run=True, debug=False, clean=False)

    if plot:
        raster_plot(ringAttractor.spikeMonitor,duration=simTime, num_neurons=ringAttractor.numNeurons, y_axisFull=True)

    return pva_angle_vec, pva_magnitude_vec
    

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
    neuron_eq = Equations(LIF_xi_vel_eq, tau=10*ms, V_rest=-70*mV, sigma_noise=0.0*mV)
    limit_joint=np.deg2rad(88)
    limit_neuron=np.round((limit_joint*120)/(2*np.pi))
    ring= FaithfulBoundedRingAttractor(neuron_eq,  
                        w_sub=-0.33478*mV,
                        g_cosine=0.33496*mV,
                        limit_neuron=int(limit_neuron))
    
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
    inputParams = {'I0': 80.00, 'targetPosition': initial_target_position+44, 'I_target': 10.0}
    # inputParams = {'I0': 80.00, 'targetPosition': initial_target_position, 'I_target': 10.0}
    velocityInput = alpha_value * tv 
    # Run the simulation once for the whole trajectory
    pva_angle_vec, pva_magnitude_vec = runSimulation(
        ringAttractor=ring, device=None, dt=dt,
        inputParams=inputParams, inputType='Uniform',
        velInput=velocityInput, runTime=50*ms, plot=False, flag=True,
        velocity_vector=velocity_vector,training=training)

    # Convert pva_angle_vec to degrees for output, but keep radians for error calculation
    bump_positions = np.rad2deg(pva_angle_vec)
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
        bounds=(-1.0, 1.0),
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
            velocity_data = pd.read_csv("/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_boundary/target_velocity_training/velocity_alpha_mapping.csv")
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
            bump_pos = bump_pos - 44
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
            # plt.savefig(os.path.join(output_dir, f"gv_validation_{os.path.basename(file_path).split('.')[0]}.png"))
            plt.close()

        except Exception as e:
            print(f"Error validating file {file_path}: {e}")

    # Save validation results
    validation_df = pd.DataFrame(validation_results)
    validation_df.to_csv(os.path.join(output_dir, "validation_results.csv"), index=False)
    print("Validation results saved to validation_results.csv")

    return validation_df



if __name__ == "__main__":
    # Define output directory for acceleration-aware training
    output_dir = "/home/fferrari-iit.local/JointAttractorNets/Results_Training/Network_boundary/target_velocity_training"
    
    # Train g(v) and h(a) functions from trajectory files
    # velocity_data = train_from_trajectory_files(
    #     folder_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck",
    #     output_dir=output_dir,
    #     training=True
    # )
    
    # Validate all trajectories using learned g(v) and h(a)
    validation_results = validate_all_trajectories(
        folder_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck",
        output_dir=output_dir,
        velocity_data=None
    )
    
    print("Training and validation with acceleration complete!")
