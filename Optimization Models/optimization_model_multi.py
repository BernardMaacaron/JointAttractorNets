from brian2 import *
import numpy as np

import os
import sys
sys.path.append('Neuron and Synapse Models')
from neuronModels import *
from ringAttractorClass import *
sys.path.append('Tools')
from utils import *

class RingAttractorSim:
    """
    Wrapper that builds the network once (in __init__)
    and simply runs the pre‑compiled binary in do_run().
    """
    def __init__(self, params, stim_center=0, stim_width=0.5):
        defaultclock.dt = 0.1*ms
        self.num_neurons = 120
        self.params      = params
        self.stim_center = stim_center
        self.stim_width  = stim_width

        # ---------- network construction ----------
        tau         = params.get('tau', 10)*ms
        sigma_noise = params.get('sigma_noise', 1)*mV
        V_rest      = -70*mV

        neuron_eq = Equations(LIF_xi_vel_eq,
                              tau=tau, V_rest=V_rest,
                              sigma_noise=sigma_noise)

        Vth, V_reset, refr = -48*mV, -80*mV, 5*ms
        self.positions = np.linspace(0, 2*np.pi, self.num_neurons, endpoint=False)

        # External bump
        I0 = 30*mV
        d  = np.angle(np.exp(1j * (self.positions - stim_center)))
        self.I_ext_on = I0 * np.exp(-(d**2) / (2 * stim_width**2))

        self.ring = RingAttractor(neuron_eq,
                                  self.num_neurons,
                                  Vth, V_reset, refr,
                                  **params)
        self.ring.ring_pool.I_ext = self.I_ext_on

        # Monitors & network op
        self.spikemon = SpikeMonitor(self.ring.ring_pool, name='spikemon')

        @network_operation(dt=defaultclock.dt, name='clip_V')
        def enforce_lower_bound():
            self.ring.ring_pool.V[:] = clip(self.ring.ring_pool.V[:],
                                            V_reset, inf*volt)

        self.net = Network(self.ring.BrianObjects +
                           [self.spikemon, enforce_lower_bound])

        # Schedule
        self.input_on  = 0.5*second
        self.input_off = 0.2*second
        self.t_stop    = self.input_on + self.input_off

        self.net.run(self.input_on)
        self.ring.ring_pool.I_ext = 0*mV
        self.net.run(self.input_off)

        # Compile once
        build_dir = os.path.join(os.getcwd(), 'Optimization Models', 'optimizationModelMulti_build')
        device.build(directory=build_dir, compile=True, run=False)
        self.device = get_device()

    def do_run(self, result_dir):
        """
        Runs the compiled binary in `result_dir`
        and returns firing_rates, PVA angle, and magnitude.
        """
        from brian2.devices import device as _active_device
        _active_device.active_device = self.device
        self.device.run(results_directory=result_dir)

        firing_rates = compute_firing_rate(
            self.spikemon, self.num_neurons,
            start_time=self.input_on, end_time=self.t_stop
        )
        pva_angle, pva_mag = calculate_PVA(firing_rates, self.positions)
        return firing_rates, pva_angle, pva_mag



if __name__ == '__main__':          # ← critical guard for Windows/macOS
    # Use Brian’s standalone backend but postpone compilation until we say so
    set_device('cpp_standalone', build_on_run=False)

    # ---------- default parameters ----------
    default_params = {
        'tau'        : 10,
        'sigma_noise': 1.0,
        'sigma_exc'  : 0.125,
        'sigma_inh'  : 0.1,
        'g_exc'      : 1.0*mV,
        'g_inh'      : -1.0*mV,
        'syn_profile': 'mexican_hat',
        'autapse'    : True,
        'glob_inh'   : False
    }

    # ---------- build the model once ----------
    stim_center = 0.0
    stim_width  = 0.5
    sim = RingAttractorSim(default_params,
                           stim_center=stim_center,
                           stim_width=stim_width)

    # ---------- run one realisation (can run many in a loop / pool) ----------
    firing_rates, pva_angle, pva_magnitude = sim.do_run('results/GT_run')

    # ---------- pretty print ----------
    print("Ground‑Truth Center:", stim_center)
    print("Ground‑Truth Input :", sim.I_ext_on)      # Gaussian bump you fed in
    print("Observed Firing Rates:", firing_rates)
    print("PVA Angle :", pva_angle)
    print("PVA Magnitude:", pva_magnitude)
