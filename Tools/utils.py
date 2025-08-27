from brian2 import *
from brian2.parsing.sympytools import str_to_sympy
import sys
from lmfit import Model, Parameters
from sympy.plotting import plot as sympy_plot

class ProgressBar(object):
    def __init__(self, toolbar_width=40):
        self.toolbar_width = toolbar_width
        self.ticks = 0

    def __call__(self, elapsed, complete, start, duration):
        if complete == 0.0:
            # setup toolbar
            sys.stdout.write("[%s]" % (" " * self.toolbar_width))
            sys.stdout.flush()
            sys.stdout.write("\b" * (self.toolbar_width + 1)) # return to start of line, after '['
        else:
            ticks_needed = int(round(complete * self.toolbar_width))
            if self.ticks < ticks_needed:
                sys.stdout.write("-" * (ticks_needed-self.ticks))
                sys.stdout.flush()
                self.ticks = ticks_needed
        if complete == 1.0:
            sys.stdout.write("\n")

def extract_spikeData(spike_input):
    """
    Helper function to extract spike data from either a Brian2 SpikeMonitor or a tuple.
    
    Parameters:
    ----------
    spike_input : Brian2 SpikeMonitor or tuple
        Either a SpikeMonitor object or a tuple of (spike_ids, spike_times)
        
    Returns:
    -------
    tuple : (spike_ids, spike_times, is_quantity)
        - spike_ids: array of neuron indices
        - spike_times: array of spike times (in seconds or as Brian2 Quantity)
        - is_quantity: boolean indicating if spike_times is a Brian2 Quantity
    """
    if hasattr(spike_input, 't') and hasattr(spike_input, 'i'):
        # It's a Brian2 SpikeMonitor
        return spike_input.i, spike_input.t, True
    else:
        # It's a tuple of (spike_ids, spike_times)
        spike_ids, spike_times = spike_input
        # Check if spike_times is a Brian2 Quantity
        hasBrianUnit = not is_dimensionless(spike_times)
        print("spike_times is a Brian2 Quantity:", hasBrianUnit)
        return spike_ids, spike_times, hasBrianUnit

def computeFiringRate(spikemon, n_neurons, start_time=None, end_time=None, total_duration=None):
    """
    Compute the firing rate for each neuron from a Brian2 SpikeMonitor or tuple of (spike_ids, spike_times).

    Parameters:
        spikemon : Brian2 SpikeMonitor or tuple
            Monitor containing spike data or a tuple of (spike_ids, spike_times).
        n_neurons : int
            Number of neurons in the network.
        start_time : float or Brian2 Quantity, optional
            Start time (in seconds) for firing rate calculation.
        end_time : float or Brian2 Quantity, optional
            End time (in seconds) for firing rate calculation.
        total_duration : float or Brian2 Quantity, optional
            Duration to use if no time window is provided.

    Returns:
        numpy.ndarray
            Array of firing rates (Hz) for each neuron.
    """
    # Use the helper function to extract spike data
    spike_ids, spike_times, hasBrianUnit = extract_spikeData(spikemon)
    
    # Check if there are no spikes
    if len(spike_times) == 0.0:
        return np.zeros(n_neurons)
    
    # Convert to seconds if needed
    if hasBrianUnit:
        spike_times = spike_times/second
        if start_time is not None:
            start_time = start_time/second
        if end_time is not None:
            end_time = end_time/second
        if total_duration is not None:
            total_duration = total_duration/second
    
    # Determine time window
    if (start_time is not None) and (end_time is not None):
        window_mask = (spike_times >= start_time) & (spike_times < end_time)
        filtered_indices = spike_ids[window_mask]
        duration_used = end_time - start_time
    else:
        filtered_indices = spike_ids
        if total_duration is not None:
            duration_used = total_duration
        elif len(spike_times) > 0:
            duration_used = np.max(spike_times)
    
    # Count spikes for each neuron
    rates = np.zeros(n_neurons)
    unique_indices, spike_counts = np.unique(filtered_indices, return_counts=True)
    
    # Assign counts to the corresponding neurons
    rates[unique_indices] = spike_counts / duration_used
    
    return rates

def computeInstRate(spikemon, numNeurons, meanISI=True):
    """
    Compute the instantaneous firing rate for each neuron from a Brian2 SpikeMonitor.

    Parameters:
        spikemon : Brian2 SpikeMonitor
            Monitor containing spike data.
        numNeurons : int
            Number of neurons in the network.
        meanISI : bool
            If True, return the mean interspike interval (ISI) as the instantaneous firing rate.

    Returns:
        numpy.ndarray
            Array of instantaneous firing rates (Hz) for each neuron.
    """

    spike_ids, spike_times, hasBrianUnit = extract_spikeData(spikemon)
    
    # Check if the spike monitor is empty
    if len(spike_times) == 0.0:
        return np.zeros(numNeurons)

    if hasBrianUnit:
        spike_times = spike_times/second
        
    # Count spikes for each neuron
    rates = [0.0] * numNeurons
    unique_indices, spike_counts = np.unique(spike_ids, return_counts=True)
    
    
    for index in unique_indices:
        # Find the interspike interval (ISI)
        isi = np.diff(spike_times[spike_ids == index])
        if len(isi) > 0:
            if meanISI:
                rates[index] = 1.0 / np.mean(isi)
            else:
                rates[index] = 1 / isi
    return np.asarray(rates)

def calculate_PVA(firing_rates, positions):
    """
    Calculate the Population Vector Average (PVA) from firing rates and neuron positions.

    Parameters:
        firing_rates (array-like): Firing rates for each neuron.
        positions (array-like): Neuron positions (angles in radians).

    Returns:
        tuple: (pva_angle, pva_magnitude)
            - pva_angle: The circular mean angle.
            - pva_magnitude: The normalized magnitude (0 to 1) indicating concentration.
    """
    total_rate = np.sum(firing_rates)
    if total_rate == 0.0:
        return 0.0, 0.0

    weighted_sum = np.sum(firing_rates * np.exp(1j * positions))
    pva_angle = np.angle(weighted_sum)
    pva_magnitude = np.abs(weighted_sum) / total_rate
    return pva_angle, pva_magnitude



#################################################
# Error Metrics
#################################################
def conf_weighted_CE(pva_angle, stimulus_center, pva_magnitude=None, epsilon=1e-8):
    """
    Calculate the absolute circular error between the PVA angle and the stimulus center.
    Subsequently, if pva_magnitude is not None, calculates the Confidence Weighted Center Error
    CWCE: Weights the center error by the normalized PVA magnitude
    This metric penalizes the center error based on the distribution of firing rates
    If the PVA magnitude is low, the penalty is higher and vice versa

    Parameters:
        stimulus_center (float): The expected center angle of the stimulus.
        pva_angle (float): The computed PVA angle from the network.
        pva_magnitude (float, optional): The normalized magnitude of the PVA. If None, only the center error is returned.
        If provided, it is used to compute the CWCE.

    Returns:
        tuple: (center_error, cwce) if pva_magnitude is provided,
               else returns only center_error.
               - center_error: The absolute circular error between the PVA angle and the stimulus center.
               - cwce: The confidence weighted center error.        
    """
    # Compute the circular difference between pva_angle and stimulus_center
    center_error = np.abs(np.angle(np.exp(1j * (pva_angle - stimulus_center))))
    
    if pva_magnitude is None:
        return center_error
    else:
        # Compute the confidence weighted center error
        cwce = center_error / (pva_magnitude + epsilon)
        return center_error, cwce    

def compute_nmse_normalized(observed_rates, ideal_input, norm_type='max'):
    """
    Compute the NMSE between normalized observed and ideal firing rate profiles.

    Parameters:
        observed_rates (numpy.ndarray): Observed firing rates.
        ideal_input (numpy.ndarray): Ideal input firing rate profile.
        norm_type (str): Type of normalization ('max' or 'area').
    
    Returns:
        float: The computed NMSE.
    """
    if len(observed_rates) != len(ideal_input):
        raise ValueError("Observed rates and ideal input must have the same length.")
    if np.sum(observed_rates) == 0:
        return np.nan
    
    if norm_type == 'max':
        normalized_ideal = ideal_input / np.max(ideal_input)
        normalized_obs = observed_rates / np.max(observed_rates)
    elif norm_type == 'area':
        normalized_ideal = ideal_input / np.sum(ideal_input)
        normalized_obs = observed_rates / np.sum(observed_rates)
    else:
        raise ValueError("Normalization type not recognized. Use 'max' or 'area'.")
    
    numerator = np.sum((normalized_obs - normalized_ideal) ** 2)
    denominator = np.sum(normalized_ideal ** 2)
    nmse = numerator / denominator
    return nmse


#################################################
# Curve Fitting
#################################################
def rect_power(V, a, V0, p):
    """Rectified power-law: phi(V) = max(a*V - V0, 0)**p"""
    return np.maximum(a*V - V0, 0.0)**p

def rect_powerInt(V, a, V0, p):
    """Integral of the activation function (rect_power)
    Phi(V) = (a/1+p)*(V - V0/a)**(p+1)"""
    power = p+1
    return (a/power)*np.maximum((V - V0/a),0.0)**(power)

def curveFit_rectPower(firing_rates, input_data, V0=None):
    mod = Model(rect_power, independent_vars=['V'])
    params = Parameters()
    params.add('a', value=1.0, min=0)       # gain must be ≥0
    params.add('V0', value=V0)           # threshold in volts
    params.add('p', value=1.0, vary=False)       # exponent must be ≥0
    result = mod.fit(firing_rates, params, V=input_data)
    return result, result.best_values

##################################################
# Analytical Evaluations
##################################################
#TODO: Finalize this function
def analytical_FiringRate(model: str, variableRange): #Work in Progress
    """
    Compute the analytical firing rate for a given neuron model.
    Neuron model has to be a brian2 neuron equation of the form.
    
    Parameters:
        model (str): Neuron model equation.
        refractory (float): Refractory period in seconds.
    """
    return "This function is a work in progress and not yet implemented."

    ##### Prepare and validate equations
    if isinstance(model, str):
        model = Equations(model)
    if not isinstance(model, Equations):
        raise TypeError(
            "model has to be a string or an Equations "
            f"object, is '{type(model)}' instead."
        )
    for eq in model.diff_eq_expressions:
        for var in eq:
            if not isinstance(var, str):
                symEq = str_to_sympy(str(var))
                sympy_plot(symEq)

