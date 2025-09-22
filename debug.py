import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import pandas as pd

from brian2 import *

nsm_path = os.path.join(os.path.dirname(__file__), 'Neuron and Synapse Models')
sys.path.append(nsm_path)
from ringAttractorClassExtended import FaithfulBoundedRingAttractor
from neuronModels import LIF_xi_vel_eq

tools_path = os.path.join(os.path.dirname(__file__), 'Tools')
sys.path.append(tools_path)
from utils import computeInstRate, computePVA
from plottingTools import raster_plot
import glob


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
   
    velocity_vector=velocity_vector[:800]
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
        plt.show(block=True)  # Force the plot window to block execution until closed
        plt.savefig('raster_plot.png')
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
                        limit_neuron=None)
    
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

def validate_trajectory_with_gv(data_file, alpha):
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
    

    # Use the full trajectory and trained alpha for this velocity
    mse, bump_positions, gt_positions = simulate_with_trajectory(
        data, target_velocity, alpha)
    return mse, bump_positions, gt_positions


def validate_all_trajectories(file_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck/run_20.4.txt", alpha=None):
    """
    Validate all trajectories using the learned g(v) function.
    
    Args:
        folder_path: Path to folder containing trajectory files
        velocity_data: DataFrame with velocity -> optimal alpha mapping
                       (if None, load from csv)
    
    Returns:
        validation_results: DataFrame with validation metrics for each file
    """

 
       
    mse, bump_pos, gt_pos = validate_trajectory_with_gv(file_path, alpha)
    # bump_pos = bump_pos - 44
 

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
    plt.show()
    plt.savefig('trajectory_plot.png')




if __name__ == "__main__":
    validate_all_trajectories(
        file_path="/home/fferrari-iit.local/RingAttractor/Ring_Attractor_madeByMe/capocaccia/data_neck/run_20.4.txt",
        alpha=-0.087
    )