from brian2 import *

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
    if total_rate == 0:
        return 0.0, 0.0

    weighted_sum = np.sum(firing_rates * np.exp(1j * positions))
    pva_angle = np.angle(weighted_sum)
    pva_magnitude = np.abs(weighted_sum) / total_rate
    return pva_angle, pva_magnitude