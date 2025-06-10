from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

def create_spike_plot(max_time_window=5.0):
    """Create a dynamic rolling plot to visualize spikes."""
    fig, ax = plt.figure(figsize=(10, 6)), plt.subplot(111)
    
    # Create scatter plot with empty data initially
    scatter = ax.scatter([], [], s=10, alpha=0.7)
    scatter.set_animated(True)

    # Set up plot properties
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Neuron ID')
    ax.set_title('Dynamic Spike Raster Plot')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Return plot elements
    return fig, ax, scatter

def update_plot(frame, scatter, ax, events_buffer, max_time_window=5.0):
    """Update the rolling spike plot."""
    
    if len(events_buffer) > 0:
        # Extract spike data
        spikesID = [e.neuron_id for e in events_buffer]
        spikesTimes = [e.timestamp*1e-6 for e in events_buffer]
        if len(spikesTimes) > 0:
            # Get current time for rolling window
            current_time = max(spikesTimes)
            min_time = current_time - max_time_window
            
            ax.set_xlim(min_time, current_time + 0.1)

            # Filter data for visible time window
            visible_indices = [i for i, t in enumerate(spikesTimes) if t > min_time]
            visible_times = [spikesTimes[i] for i in visible_indices]
            visible_ids = [spikesID[i] for i in visible_indices]
            
            # Update data in the scatter plot
            scatter.set_offsets(np.column_stack((visible_times, visible_ids)))
            
            # Adjust axis limits dynamically
            if len(visible_ids) > 0:
                ax.set_xlim(min_time, current_time + 0.1)
                ax.set_ylim(min(visible_ids) - 1 if visible_ids else 0, 
                           max(visible_ids) + 1 if visible_ids else 10)
            
    return scatter,  # Return as tuple with trailing comma for blit=True

def start_spike_visualization(events_buffer, max_time_window=3.0, update_interval=10):
    """Start the dynamic spike visualization."""
    fig, ax, scatter = create_spike_plot(max_time_window)
    
    # Create animation with buffer passed to update_plot
    animation = FuncAnimation(
        fig, 
        update_plot, 
        fargs=(scatter, ax, events_buffer, max_time_window),
        interval=update_interval,
        blit=True
    )
    
    plt.tight_layout()
    plt.show()
    
    return animation