##############################
# Dynamic Plotting Classes   #
##############################

# import threading
# import time
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from brian2 import *

from utils import calculate_PVA

class DynamicPlot:
    """Base class for all dynamic plots"""
    
    def __init__(self, fig=None, ax=None, update_interval=100, time_unit=1.0):
        """
        Initialize the base dynamic plot.
        
        Parameters:
        ----------
        fig : matplotlib figure, optional
            Figure to plot on. If None, a new figure will be created
        ax : matplotlib axis, optional
            Axis to plot on. If None, a new axis will be created
        update_interval : int
            Refresh interval in milliseconds
        time_unit : float
            Conversion factor to seconds for non-Brian time values (default=1.0 assumes seconds)
        """
        self.fig = fig
        self.ax = ax
        self.update_interval = update_interval
        self.animation = None
        self.time_unit = time_unit
        
    def setup(self):
        """Set up the plot (to be implemented by subclasses)"""
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 4))
        return self
        
    def update(self, frame):
        """Update function for animation (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement update method")
        
    def start(self):
        """Start the animation"""
        if self.ax is None:
            self.setup()
        
        self.animation = FuncAnimation(self.fig, self.update,
                               interval=self.update_interval, blit=True)

        return self.animation
        
    def stop(self):
        """Stop the animation"""
        if self.animation:
            self.animation.event_source.stop()

class DynamicRasterPlot(DynamicPlot):
    """Dynamic raster plot that updates in real-time"""
    
    def __init__(self, data_buffer, positions=None, num_neurons=10, 
                 max_points=5000, duration_window=None, time_unit=1.0, **kwargs):
        """
        Initialize the dynamic raster plot.
        
        Parameters:
        ----------
        data_buffer : deque or list-like
            Buffer containing (neuron_indices, spike_times) tuples
        positions : array, optional
            Neuron positions if needed for coloring
        num_neurons : int
            Total number of neurons in the simulation
        max_points : int
            Maximum number of points to display at once (for performance)
        duration_window : float, optional
            Time window to display (in seconds). If None, will show all data.
        time_unit : float
            Conversion factor to seconds for non-Brian time values (default=1.0 assumes seconds)
        """
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.positions = positions
        self.num_neurons = num_neurons
        self.max_points = max_points
        self.duration_window = duration_window
        self.scatter = None
        
    def setup(self):
        """Set up the raster plot"""
        super().setup()
        
        # Initialize empty scatter plot
        self.scatter = self.ax.scatter([], [], s=2, color='k')
        self.scatter.set_animated(True)
        
        # Set initial plot properties
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Neuron index')
        self.ax.set_title('Raster Plot (Real-time)')
        self.ax.set_ylim(-1, self.num_neurons)
        
        return self
        
    def update(self, frame):
        """Update the raster plot with new data"""
        try:
            spike_times_all = []
            spike_ids_all = []
            
            for spikes in self.data_buffer:
                if len(spikes) == 2:
                    ids, times = spikes
                    # Convert times to seconds if they're Brian quantities
                    if hasattr(times, 'dimensionality'):
                        times = times/second
                    else:
                        times = np.asarray(times) * self.time_unit
                        
                    spike_ids_all.extend(ids)
                    spike_times_all.extend(times)
            
            # Convert to arrays and sort by time
            if spike_times_all:
                spike_times_all = np.array(spike_times_all)
                spike_ids_all = np.array(spike_ids_all)
                order = np.argsort(spike_times_all)
                spike_times_all = spike_times_all[order]
                spike_ids_all = spike_ids_all[order]
                
                # Update scatter plot data
                if len(spike_times_all) > 0:
                    # Limit to max_points for performance
                    if len(spike_times_all) > self.max_points:
                        # Keep the most recent spikes
                        spike_times_all = spike_times_all[-self.max_points:]
                        spike_ids_all = spike_ids_all[-self.max_points:]
                    
                    # Update time window (always update, not just when specified)
                    current_time = max(spike_times_all)
                    self.ax.set_xlim(max(0, current_time - self.duration_window), current_time + 0.05)
                    
                    # Update scatter plot data
                    self.scatter.set_offsets(np.column_stack([spike_times_all, spike_ids_all]))
            
            # Return the artists that were modified
            return [self.scatter]
            
        except Exception as e:
            print(f"Error updating raster plot: {e}")
            return [self.scatter]

class DynamicMembraneTraces(DynamicPlot):
    """Dynamic membrane potential traces that update in real-time"""
    
    def __init__(self, data_buffer, neurons_to_plot=None, time_window=1.0, Vth=None,
                 time_unit=1.0, volt_unit=1.0, **kwargs):
        """
        Initialize the dynamic membrane potential plot.
        
        Parameters:
        ----------
        data_buffer : deque or list-like
            Buffer containing (times, voltages) tuples
        neurons_to_plot : list, optional
            Indices of neurons to plot. If None, will plot the first 5 neurons.
        time_window : float
            Time window to display (in seconds)
        Vth : float, optional
            Threshold voltage to display as horizontal line (in mV if using Brian units)
        time_unit : float
            Conversion factor to seconds for non-Brian time values (default=1.0 assumes seconds)
        volt_unit : float
            Conversion factor to mV for non-Brian voltage values (default=1.0 assumes mV)
        """
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.neurons_to_plot = neurons_to_plot if neurons_to_plot is not None else list(range(5))
        self.time_window = time_window
        self.Vth = Vth
        self.volt_unit = volt_unit
        self.lines = []
    
    def setup(self):
        """Set up the membrane potential plot"""
        super().setup()
        
        # Create one line per neuron
        self.lines = []
        for i in self.neurons_to_plot:
            line, = self.ax.plot([], [], label=f'Neuron {i}')
            line.set_animated(True)
            self.lines.append(line)
        
        # Add threshold line if provided
        if self.Vth is not None:
            # Handle both Brian and non-Brian threshold values
            if hasattr(self.Vth, 'dimensionality'):
                vth_val = self.Vth/mV
            else:
                vth_val = self.Vth * self.volt_unit
                
            self.ax.axhline(vth_val, color='red', linestyle='--', label='Threshold')
        
        # Set initial plot properties
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Membrane potential (mV)')
        self.ax.set_title('Membrane Potentials (Real-time)')
        self.ax.legend()
        
        return self
    
    def update(self, frame):
        """Update the membrane potential plot with new data"""
        try:
            # Get latest data
            if not self.data_buffer:
                return self.lines
                
            times, voltages = self.data_buffer[-1]
            
            # Convert Brian2 quantities if needed
            if hasattr(times, 'dimensionality'):
                times = times/second
            else:
                times = np.asarray(times) * self.time_unit
                
            if hasattr(voltages, 'dimensionality'):
                voltages = voltages/mV
            else:
                voltages = np.asarray(voltages) * self.volt_unit
            
            # Update time window
            current_time = times[-1]
            self.ax.set_xlim(max(0, current_time - self.time_window), current_time + 0.05)
            
            # Determine y-axis limits based on the data
            if len(voltages) > 0:
                min_v = np.min(voltages)
                max_v = np.max(voltages)
                margin = (max_v - min_v) * 0.1
                self.ax.set_ylim(min_v - margin, max_v + margin)
            
            # Update each line
            for i, line in enumerate(self.lines):
                if i < len(self.neurons_to_plot) and self.neurons_to_plot[i] < len(voltages):
                    neuron_idx = self.neurons_to_plot[i]
                    line.set_data(times, voltages[neuron_idx])
            
            return self.lines
            
        except Exception as e:
            print(f"Error updating membrane potential plot: {e}")
            return self.lines

class DynamicPVAPlot(DynamicPlot):
    """Dynamic Population Vector Average plot that updates in real-time"""
    
    def __init__(self, data_buffer, positions, num_neurons, 
                 window_size=50*ms, step_size=10*ms, time_window=2.0, 
                 color_trail=True, time_unit=1.0, **kwargs):
        """
        Initialize the dynamic PVA plot.
        
        Parameters:
        ----------
        data_buffer : deque or list-like
            Buffer containing (spike_ids, spike_times) tuples
        positions : array
            Neuron positions (angles in radians)
        num_neurons : int
            Total number of neurons in the simulation
        window_size : float or Brian2 Quantity
            Size of the time window for PVA calculation (in seconds if not Brian)
        step_size : float or Brian2 Quantity
            Step size between successive PVA calculations (in seconds if not Brian)
        time_window : float
            Time window to display (in seconds)
        color_trail : bool
            Whether to color the trail of PVA points by time
        time_unit : float
            Conversion factor to seconds for non-Brian time values (default=1.0 assumes seconds)
        """
        super().__init__(time_unit=time_unit, **kwargs)
        self.data_buffer = data_buffer
        self.positions = positions
        self.num_neurons = num_neurons
        
        # Handle window_size and step_size whether they're Brian quantities or not
        if hasattr(window_size, 'dimensionality'):
            self.window_size = window_size
        else:
            self.window_size = window_size * second
            
        if hasattr(step_size, 'dimensionality'):
            self.step_size = step_size
        else:
            self.step_size = step_size * second
            
        self.time_window = time_window
        self.color_trail = color_trail
        self.scatter = None
        self.times = []
        self.pva_angles = []
    
    def setup(self):
        """Set up the PVA plot"""
        super().setup()
        
        # Create scatter plot
        self.scatter = self.ax.scatter([], [], s=5, c=[], cmap='viridis')
        self.scatter.set_animated(True)
        
        # Set initial plot properties
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Decoded angle (rad)')
        self.ax.set_ylim(0, 2*np.pi)
        self.ax.set_title('Time-Resolved PVA (Real-time)')
        
        # Create colorbar if using color trail
        if self.color_trail:
            self.cbar = plt.colorbar(self.scatter, ax=self.ax, label="Time (s)")
        
        return self
        
    def update(self, frame):
        """Update the PVA plot with new data"""
        try:
            # Extract all spike data from buffer
            all_spike_ids = []
            all_spike_times = []
            
            for spikes in self.data_buffer:
                if len(spikes) == 2:
                    ids, t = spikes
                    # Handle unit conversion
                    if hasattr(t, 'dimensionality'):  # Brian2 quantities
                        t = t * second
                    else:
                        # Convert to seconds and then to Brian units for internal calculations
                        t = np.asarray(t) * self.time_unit * second
                    all_spike_ids.extend(ids)
                    all_spike_times.extend(t)
            
            if not all_spike_times:
                return [self.scatter]
                
            # Convert to arrays
            all_spike_ids = np.array(all_spike_ids)
            all_spike_times = np.array(all_spike_times)
            
            # Get current time and calculate window start
            current_time = np.max(all_spike_times)/second if len(all_spike_times) > 0 else 0
            
            # Calculate new PVA points since last update
            new_t_windows = np.arange(
                0 if not self.times else self.times[-1] + self.step_size/second,
                current_time,
                self.step_size/second
            )
            
            for t in new_t_windows:
                t_start = t * second
                t_end = t_start + self.window_size
                
                # Count spikes in window
                window_spike_counts = np.zeros(self.num_neurons)
                for neuron_idx, spike_time in zip(all_spike_ids, all_spike_times):
                    if t_start <= spike_time < t_end:
                        window_spike_counts[neuron_idx] += 1
                
                # Calculate PVA
                pva_angle, _ = calculate_PVA(window_spike_counts, self.positions)
                pva_angle = pva_angle if pva_angle >= 0 else pva_angle + 2*np.pi
                # Add to data
                self.times.append(t)
                self.pva_angles.append(pva_angle)
            
            # Update plot data
            self.scatter.set_offsets(np.column_stack([self.times, self.pva_angles]))
            
            # Update colors if using color trail
            if self.color_trail and self.times:
                norm = plt.Normalize(vmin=max(0, self.times[-1] - self.time_window), vmax=self.times[-1])
                self.scatter.set_array(np.array(self.times))
                self.scatter.set_norm(norm)
            
            # Update time window
            if self.times:
                self.ax.set_xlim(max(0, self.times[-1] - self.time_window), self.times[-1] + 0.05)
            
            return [self.scatter]
            
        except Exception as e:
            print(f"Error updating PVA plot: {e}")
            return [self.scatter]

class DynamicPlotManager:
    """Manager for multiple dynamic plots"""
    
    def __init__(self, update_interval=100):
        """
        Initialize the plot manager.
        
        Parameters:
        ----------
        update_interval : int
            Update interval in milliseconds for all plots
        """
        self.update_interval = update_interval
        self.plots = []
        self.fig = None
        self.axes = None
        self.animations = []
        
    def add_plot(self, plot_class, **kwargs):
        """
        Add a plot to the manager.
        
        Parameters:
        ----------
        plot_class : DynamicPlot class
            The class of the plot to add
        **kwargs : dict
            Arguments to pass to the plot constructor
            
        Returns:
        -------
        self : DynamicPlotManager
            For method chaining
        """
        self.plots.append((plot_class, kwargs))
        return self
        
    def setup(self):
        """
        Set up all plots.
        
        Returns:
        -------
        self : DynamicPlotManager
            For method chaining
        """
        plt.ion()  # Turn on interactive mode
        
        # Create figure and subplots
        n_plots = len(self.plots)
        self.fig, self.axes = plt.subplots(n_plots, 1, figsize=(10, 5*n_plots))
        
        # Handle single plot case
        if n_plots == 1:
            self.axes = [self.axes]
        
        # Initialize each plot and create animations
        for i, (plot_class, kwargs) in enumerate(self.plots):
            # Pass figure and axis to each plot
            kwargs['fig'] = self.fig
            kwargs['ax'] = self.axes[i]
            kwargs['update_interval'] = self.update_interval
            
            # Create and setup plot
            plot = plot_class(**kwargs).setup()
            
            # Start animation
            anim = plot.start()
            self.animations.append(anim)
        
        # Adjust layout
        plt.tight_layout()
        
        return self
        
    def show(self, block=False):
        """
        Show all plots.
        
        Parameters:
        ----------
        block : bool
            Whether to block execution while showing plots
        """
        plt.show(block=block)
        return self
