:py:mod:`byma.iteral.nonstationary.Newton`
==========================================

.. py:module:: byma.iteral.nonstationary.Newton


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   byma.iteral.nonstationary.Newton.newton



.. py:function:: newton(x, f, df, **kwargs)

   Perform Newton iterations to find the root of a given function.

   Parameters
   ----------
   x : array_like
       Initial guess for the root.
   f : callable
       Function to evaluate the residuals.
   df : callable
       Function to evaluate the Jacobian matrix.
   **kwargs : dict
       Additional keyword arguments for customization.
       tol : float, optional
           Tolerance for convergence. Default is 1e-8.
       maxit : int, optional
           Maximum number of iterations. Default is 10000.
       verbose : bool, optional
           If True, prints iteration information. Default is False.
       mode : str, optional
           Mode of the output ('full', 'partial', None).

   Returns
   -------
   root, correction_norm, residuals_norm : tuple
       If mode is 'full'
   root, correction_norm, (residuals_norm) : tuple
       if mode is 'partial'. The residuals_norm are returned if method is not 'normal' 

   root, iterations, correction_norm, residuals_norm: tuple
       if mode is None

   Raises
   ------
   ValueError
       If the maximum number of iterations or tolerance is not a positive integer.

   Examples
   --------
   Basic usage:
   >>> root, iterations, norm_correction = newton(2.0, lambda x: x**2 - 4, lambda x: 2 * x, verbose=True)
   >>> print("Root:", root, "Iterations:", iterations, "Norm of correction:", norm_correction)
       
   Usage with kwargs provided as a dictionary:
   >>> kwargs = {'verbose': True, 'tol': 1e-6, 'maxit': 20}
   >>> root, norm_correction = newton(3.0, lambda x: x**3 - 27, lambda x: 3 * x**2, **kwargs)
   >>> print("Root:", root, "Norm of correction:", norm_correction)


