:py:mod:`byma.pyplot.plots`
===========================

.. py:module:: byma.pyplot.plots


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   byma.pyplot.plots.plot_scale
   byma.pyplot.plots.plot
   byma.pyplot.plots.plot_numerical_error



.. py:function:: plot_scale(x, y, label, scale, style=None)

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


.. py:function:: plot(x, y, **kwargs)

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


.. py:function:: plot_numerical_error(n, func, solve_func, save_title=None, save_path=None, **kwargs)

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


