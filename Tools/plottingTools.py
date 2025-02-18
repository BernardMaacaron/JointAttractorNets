import matplotlib.pyplot as plt
from brian2 import *

def plot_on_circle(x, y, 
                   title="Circular Plot",
                   title_pad=30,      # Padding between title and plot
                   title_y=1.0,       # Vertical position of title 
                   r_label=None,
                   theta_ticks=None,   # Expect a tuple: (tick_locations (in radians), tick_labels)
                   r_ticks=None, 
                   legend_label=None, 
                   grid=True, 
                   line_kwargs=None,
                   legend_kwargs=None):
    """
    Plots a given 1D dataset (x, y) on a circle.
    
    Parameters:
        x (array-like): The x-values (will be mapped to angles in the range [0, 2pi]).
        y (array-like): The corresponding y-values (used as the radial coordinate).
        title (str): Title of the plot.
        title_pad (float): Extra padding (in points) between the title and the axes.
        title_y (float): Vertical position for the title (axes fraction, default is above the axes).
        r_label (str): Label for the radial coordinate.
        theta_ticks (tuple, optional): A tuple (ticks, tick_labels) to customize the angular ticks.
            - ticks: list or array-like of tick locations (in radians).
            - tick_labels: list of labels corresponding to the ticks.
        r_ticks (array-like, optional): Custom radial tick locations.
        legend_label (str, optional): Label for the plot legend.
        grid (bool): Whether to display grid lines.
        line_kwargs (dict, optional): Additional keyword arguments to pass to the plot function.
        
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
        ax.set_ylabel(r_label, labelpad=20)
    
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
    
    plt.show()