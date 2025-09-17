from brian2 import *
import numpy as np

# Reuse the existing RingAttractor implementation (support both package and flat usage)
try:
    from .ringAttractorClass import RingAttractor  # when used as a package
except Exception:
    from ringAttractorClass import RingAttractor   # when folder is on sys.path


class FaithfulRingAttractor(RingAttractor):
    """
    A variant of RingAttractor where inhibition is implemented by directly
    subtracting a constant inhibitory weight from the baseline connectivity
    profile, rather than introducing a separate global inhibitory neuron.

    This class mirrors the API of RingAttractor but ignores the `glob_inh`
    pathway. Instead, it applies a uniform subtractive inhibitory term to
    all synaptic weights after the baseline connectivity has been set.

    Parameters
    ----------
    neuron_eq : str or brian2.Equations
        Neuron model equations/string.
    N : int, optional
        Number of neurons on the ring (default 120).
    Vth : quantity, optional
        Spike threshold (default -48*mV).
    V_reset : quantity, optional
        Reset voltage (default -80*mV).
    refractory_period : quantity, optional
        Refractory period (default 5*ms).
    syn_profile : str, optional
        Connectivity profile ('mexican_hat', 'gaussian', 'cosine').
    autapse : bool, optional
        Whether to allow self-connections; default False.
    normalized : bool, optional
        If True, divide weights by N; default False. The subtractive term
        is also divided by N in this case to preserve scaling.
    w_sub : quantity, optional
        Magnitude of subtractive inhibition applied to all synapses.
        Default is 0.15*mV. The sign is ignored; subtraction uses abs(w_sub).
    mujoco : bool, optional
        Forwarded to base class; default False.
    **syn_params : dict
        Additional parameters for connectivity profiles, forwarded to base.
    """

    def __init__(
        self,
        neuron_eq,
        N=120,
        Vth=-48 * mV,
        V_reset=-80 * mV,
        refractory_period=5 * ms,
        syn_profile='cosine',
        autapse=True,
        normalized=False,
        w_sub=0.15 * mV,
        mujoco=False,
        **syn_params
    ):
        # Initialize base class with glob_inh disabled; we implement subtraction instead
        super().__init__(
            neuron_eq=neuron_eq,
            N=N,
            Vth=Vth,
            V_reset=V_reset,
            refractory_period=refractory_period,
            syn_profile=syn_profile,
            autapse=autapse,
            normalized=normalized,
            glob_inh=False,
            mujoco=mujoco,
            **syn_params,
        )

        # Compute the subtractive term, respecting normalization if requested
        subtract_term = abs(w_sub)
        if self.normalized:
            subtract_term = subtract_term / self.numNeurons

        # Apply subtractive inhibition to all synaptic weights numerically
        # (This avoids needing symbol names inside the assignment expression.)
        self.ring_synapses.w = self.ring_synapses.w - subtract_term

        # Ensure autapse setting is respected after modification
        if not self.autapse:
            self.ring_synapses.w['i==j'] = 0 * mV

        # Nothing to add to BrianObjects (we didn't create new groups/synapses)
