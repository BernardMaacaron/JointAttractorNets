import matplotlib.pyplot as plt
from brian2 import *
from utils import calculate_PVA

def plot_on_circle(x, y, 
                   title="Circular Plot",
                   title_pad=30,      # Padding between title and plot
                   title_y=1.0,       # Vertical position of title 
                   r_label=None,
                   label_pad=30,      # Padding between radial label and plot
                   theta_ticks=None,   # Expect a tuple: (tick_locations (in radians), tick_labels)
                   r_ticks=None, 
                   legend_label=None, 
                   grid=True, 
                   line_kwargs=None,
                   legend_kwargs={},
                   ax=None): # Added ax argument
    """
    Plots a given 1D dataset (x, y) on a circle.
    
    Parameters:
        x (array-like): The x-values (will be mapped to angles in the range [0, 2pi]).
        y (array-like): The corresponding y-values (used as the radial coordinate).
        
        title (str): Title of the plot.
        title_pad (float): Extra padding (in points) between the title and the axes.
        title_y (float): Vertical position for the title (axes fraction, default is above the axes).
        
        r_label (str): Label for the radial coordinate.
        label_pad (float): Extra padding (in points) between the label and the axes.
        theta_ticks (tuple, optional): A tuple (ticks, tick_labels) to customize the angular ticks.
        
            - ticks: list or array-like of tick locations (in radians).
            - tick_labels: list of labels corresponding to the ticks.
        r_ticks (array-like, optional): Custom radial tick locations.
        
        legend_label (str, optional): Label for the plot legend.
        grid (bool): Whether to display grid lines.
        line_kwargs (dict, optional): Additional keyword arguments to pass to the plot function.
        ax (matplotlib.axes._axes.PolarAxes, optional): The axes to plot on. If None, a new figure will be created.
        
    Note:
        - This function maps x-values linearly onto the interval [0, 2pi].
        - In polar plots, there isn’t a direct theta-axis label; theta ticks are typically used.
    """
    # Set default line styling if none provided
    if line_kwargs is None:
        line_kwargs = {'lw': 2}
    
    # Map x to radians in the range [0, 2pi]
    theta = 2 * np.pi * (x - np.min(x)) / (np.max(x) - np.min(x))     # NOTE: This doesn't use np.deg2rad to generalize to all type of values not just degrees.

    
    # Create polar subplot with custom figure size
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})  # Adjust figsize as needed
    
    # Plot with or without a legend label
    if legend_label:
        ax.plot(theta, y, label=legend_label, **line_kwargs)
        ax.legend(**legend_kwargs)
    else:
        ax.plot(theta, y, **line_kwargs)
    
    # Set the title with custom padding and vertical position
    title_obj = ax.set_title(title, pad=title_pad)
    # Adjust the title's vertical position. The default is around 1.0, so 1.1 moves it a bit above.
    title_obj.set_position([0.5, title_y])
    
    # Set radial label if provided
    if r_label:
        # Polar plots don't have a dedicated radial label,
        # so we can mimic one by adding a label to the y-axis.
        ax.set_ylabel(r_label, labelpad=label_pad)
    
    # Set custom theta ticks if provided
    if theta_ticks is not None:
        ticks, tick_labels = theta_ticks
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
    
    # Set custom radial ticks if provided
    if r_ticks is not None:
        ax.set_yticks(r_ticks)
    
    # Option to disable grid
    ax.grid(grid)
    
    return ax

def visualise_connectivity(Synapses):
    Ns = len(Synapses.source)
    Nt = len(Synapses.target)
    figure(figsize=(10, 4))
    subplot(121)
    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(Synapses.i, Synapses.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], ['Source', 'Target'])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))
    subplot(122)
    plot(Synapses.i, Synapses.j, 'ok')
    xlim(-1, Ns)
    ylim(-1, Nt)
    xlabel('Source neuron index')
    ylabel('Target neuron index')

def raster_plot(spikemon, ax=None, stim_periods=None, stim_display_method='highlight',
                highlight_alpha=0.2, highlight_color='yellow', lines_style='--', duration=None):
    """Create a raster plot of spike times with optional stimulus visualization
    
    Parameters:
    ----------
    spikemon : Brian2 SpikeMonitor
        Monitor object containing spike data
    ax : matplotlib axis, optional
        Axis to plot on. If None, a new figure will be created
    stim_periods : list of tuples or tuple, optional
        List of stimulus periods as (start_time, end_time) tuples or a single tuple.
        Time values should be Brian2 Quantity objects.
        If None, no stimulus will be visualized.
    stim_display_method : str, optional
        Method to display stimulus periods: 'highlight' or 'lines'
        'highlight' - highlight the stimulus period with a colored background
        'lines' - use vertical lines to mark start and end of each stimulus period
    highlight_alpha : float, optional
        Alpha transparency for highlighted areas (0-1)
    highlight_color : str or list, optional
        Color(s) for highlighting stimulus periods. If a list, colors will cycle for multiple periods.
    lines_style : str, optional
        Line style for vertical lines when using 'lines' method
    duration : Brian2 Quantity, optional
        Total simulation duration. If provided, sets the x-axis limit from 0 to duration.
        
    Returns:
    -------
    ax : matplotlib axis
        The axis with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot spike data
    ax.plot(spikemon.t/second, spikemon.i, '.k', ms=1)
    
    # Handle stimulus visualization if provided
    if stim_periods is not None:
        # Convert single period to list for consistent processing
        if not isinstance(stim_periods[0], (list, tuple)):
            stim_periods = [stim_periods]
            
        # Make highlight_color a list if it's a single color
        if isinstance(highlight_color, str):
            highlight_color = [highlight_color] * len(stim_periods)
        
        # Ensure enough colors for all periods
        if len(highlight_color) < len(stim_periods):
            highlight_color = highlight_color * (len(stim_periods) // len(highlight_color) + 1)
            
        # Display each stimulus period
        for i, (start, end) in enumerate(stim_periods):
            color = highlight_color[i % len(highlight_color)]
            
            if stim_display_method == 'highlight':
                ax.axvspan(start/second, end/second, alpha=highlight_alpha, color=color)
            elif stim_display_method == 'lines':
                # Plot vertical lines with the same color for start-stop pair
                ax.axvline(start/second, color=color, linestyle=lines_style)
                ax.axvline(end/second, color=color, linestyle=lines_style)
    
    # Set x-axis limit if duration is provided
    if duration is not None:
        ax.set_xlim(0, duration/second)
    
    # Set labels and title
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Neuron index')
    ax.set_title('Raster Plot')
    
    return ax

def firing_rate_profile(spikemon, positions, duration, ax=None):
    """Calculate and plot firing rates across positions
    
    Parameters:
    ----------
    spikemon : Brian2 SpikeMonitor
        Monitor containing spike data
    positions : array
        Position of each neuron on the ring
    duration : Brian2 Quantity
        Total simulation duration
    ax : matplotlib axis, optional
        Axis to plot on. If None, a new figure will be created
        
    Returns:
    -------
    spike_rates : dict
        Dictionary containing 'first_half' and 'second_half' firing rates
    ax : matplotlib axis
        The axis with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    
    num_indices = len(positions)
    # Calculate firing rates
    spike_count = np.zeros(num_indices)
    
    for i, t in zip(spikemon.i, spikemon.t):
        spike_count[i] += 1
    
    firing_rate = spike_count / (duration/second)
    
    # Plot firing rates
    ax.plot(positions, firing_rate, marker='o', linestyle='-')
    ax.set_xlabel('Position (radians)')
    ax.set_ylabel('Firing rate (Hz)')
    ax.set_title('Firing Rate Profile')
    ax.legend()
    
    return firing_rate, ax

def polar_plot_PVA(firing_rates, positions, scale=1.5, ax=None):
    """
    Plots the Population Vector Average (PVA) on a polar plot using plot_on_circle.
    
    Parameters:
        firing_rates (array-like): Firing rates for each neuron.
        positions (array-like): Neuron positions (angles in radians).
        ax (matplotlib.axes._axes.PolarAxes, optional): Axes to plot on. If None, a new figure is created.
    """
    # Use the dedicated function to calculate PVA.
    pva_angle, pva_magnitude = calculate_PVA(firing_rates, positions)
    
    # Set a scaling factor for clarity.
    scale_factor = scale * np.max(firing_rates)  
    
    x = positions
    y = firing_rates
    
    ax = plot_on_circle(x, y, 
                        title='Population Vector Average (PVA)',
                        r_label='Firing Rate',
                        legend_label='Neuron activity',
                        line_kwargs={'marker': 'o', 'linestyle': '-'},
                        ax=ax)
    
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(6,6))
    
    ax.arrow(pva_angle, 0, 0, pva_magnitude*scale_factor, width=0.05,
             color='r', label='PVA', alpha=0.9, length_includes_head=True)
    
    ax.set_rlim(0, pva_magnitude*scale_factor)
    ax.legend(loc='upper right')
    
    return ax

def time_resolved_PVA(spikemon, positions, duration, num_neurons, 
                      window_size=50*ms, step_size=10*ms, ax=None,
                      color_windows=False, cmap_name='viridis',
                      stim_periods=None, stim_display_method='highlight',
                      highlight_alpha=0.2, highlight_color='yellow', lines_style='--'):
    """
    Plot time-resolved population vector average using calculate_PVA from utils and optionally color the windows.
    
    Parameters:
        spikemon (Brian2 SpikeMonitor): Monitor containing spike data.
        positions (array): Neuron positions (angles in radians).
        duration (Brian2 Quantity): Total simulation duration.
        num_neurons (int): Number of neurons.
        window_size (Brian2 Quantity): Time window for PVA calculation.
        step_size (Brian2 Quantity): Step size between windows.
        ax (matplotlib axis, optional): Axis to plot on. If None, a new figure is created.
        color_windows (bool): If True, color the computed windows based on time.
        cmap_name (str): Name of the matplotlib colormap to use (if color_windows is True).
        stim_periods (list of tuples or tuple, optional): List of stimulus periods as (start_time, end_time) tuples or a single tuple.
        stim_display_method (str, optional): Method to display stimulus periods: 'highlight' or 'lines'
        highlight_alpha (float, optional): Alpha transparency for highlighted areas (0-1)
        highlight_color (str or list, optional): Color(s) for highlighting stimulus periods. If a list, colors will cycle for multiple periods.
        lines_style (str, optional): Line style for vertical lines when using 'lines' method
        
    Returns:
        tuple: (pva_angles, ax) where pva_angles is an array of computed angles.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    
    # Generate time windows in seconds.
    t_windows = np.arange(0, duration/second, step_size/second)
    pva_angles = np.zeros(len(t_windows))
    
    for i, t in enumerate(t_windows):
        t_start = t * second
        t_end = t_start + window_size
        
        # Count spikes for each neuron in the current window
        window_spike_counts = np.zeros(num_neurons)
        for neuron_idx, spike_time in zip(spikemon.i, spikemon.t):
            if t_start <= spike_time < t_end:
                window_spike_counts[neuron_idx] += 1
        
        # Use calculate_PVA from utils to get the PVA angle (ignore magnitude here)
        pva_angle, _ = calculate_PVA(window_spike_counts, positions)
        # Ensure angle is in [0, 2pi]
        pva_angles[i] = pva_angle if pva_angle >= 0 else pva_angle + 2*np.pi

    if color_windows:
        # Create a colormap to color the windows by time.
        cmap = plt.get_cmap(cmap_name)
        norm = plt.Normalize(vmin=t_windows.min(), vmax=t_windows.max())
        colors = cmap(norm(t_windows))
        scatter = ax.scatter(t_windows, pva_angles, s=10, c=colors)
        plt.colorbar(scatter, ax=ax, label="Time (s)")
    else:
        ax.scatter(t_windows, pva_angles, s=10, color='blue')
    
    # Incorporate stim_periods visualization
    if stim_periods is not None:
        if not isinstance(stim_periods[0], (list, tuple)):
            stim_periods = [stim_periods]
        if isinstance(highlight_color, str):
            highlight_color = [highlight_color] * len(stim_periods)
        if len(highlight_color) < len(stim_periods):
            highlight_color = highlight_color * (len(stim_periods) // len(highlight_color) + 1)
        for i, (start, end) in enumerate(stim_periods):
            color = highlight_color[i % len(highlight_color)]
            if stim_display_method == 'highlight':
                ax.axvspan(start/second, end/second, alpha=highlight_alpha, color=color)
            elif stim_display_method == 'lines':
                ax.axvline(start/second, color=color, linestyle=lines_style)
                ax.axvline(end/second, color=color, linestyle=lines_style)
    
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Decoded angle (rad)')
    ax.set_ylim(0, 2*np.pi)
    ax.set_title('Time-Resolved Population Vector Average (PVA)')
    ax.legend()
    
    return pva_angles, ax

def membrane_potential_traces(statemon, duration, Vth = None,
                              stim_periods=None, stim_display_method='highlight',
                              highlight_alpha=0.2, highlight_color='yellow', lines_style='--', num_neurons=5, ax=None):
    
    """Plot membrane potential traces for a subset of neurons
    
    Parameters:
    ----------
    statemon : Brian2 StateMonitor
        Monitor containing membrane potential data
    duration : Brian2 Quantity
        Total simulation duration
    stim_periods : list of tuples or tuple, optional
        List of stimulus periods as (start_time, end_time) tuples or a single tuple.
        Time values should be Brian2 Quantity objects.
        If None, no stimulus will be visualized.
    stim_display_method : str, optional
        Method to display stimulus periods: 'highlight' or 'lines'
        'highlight' - highlight the stimulus period with a colored background
        'lines' - use vertical lines to mark start and end of each stimulus period
    highlight_alpha : float, optional
        Alpha transparency for highlighted areas (0-1)
    highlight_color : str or list, optional
        Color(s) for highlighting stimulus periods. If a list, colors will cycle for multiple periods.
    lines_style : str, optional
        Line style for vertical lines when using 'lines' method
    num_neurons : int, optional
        Number of neurons to plot
    ax : matplotlib axis, optional
        Axis to plot on. If None, a new figure will be created
        
    Returns:
    -------
    ax : matplotlib axis
        The axis with the plot
    """
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot membrane potential for a few neurons
    step = max(1, len(statemon.V) // num_neurons)
    for i in range(0, len(statemon.V), step)[:num_neurons]:
        ax.plot(statemon.t/second, statemon.V[i]/mV, label=f'Neuron {i}')
    
    # Incorporate stim_periods visualization
    if stim_periods is not None:
        if not isinstance(stim_periods[0], (list, tuple)):
            stim_periods = [stim_periods]
        if isinstance(highlight_color, str):
            highlight_color = [highlight_color] * len(stim_periods)
        if len(highlight_color) < len(stim_periods):
            highlight_color = highlight_color * (len(stim_periods) // len(highlight_color) + 1)
        for i, (start, end) in enumerate(stim_periods):
            color = highlight_color[i % len(highlight_color)]
            if stim_display_method == 'highlight':
                ax.axvspan(start/second, end/second, alpha=highlight_alpha, color=color)
            elif stim_display_method == 'lines':
                ax.axvline(start/second, color=color, linestyle=lines_style)
                ax.axvline(end/second, color=color, linestyle=lines_style)
    
    if Vth is not None:
        ax.axhline(Vth/mV, color='red', linestyle='--', label='Threshold')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Membrane potential (mV)')
    ax.set_title('Membrane Potentials')
    ax.legend()
    
    return ax
