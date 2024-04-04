import matplotlib.pyplot as plt
import numpy as np

    

def plot_scale(x, y, label, scale, style=None):
    """
    Plot data with specified scale and style.

    Parameters
    ----------
    x : array-like
        Data points for the x-axis.
    y : array-like
        Data points for the y-axis.
    label : str
        Label for the data.
    scale : str
        Scale for the plot. Options: 'normal', 'loglog', 'xlog', 'ylog'.
    style : dict or None, optional
        Dictionary specifying line style. If None, default style is used.

    Returns
    -------
    None
    """
    if scale == 'loglog':
        plt.loglog(x, y, label=label)
    elif scale == 'xlog':
        plt.semilogx(x, y, label=label)
    elif scale == 'ylog':
        plt.semilogy(x, y, label=label)
    else:
        plt.plot(x, y, label=label)

def plot(x, y, **kwargs):
    """
    Function that create plots of different kinds. With this function it is possible to plots n numbers of 
    function in the same figure quickly and with high personalization.

    Parameters
    ----------
    x : array-like
        Array of x values.
    y : array-like
        Array of y values.
    **kwargs : dict, optional
        settings (dict): Overall plot settings.
            title (str): Title of the plot.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            label (str):  Label for the 1st function.
            label{i} (str): Label for the ith function from i=2.
            x{i} (array-like): Array of x values for the ith function from i=2.
            y{i} (array-like): Array of y values for the ith function from i=2.
            save_title (str): File name to save the plot.
            save_path (str): Path to save the plot. If None, the plot will be saved in the current directory.
            scale (str): Scale for the plot. Options: 'normal', 'loglog', 'xlog', 'ylog'.
        style (dict or list of dicts): Line style(s) for the plot. (Not yet working)

    Returns
    -------
    None
    """
    settings = kwargs.pop('settings', {})
    settings.update(kwargs)  # Incorporate any additional kwargs into settings

    scale = settings.get('scale', 'normal')
    style = settings.get('style', None)

    plt.figure()
    plt.title(settings.get('title', 'Plot'))
    plt.xlabel(settings.get('xlabel', 'x'))
    plt.ylabel(settings.get('ylabel', 'y'))

    plot_scale(x, y, label=settings.get('label', 'y'), scale=scale, style=style)

    for i in range(2, 10):
        y_i = settings.get(f'y{i}', None)
        if y_i is not None:
            label_i = settings.get(f'label{i}', f'y{i}')
            style_i = style[i-2] if isinstance(style, list) else style
            plot_scale(x, y_i, label=label_i, scale=scale, style=style_i)
        else:
            break

    plt.legend()
    plt.show()

    save_title = settings.get('save_title', settings.get('title', 'Plot'))
    save_path = settings.get('save_path', None)

    # Save the plot if requested
    if save_title:
        if save_path is None:
            save_path = '.'
        plt.savefig(f"{save_path}/{save_title}.png")
        print(f"Plot saved at: {save_path}/{save_title}.png")
        
        
def plot_numerical_error(n, func, solve_func, save_title=None, save_path=None, **kwargs):
    """
    Plot the numerical error between the exact and numerical solutions and print the maximum error.

    Parameters
    ----------
    n : int
        Number of grid points.
    func : object
        Instance of the class containing the exact solution.
    solve_func : function
        Function to solve the system.
    save_title : str, optional
        File name plot.
    save_path : str, optional
        Path to save the plot. If None, the plot will be saved in the current directory.
    **kwargs : dict, optional
        Additional keyword arguments to customize the plot and title for saving.

    Returns
    -------
    None
    """

    # Solve the sparse linear system
    numerical_solution = solve_func(n=n, func=func)

    # Generate the x values for plotting
    x_values = np.linspace(0, 1, n + 1)[1:]

    # Calculate the exact solution at each x value
    exact_solution = func.exact(x_values)

    # Calculate the error between the numerical and exact solutions
    error = abs(numerical_solution - exact_solution)

    # Plot the error
    plt.plot(x_values, error, label=kwargs.get('label', 'Error'))
    plt.xlabel(kwargs.get('x_label', 'x'))
    plt.ylabel(kwargs.get('y_label', 'Error'))
    plt.title(kwargs.get('title', 'Error in Numerical Solution'))
    plt.legend()
    
    
    # Save the plot if requested
    if save_title:
        if save_path is None:
            save_path = '.'
        plt.savefig(f"{save_path}/{save_title}.png")
        print(f"Plot saved at: {save_path}/{save_title}.png")

    
    # Show the plot
    plt.show()

    # Print the maximum error
    max_error = np.max(np.abs(error))
    print(f"Maximum error: {max_error}")