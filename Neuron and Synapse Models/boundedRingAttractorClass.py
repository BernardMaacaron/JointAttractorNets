"""BoundedRingAttractorClass

introduces joint
boundary on the circular population. You supply `limit_neuron` (index in
0..N-1, excluding first and last) and the class computes:

* `boundary_angle` (theta of that neuron)
* Partition counts: how many inbound vs outbound neurons
* The center angle of the outbound population: `theta_star` and a local transition width `t_thresh`
* Velocity–dependent asymmetric synaptic weight terms using piecewise ramps

When a boundary is provided the original asymmetric synapse object is replaced
by two pre‑computed weight fields (positive vs negative velocity). If no
boundary is given the object behaves like the base `RingAttractor`.
"""

from brian2 import *  # Reuse same Brian2 symbolic names (V, mV, ms, etc.)
from ringAttractorClass import RingAttractor
import numpy as np
from warnings import warn
import os
import sys



# Add the Tools directory to the path
tools_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Tools')
sys.path.append(tools_path)

from plottingTools import *
from utils import *
"""Helper functions (C++ friendly)

Module‑level pure functions used inside synapse equations so Brian2 can export
them to cpp_standalone. They avoid closures / object state; all parameters are
passed explicitly. Piecewise definitions supply smooth (linear) transitions
around boundary and theta_star regions for velocity‑dependent asymmetry.
"""


@implementation('cpp', """
inline double linear_interp(double x, double x0, double y0, double xf, double yf){
    return y0 + (yf - y0) * (x - x0) / (xf - x0);
}
""")
@check_units(x=1, x0=1, y0=1, xf=1, yf=1, result=1)
def linear_interp(x, x0, y0, xf, yf):
    return y0 + (yf - y0) * (x - x0) / (xf - x0)


# NOTE: The following functions are intentionally verbose (if/else logic) rather than
# using numpy.select to ease translation to C++ and avoid reliance on closures.
# All parameters are dimensionless scalars (angles in radians, already unitless in Brian2 expressions).

@implementation('cpp', """
inline double positive_velocity_connectivity(double theta_pre, double theta_post, double t_thresh, double theta_star, double joint_limit, double g_sine_over_mV){
    const double TWO_PI = 6.283185307179586;
    double a = 1.0;
    if(theta_pre < t_thresh){
        a = linear_interp(theta_pre, 0.0, 0.0, t_thresh, -1.0);
    } else if(theta_pre < theta_star - t_thresh){
        a = -1.0;
    } else if(theta_pre <= theta_star){
        a = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0);
    } else if(theta_pre <= theta_star + t_thresh){
        a = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0);
    } else if(theta_pre <= TWO_PI - t_thresh){
        a = 1.0;
    } else {
        a = linear_interp(theta_pre, TWO_PI - t_thresh, 1.0, TWO_PI, 0.0);
    }
    return g_sine_over_mV * a * sin(-theta_pre + theta_post);
}
""")
@check_units(theta_pre=1, theta_post=1, t_thresh=1, theta_star=1, joint_limit=1, g_sine_over_mV=1, result=1)
def positive_velocity_connectivity(theta_pre, theta_post, t_thresh, theta_star, joint_limit, g_sine_over_mV):
    """Positive velocity kernel (vectorised numpy version).

    Returns sign‑modulated sine coupling with piecewise linear ramps near
    0, theta_star and 2π providing smooth transitions.
    """
    theta_pre = np.asarray(theta_pre)
    theta_post = np.asarray(theta_post)
    cond1 = (theta_pre < t_thresh)
    cond2 = (theta_pre >= t_thresh) & (theta_pre < theta_star - t_thresh)
    cond3 = (theta_pre >= theta_star - t_thresh) & (theta_pre <= theta_star)
    cond4 = (theta_pre > theta_star) & (theta_pre <= theta_star + t_thresh)
    cond5 = (theta_pre > theta_star + t_thresh) & (theta_pre <= 2 * np.pi - t_thresh)
    cond6 = (theta_pre > 2 * np.pi - t_thresh)

    interp1 = linear_interp(theta_pre, 0.0, 0.0, t_thresh, -1.0)
    interp2 = -1.0
    interp3 = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0)
    interp4 = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0)
    interp5 = 1.0
    interp6 = linear_interp(theta_pre, 2 * np.pi - t_thresh, 1.0, 2 * np.pi, 0.0)

    a = np.select([cond1, cond2, cond3, cond4, cond5, cond6],
                  [interp1, interp2, interp3, interp4, interp5, interp6],
                  default=1.0)
    return g_sine_over_mV * a * np.sin(-theta_pre + theta_post)


@implementation('cpp', """
inline double negative_velocity_connectivity(double theta_pre, double theta_post, double t_thresh, double theta_star, double joint_limit, double g_sine_over_mV){
    const double TWO_PI = 6.283185307179586;
    double a = 1.0;
    if(theta_pre <= joint_limit - t_thresh){
        a = 1.0;
    } else if(theta_pre <= joint_limit){
        a = linear_interp(theta_pre, joint_limit - t_thresh, 1.0, joint_limit, 0.0);
    } else if(theta_pre <= joint_limit + t_thresh){
        a = linear_interp(theta_pre, joint_limit, 0.0, joint_limit + t_thresh, -1.0);
    } else if(theta_pre <= theta_star - t_thresh){
        a = -1.0;
    } else if(theta_pre <= theta_star){
        a = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0);
    } else if(theta_pre <= theta_star + t_thresh){
        a = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0);
    } else { // theta_pre <= 2*pi
        a = 1.0;
    }
    return g_sine_over_mV * a * sin(-theta_pre + theta_post);
}
""")
@check_units(theta_pre=1, theta_post=1, t_thresh=1, theta_star=1, joint_limit=1, g_sine_over_mV=1, result=1)
def negative_velocity_connectivity(theta_pre, theta_post, t_thresh, theta_star, joint_limit, g_sine_over_mV):
    """Negative velocity kernel (vectorised numpy version).

    Similar to the positive kernel but shaped around the joint limit and
    theta_star for opposite movement direction.
    """
    theta_pre = np.asarray(theta_pre)
    theta_post = np.asarray(theta_post)
    cond1 = (theta_pre <= joint_limit - t_thresh)
    cond2 = (theta_pre > joint_limit - t_thresh) & (theta_pre <= joint_limit)
    cond3 = (theta_pre > joint_limit) & (theta_pre <= joint_limit + t_thresh)
    cond4 = (theta_pre > joint_limit + t_thresh) & (theta_pre <= theta_star - t_thresh)
    cond5 = (theta_pre > theta_star - t_thresh) & (theta_pre <= theta_star)
    cond6 = (theta_pre > theta_star) & (theta_pre <= theta_star + t_thresh)
    cond7 = (theta_pre > theta_star + t_thresh)

    interp1 = 1.0
    interp2 = linear_interp(theta_pre, joint_limit - t_thresh, 1.0, joint_limit, 0.0)
    interp3 = linear_interp(theta_pre, joint_limit, 0.0, joint_limit + t_thresh, -1.0)
    interp4 = -1.0
    interp5 = linear_interp(theta_pre, theta_star - t_thresh, -1.0, theta_star, 0.0)
    interp6 = linear_interp(theta_pre, theta_star, 0.0, theta_star + t_thresh, 1.0)
    interp7 = 1.0

    a = np.select([cond1, cond2, cond3, cond4, cond5, cond6, cond7],
                  [interp1, interp2, interp3, interp4, interp5, interp6, interp7],
                  default=1.0)
    return g_sine_over_mV * a * np.sin(-theta_pre + theta_post)


class BoundedRingAttractor(RingAttractor):
    """Ring attractor + unilateral joint limit.

    Required args (mirrors base): neuron_eq, N, threshold/reset/refractory.
    Extra input: limit_neuron (index marking the joint boundary). Must not be
    the first or last neuron. If omitted, behaves exactly like `RingAttractor`.

    On construction (with a boundary) computes:
      - boundary_angle (radians of limit)
      - theta_star (center angle of the outbound neuron population, made unstable equilibrium point)
      - t_thresh (small angular transition width from sin connectivity to -sin connectivity)
      - inbound/outbound counts and index of neuron at theta_star
      - Replaces asymmetric synapse with velocity‑signed positive/negative
        weight fields using piecewise linear modulation.
    """

    def __init__(self,
                 neuron_eq, N=120,
                 Vth=-48*mV, V_reset=-80*mV, refractory_period=5*ms, # Neuron parameters,                         
                 autapse = True,
                 glob_inh = True, w_inh = -0.15*mV,                 # Global Inhibitory neuron parameters
                 mujoco = False, limit_neuron=None,
                 **syn_params):
        
        # Initialize parent class fully.
        super().__init__(neuron_eq, N=N, Vth=Vth, V_reset=V_reset, refractory_period=refractory_period,
                         syn_profile='cosine', autapse=autapse, glob_inh=glob_inh, w_inh=w_inh,
                         mujoco=mujoco, **syn_params)

        self.numNeurons=self.N
        # Store boundary info.
        self.limit_neuron = limit_neuron
        self.has_boundary = limit_neuron is not None
        if self.has_boundary:
            if not (0 <= limit_neuron < self.N):
                raise ValueError(f"boundary_neuron must be in [0, {self.N-1}], got {limit_neuron}")
            if limit_neuron==self.N-1:
                raise ValueError(f"boundary_neuron cannot be the last neuron (index {self.N-1}), at least one out of bound neuron is needed.")
            if limit_neuron==0:
                raise ValueError(f"boundary_neuron cannot be the first neuron (index 0), at least one in-bound neuron is needed.")
            # Pre-compute angle (consistent with parent: uniform positions in [0, 2*pi))
            self.boundary_angle = float(self.positions[limit_neuron])
            joint_limit=self.boundary_angle
            self.N_inboundNeurons=self.limit_neuron+1
            self.N_outboundNeurons=self.N-self.N_inboundNeurons
            self.theta_star=(self.boundary_angle / 2 + pi)
            self.neuron_at_theta_star = int(self.theta_star / (2 * pi) * self.N)
            t_thresh_0=((self.N-self.neuron_at_theta_star)//4)*2*pi/self.N
            t_thresh_limit=((self.neuron_at_theta_star-self.limit_neuron)//4)*2*pi/self.N
            t_thresh_inbound=(self.limit_neuron//4)*2*pi/self.N
            self.t_thresh = min(t_thresh_0,t_thresh_limit,t_thresh_inbound)
            t_thresh = self.t_thresh
            
            g_sine = syn_params.get('g_sine', 0.1*mV)

            # Precompute dimensionless gain
            g_sine_over_mV = (g_sine / mV)

            # Use parameterized functions (fully supported in cpp_standalone)
            self.connectivityAsym_eq = '0*mV'
            self.connectivityAsymPositive_eq = (
                f'positive_velocity_connectivity(theta_pre, theta_post, {t_thresh}, {self.theta_star}, {joint_limit}, {g_sine_over_mV})*mV'
            )
            self.connectivityAsymNegative_eq = (
                f'negative_velocity_connectivity(theta_pre, theta_post, {t_thresh}, {self.theta_star}, {joint_limit}, {g_sine_over_mV})*mV'
            )
            
            self.BrianObjects.remove(self.ring_synapses_asym)
            
            self.ring_synapses_asym = Synapses(self.ring_pool, self.ring_pool,
                                    model='''vel_in : 1 (shared)
                                                w_asym_positive : volt
                                                w_asym_negative : volt''',
                                    on_pre='I_vel_post += vel_in * (w_asym_positive * int(vel_in > 0) - w_asym_negative * int(vel_in < 0))')
            self.ring_synapses_asym.connect()
            self.ring_synapses_asym.w_asym_positive = self.connectivityAsymPositive_eq
            self.ring_synapses_asym.w_asym_negative = self.connectivityAsymNegative_eq
            
            
            self.BrianObjects.append(self.ring_synapses_asym)
            
        else:
            warn("No boundary neuron specified; acting as a normal ring", UserWarning, stacklevel=2)
            self.N_inboundNeurons = self.N
            self.N_outboundNeurons = 0
            self.boundary_angle = None
            self.theta_star=None
            self.t_thresh=None
            self.neuron_at_theta_star=None
            
        

        