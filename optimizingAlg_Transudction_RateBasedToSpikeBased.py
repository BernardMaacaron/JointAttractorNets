"""
Bridge energy-landscape (rate-based) optimization outputs to a spike-based model.

What this does
--------------
Given the rate-optimized gains (JE, JI) from `optimizingAlg.optimizeMatrixGains`,
this module maps them into spike-based synaptic weights for a Brian2 LIF network.
The end-to-end steps are:

1) From a constant injected current I_ff, compute a baseline firing rate f_ff using the
     closed-form LIF rate function I2f.
2) Convert the optimizer gains to per-neuron target frequencies:
     f_target_Je = JE * f_ff / N and f_target_Ji = |JI| * f_ff / N. Here JE, JI are
     unitless gains returned by the optimizer (JI typically negative; we use |JI|).
3) Convert these target frequencies back to the required constant input currents via f2I.
4) Treat those targets as a total synaptic contribution G and invert the relation
     G = g * tau_synapse * f to obtain the synaptic weight g.

Core relations
--------------
- Total contribution:       G = g * tau_synapse * f
- Inverse for synaptic g:   g = G / (tau_synapse * f)
- LIF analytical rate (noise-free):
        f = 1 / (tau * ln((V_ss - V_reset) / (V_ss - V_th)) + tau_refrac),
        with V_ss = V_rest + R * I_ext.

Units and conventions
---------------------
- We use Brian2 quantities throughout (mV, ms, Hz, ohm, A, etc.).
- G and g are treated here as voltage-equivalent quantities for convenience, so using
    R = 1 Ω maps A ↔ V. In practice this ensures dimensional consistency with the
    formula G = g * tau_synapse * f used in the codebase.
- Consistency note: in the Je path we convert currents to volts via "* ohm" before
    solving for g. Historically, some code paths treated Ji directly as volts without
    multiplying by ohm. The `main()` demo prints both paths, with Ji shown in its
    legacy convention for backwards comparability; the helper conversion function
    uses the consistent "* ohm" mapping for both Je and Ji.
"""

from __future__ import annotations

import numpy as np
from brian2 import *  # Units and Brian2 quantities (e.g., mV, ms, Hz, ohm)

# Import optimization routine from local module
import optimizingAlg as opt


# ---------------------------------------------------------------------------
# Total synaptic contribution G and its inverse mapping to synaptic weight g
# ---------------------------------------------------------------------------

def total_contribution(g: Quantity, f: Quantity, tau_synapse: Quantity = 5 * ms) -> Quantity:
    """
    Total postsynaptic contribution from one presynaptic source.

    Relation: G = g * tau_synapse * f

    Parameters
    ----------
    g : Quantity [volt]
        Voltage-equivalent synaptic weight per spike.
    f : Quantity [Hz]
        Presynaptic firing rate.
    tau_synapse : Quantity [second], optional
        Synaptic decay (or effective integration) time constant.

    Returns
    -------
    Quantity [volt]
        Total contribution G (voltage-equivalent) implied by (g, f, tau_synapse).
    """
    return g * tau_synapse * f


def synaptic_weight_from_totalContribution(G: Quantity, f: Quantity, tau_synapse: Quantity = 5 * ms) -> Quantity:
    """
    Invert G = g * tau_synapse * f to recover the synaptic weight g.

    Parameters
    ----------
    G : Quantity [volt]
        Target total contribution (voltage-equivalent).
    f : Quantity [Hz]
        Presynaptic firing rate.
    tau_synapse : Quantity [second], optional
        Synaptic decay (or effective integration) time constant.

    Returns
    -------
    Quantity [volt]
        Synaptic weight g such that total_contribution(g, f, tau_synapse) == G.
    """
    return G / (f * tau_synapse)


# ---------------------------------------------------------------------------
# LIF analytical rate and its inverse (I <-> f)
# ---------------------------------------------------------------------------

def I2f(
    I_ext: Quantity,
    tau: Quantity = 10 * ms,
    tau_refrac: Quantity = 5 * ms,
    V_rest: Quantity = -70 * mV,
    Vth: Quantity = -48 * mV,
    V_reset: Quantity = -80 * mV,
    R: Quantity = 1.0 * ohm,
) -> Quantity:
    """
    Closed-form firing rate for a noise-free LIF neuron driven by constant current.

    Parameters
    ----------
    I_ext : Quantity [ampere]
        External injected current.
    tau : Quantity [second]
        Membrane time constant.
    tau_refrac : Quantity [second]
        Absolute refractory period.
    V_rest : Quantity [volt]
        Resting potential.
    Vth : Quantity [volt]
        Threshold potential.
    V_reset : Quantity [volt]
        Reset potential.
    R : Quantity [ohm]
        Membrane resistance.

    Returns
    -------
    Quantity [Hz]
        Firing rate. Returns 0 Hz if the steady-state voltage V_ss = V_rest + R*I_ext
        does not cross threshold.
    """
    V_ss = V_rest + R * I_ext  # Steady-state voltage

    # If steady-state does not reach threshold, no spiking
    if V_ss <= Vth:
        return 0.0 * Hz

    # f = 1 / (tau * ln((V_ss - V_reset) / (V_ss - Vth)) + tau_refrac)
    try:
        interspike_interval = tau * np.log((V_ss - V_reset) / (V_ss - Vth)) + tau_refrac
        if interspike_interval <= 0:
            return 0.0 * Hz
        return 1 / interspike_interval
    except Exception:
        return 0.0 * Hz


def f2I(
    freq: Quantity,
    tau: Quantity = 10 * ms,
    tau_refrac: Quantity = 5 * ms,
    V_rest: Quantity = -70 * mV,
    Vth: Quantity = -48 * mV,
    V_reset: Quantity = -80 * mV,
    R: Quantity = 1.0 * ohm,
) -> Quantity:
    """
    Inverse of I2f: for a desired firing rate (Hz), return the constant current I_ext.

    Derivation sketch (noise-free LIF)
    ----------------------------------
    Let d = 1/f - tau_refrac and k = exp(d/tau). From the LIF solution,
      (V_ss - V_reset) = k * (V_ss - Vth)  =>  V_ss = (V_reset - k * Vth) / (1 - k),
    and I_ext = (V_ss - V_rest) / R.

    Parameters
    ----------
    freq : Quantity [Hz]
        Desired firing rate.
    tau, tau_refrac, V_rest, Vth, V_reset, R : see I2f

    Returns
    -------
    Quantity [ampere]
        Required constant input current. Returns 0 mA if freq <= 0. May return inf
        in limiting cases where the target rate implies k → 1.
    """
    if freq <= 0:
        return 0.0 * mA

    d = 1 / freq - tau_refrac
    # If d/tau is extreme, k may overflow/underflow; rely on numpy/float behavior gracefully.
    try:
        k = np.exp(d / tau)
    except Exception:
        # Limits: k -> inf => V_ss -> Vth; k -> 0 => V_ss -> V_reset
        k = np.inf if float(d) > 0 else 0.0

    # Avoid division by zero when k ~ 1
    if np.isclose(k, 1.0):
        # In the limit k -> 1, denominator -> 0; firing rate -> infinity => I_ext large
        return np.inf

    V_ss = (V_reset - k * Vth) / (1.0 - k)
    return (V_ss - V_rest) / R

def conversion_to_spike_based(
    JE: float,
    JI: float,
    N: int,
    f_ff: Quantity,
    tau_s: Quantity,
    Vrest: Quantity,
    Vth: Quantity,
    V_reset: Quantity,
    refractory_period: Quantity,
    tau: Quantity,
) -> tuple[Quantity, Quantity]:
    """
    Convert rate-optimized gains (JE, JI) to spike-based synaptic weights (g_Je, g_Ji).

    Pipeline: (i) target per-neuron frequencies from JE/JI and f_ff; (ii) recover the
    required constant currents via f2I; (iii) treat currents as total contribution G and
    solve for g using G = g * tau_synapse * f.

    Parameters
    ----------
    JE, JI : float (unitless)
        Optimizer gains. JI is typically negative; we use abs(JI) for frequencies.
    N : int
        Number of neurons in the ring/network used for normalization.
    f_ff : Quantity [Hz]
        Baseline feed-forward firing rate.
    tau_s : Quantity [second]
        Synaptic decay/integration constant used in the G↔g relation.
    Vrest, Vth, V_reset : Quantity [volt]
        Resting, threshold, and reset potentials for the LIF mapping.
    refractory_period : Quantity [second]
        Absolute refractory period.
    tau : Quantity [second]
        Membrane time constant.

    Returns
    -------
    tuple[Quantity, Quantity]
        Synaptic weights (g_Je, g_Ji) in voltage-equivalent units.

    Notes
    -----
    For dimensional consistency we convert both I_target_Je and I_target_Ji to volts using "* ohm"
    before applying the G↔g formula. This aligns with the Je path in main() and avoids the legacy
    special case for Ji.
    """
    # Compute the target frequencies per neuron
    f_target_Je = JE * f_ff / N
    f_target_Ji = np.abs(JI) * f_ff / N

    # Convert frequencies to required currents
    I_target_Je = f2I(freq=f_target_Je, tau=tau, tau_refrac=refractory_period, V_rest=Vrest, Vth=Vth, V_reset=V_reset)
    I_target_Ji = f2I(freq=f_target_Ji, tau=tau, tau_refrac=refractory_period, V_rest=Vrest, Vth=Vth, V_reset=V_reset)

    # Interpret currents as total contributions (map A → V via R=1 Ω)
    G_target_Je = I_target_Je * ohm
    G_target_Ji = I_target_Ji * ohm

    # Compute synaptic weights
    g_Je = synaptic_weight_from_totalContribution(G=G_target_Je, f=f_ff, tau_synapse=tau_s)
    g_Ji = synaptic_weight_from_totalContribution(G=G_target_Ji, f=f_ff, tau_synapse=tau_s)

    return g_Je, g_Ji

def main() -> None:
    """
    Demonstration of the end-to-end conversion with printed outputs only.

    Steps shown:
    1) Set network size and optimizer params; define LIF and synaptic constants.
    2) Compute baseline rate f_ff from a constant current I_ff using I2f.
    3) Run optimizer to obtain (JE, JI).
    4) Convert to target per-neuron rates, then to currents via f2I.
    5) Convert currents to total contribution and solve for synaptic weights.

    Consistency note:
    - Je path: G_target_Je = I_target_Je * ohm (recommended).
    - Ji path below keeps the legacy behavior G_target_Ji = I_target_Ji (without "* ohm")
      to illustrate the historical convention; prefer multiplying by ohm for consistency.
    """

    # --- Optimization parameters ---
    N = 12
    cff = 1.0
    A = 0.6
    Nact = N // 2

    # --- LIF neuron parameters ---
    Vrest = -70 * mV
    Vth = -48 * mV
    V_reset = -80 * mV
    refractory_period = 5 * ms
    tau = 10 * ms
    tau_s = 13 * ms

    # --- Feed-forward input and baseline firing rate ---
    I_ff = 80.0 * mA
    print(f"Constant current feed-forward: I_ff = {I_ff}")
    f_ff = I2f(I_ext=I_ff, tau=tau, tau_refrac=refractory_period, V_rest=Vrest, Vth=Vth, V_reset=V_reset)
    print(f"Baseline frequency: f_ff = {f_ff}")

    # --- Run optimizer to get JE and JI ---
    JE_chosen, JI_chosen = opt.optimizeMatrixGains(N, cff=cff, A=A, Nact=Nact)
    print("\n*** Optimization Results ***")
    print(f"JE_chosen = {JE_chosen}")
    print(f"JI_chosen = {JI_chosen}")

    # --- Conversion to spike-based weights (excitatory path) ---
    print("\n*** Je conversion ***")
    f_target_Je = JE_chosen * f_ff / N
    print(f"Target frequency per neuron (Je): f_target_Je = {f_target_Je}")
    I_target_Je = f2I(freq=f_target_Je, tau=tau, tau_refrac=refractory_period, V_rest=Vrest, Vth=Vth, V_reset=V_reset)
    print(f"Required current (Je): I_target_Je = {I_target_Je}")

    # Interpret current as a voltage-equivalent total contribution (via R=1 Ω)
    # so that it matches the units of G in the contribution formula.
    G_target_Je = I_target_Je * ohm
    g_Je = synaptic_weight_from_totalContribution(G=G_target_Je, f=f_ff, tau_synapse=tau_s)
    print(f"Synaptic weight (Je): g_Je = {g_Je}")

    # --- Conversion to spike-based weights (inhibitory path) ---
    print("\n*** Ji conversion ***")
    f_target_Ji = np.abs(JI_chosen) * f_ff / N
    print(f"Target frequency per neuron (Ji): f_target_Ji = {f_target_Ji}")
    I_target_Ji = f2I(freq=f_target_Ji, tau=tau, tau_refrac=refractory_period, V_rest=Vrest, Vth=Vth, V_reset=V_reset)
    print(f"Required current (Ji): I_target_Ji = {I_target_Ji}")

    # NOTE: For consistency with the Je path, one would typically multiply by ohm here as well
    # (G_target_Ji = I_target_Ji * ohm). The original code interpreted this directly as volts.
    G_target_Ji = I_target_Ji * ohm
    g_Ji = synaptic_weight_from_totalContribution(G=G_target_Ji, f=f_ff, tau_synapse=tau_s)
    print(f"Synaptic weight (Ji): g_Ji = {g_Ji}")


if __name__ == "__main__":
    main()
