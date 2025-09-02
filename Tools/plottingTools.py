import matplotlib.pyplot as plt
from brian2 import *
from utils import *



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
        
        r_label (str):
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
    theta = 2 * np.pi * (x - np.min(x)) / (np.max(x) - np.min(x))     # NOTE: This doesn't use np.deg

    
    # Create polar subplot with custom figure size
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})  # Adjust figsize as needed
    
    # Plot with or without a legend label
    if legend_label:
        ax.plot(theta, y, label=legend_label, **line_kwargs)
        # Conditionally add legend only if legend handles exist.
        handles, labels = ax.get_legend_handles_labels()
        if handles:
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
                highlight_alpha=0.2, highlight_color='yellow', lines_style='--', duration=None,
                num_neurons=120, y_axisFull=False):
    """Create a raster plot of spike times with optional stimulus visualization
    
    Parameters:
    ----------
    spikemon : Brian2 SpikeMonitor or tuple
        Monitor object containing spike data, or a tuple of (spike_ids, spike_times)
        where spike_ids is an array of neuron indices and spike_times is an array of 
        corresponding spike times (in seconds or as Brian2 Quantity objects)
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
    
    # Extract spike data using the helper function
    spike_ids, spike_times, is_quantity = extractSpikeData(spikemon)
    
    # Convert spike_times to seconds if it's a Brian2 Quantity
    if is_quantity:
        spike_times = spike_times/second
    
    # Plot spike data
    ax.plot(spike_times, spike_ids, '.k', ms=1)
    
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
            highlight_color = highlight_color * (len(highlight_color) // len(stim_periods) + 1)
            
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
    
    if y_axisFull:
        ax.set_ylim(-1, num_neurons)
    
    # Set labels and title
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Neuron index')
    ax.set_title('Raster Plot')
    
    return ax

def firing_rate_profile(spikemon, positions, duration, ax=None, instantRate=False):
    """Calculate and plot firing rates across positions
    
    Parameters:
    ----------
    spikemon : Brian2 SpikeMonitor or tuple
        Monitor containing spike data, or a tuple of (spike_ids, spike_times)
    positions : array
        Position of each neuron on the ring
    duration : Brian2 Quantity
        Total simulation duration
    ax : matplotlib axis, optional
        Axis to plot on. If None, a new figure will be created
    instantRate : bool, optional
        If True, uses computeInstRate, otherwise uses computeFiringRate
        
    Returns:
    -------
    firing_rate : array
        Array of firing rates for each neuron
    ax : matplotlib axis
        The axis with the plot
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
    
    # Calculate firing rates using either computeFiringRate or computeInstRate
    num_neurons = len(positions)
    if instantRate:
        firing_rate = computeInstRate(spikemon, num_neurons)
    else:
        firing_rate = computeFiringRate(spikemon, num_neurons, total_duration=duration)
    
    # Plot firing rates
    ax.plot(positions, firing_rate, marker='o', linestyle='-')
    ax.set_xlabel('Position (radians)')
    if instantRate:
        ax.set_ylabel('Instantaneous Firing rate (Hz)')
        ax.set_title('Instant. Firing Rate Profile')
    else:
        ax.set_ylabel('Firing rate (Hz)')
        ax.set_title('Firing Rate Profile')
    
    # Conditionally add legend only if there are legend entries
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend()
    
    return firing_rate, ax

def instantRateTT_plot(spikemon, positions, duration, num_neurons=None,
                          fig=None, ax=None, colormap='viridis', alpha=0.7,
                          view_angle=(30, 35), max_rate=None):
    """Create a 3D visualization of instantaneous firing rates over time"""
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.cm as cm
    
    # Determine number of neurons if not provided
    if num_neurons is None:
        num_neurons = len(positions)
    
    # Create figure and 3D axis if not provided
    if fig is None or ax is None:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
    
    # Get the instantaneous firing rates
    neuron_ids, spike_times, inst_rates = computeInstRateTT(spikemon, num_neurons)
    
    if len(neuron_ids) == 0:
        print("No spikes found for 3D visualization")
        return fig, ax
    
    # Convert duration to seconds if it's a Brian2 Quantity
    if isinstance(duration, Quantity):
        duration = duration/second
    
    # Get neuron positions
    neuron_positions = positions[neuron_ids]
    
    # Cap rates to improve visualization if needed
    if max_rate is not None:
        inst_rates = np.minimum(inst_rates, max_rate)
    
    # Create the 3D scatter plot with color based on rate
    scatter = ax.scatter(neuron_positions, spike_times, inst_rates, 
                         c=inst_rates, cmap=colormap, alpha=alpha, 
                         s=10, edgecolors='none')

    # plot = ax.plot_trisurf(neuron_positions, spike_times, inst_rates, cmap=colormap, alpha=alpha)
    # Add a color bar
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5, label='Instantaneous Firing Rate (Hz)')
    
    # Set labels
    ax.set_xlabel('Neuron Position (rad)')
    ax.set_ylabel('Time (s)')
    ax.set_zlabel('Instantaneous Firing Rate (Hz)')
    
    # Set title
    ax.set_title('3D Instantaneous Firing Rate Profile')
    
    # Set view angle
    ax.view_init(elev=view_angle[0], azim=view_angle[1])
    
    # Set axis limits
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(0, duration)
    
    return fig, ax

def polar_plot_PVA(firing_rates, positions, scale=1.5, ax=None):
    """
    Plots the Population Vector Average (PVA) on a polar plot using plot_on_circle.
    
    Parameters:
        firing_rates (array-like): Firing rates for each neuron.
        positions (array-like): Neuron positions (angles in radians).
        ax (matplotlib.axes._axes.PolarAxes, optional): Axes to plot on. If None, a new figure is created.
    """
    # Use the dedicated function to calculate PVA.
    pva_angle, pva_magnitude = computePVA(firing_rates, positions)
    
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
    # Conditionally add legend only if there are legend entries.
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc='upper right')
    
    return ax

def time_resolved_PVA(spikemon, positions, duration, num_neurons, 
                      window_size=50*ms, step_size=10*ms,
                      ax=None, label=None,
                      color_windows=False, cmap_name='viridis',
                      stim_periods=None, stim_display_method='highlight',
                      highlight_alpha=0.2, highlight_color='yellow', lines_style='--'):
    """
    Plot time-resolved population vector average using calculate_PVA from utils and optionally color the windows.
    
    Parameters:
        spikemon (Brian2 SpikeMonitor or tuple): Monitor containing spike data, or a tuple of (spike_ids, spike_times)
            where spike_ids is an array of neuron indices and spike_times is an array of 
            corresponding spike times (in seconds or as Brian2 Quantity objects)
        positions (array): Neuron positions (angles in radians).
        duration (Brian2 Quantity): Total simulation duration.
        num_neurons (int): Number of neurons.
        window_size (Brian2 Quantity): Time window for PVA calculation.
        step_size (Brian2 Quantity): Step size between windows.
        ax (matplotlib axis, optional): Axis to plot on. If None, a new figure is created.
        label (str, optional): Label for the plot (used in the legend).
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

    # Compute PVA angles and time windows
    pva_angles, time_windows = computePVATT(spikemon, positions, duration, num_neurons, window_size, step_size)

    # Plot the data
    if color_windows:
        # Create a colormap to color the windows by time
        cmap = plt.get_cmap(cmap_name)
        norm = plt.Normalize(vmin=time_windows.min(), vmax=time_windows.max())
        colors = cmap(norm(time_windows))
        scatter = ax.scatter(time_windows, pva_angles, s=10, c=colors, label=label)
        plt.colorbar(scatter, ax=ax, label="Time (s)")
    else:
        ax.plot(time_windows, pva_angles, linestyle='', marker='o', markersize=3, label=label)

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
    
    # Set axis labels and title
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Decoded angle (rad)')
    ax.set_ylim(0, 2*np.pi)
    ax.set_title('Time-Resolved Population Vector Average (PVA)')

    # Add a legend if a label is provided
    if label:
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
    # Conditionally add legend only if there are legend entries.
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend()
    
    return ax

def spectrumPlot(eigenvalues, ax=None):
    """
    Plots the spectrum of a complex-valued matrix using matplotlib,
    mimicking Seaborn's aesthetic (color, size, hollow markers, etc.).
    
    Parameters
    ----------
    eigenvalues : array-like
        Complex eigenvalues to plot
    ax : matplotlib.axes.Axes, optional
        Existing axis to plot on. If None, creates new figure and axis.
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object (None if ax was provided)
    ax : matplotlib.axes.Axes
        Axis object
    scat : matplotlib.collections.PathCollection
        Scatter plot object
    """
    # Separate real and imaginary parts
    real = np.real(eigenvalues)
    imag = np.imag(eigenvalues)

    # Determine color based on stability threshold - using list comprehension
    colors = ['#ff7f0e' if r >= 1 else '#005f73' for r in real]
    
    # Create figure and axis if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = None

    # Plot filled scatter points with colored faces
    scat = ax.scatter(
        real, imag,
        s=40,
        c=colors,  # Use 'c' for face colors
        # edgecolors='black',  # Optional: add black edges
        linewidth=0.5,
        marker='o'
    )

    # Vertical line at x = 1 (stability boundary)
    ax.axvline(1, color='#ff7f0e', linewidth=1.5)

    # Axis labels and layout
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.set_aspect("equal")
    ax.legend([], [], frameon=False)  # No legend

    return fig, ax, scat