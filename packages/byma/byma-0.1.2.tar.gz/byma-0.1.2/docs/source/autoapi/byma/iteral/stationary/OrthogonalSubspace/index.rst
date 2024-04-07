:py:mod:`byma.iteral.stationary.OrthogonalSubspace`
===================================================

.. py:module:: byma.iteral.stationary.OrthogonalSubspace


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   byma.iteral.stationary.OrthogonalSubspace.osim



.. py:function:: osim(A, V, **kwargs)

   Orthogonal Subspace Iteration Method (OSIM).

   Args:
   A : numpy.ndarray
       The matrix to compute the eigenvalues and eigenvectors for.
   V : numpy.ndarray
       Initial guess of eigenvectors.

   Keyword Arguments:
       tol : float, optional
           Tolerance for convergence (default: 1e-8).
       maxit : int, optional
           Maximum number of iterations (default: 100).
       stop : str, optional
           Stopping criteria for convergence. Options are 'eig' (default), 'matrix', or 'residual'.
       method : str, optional
           Method for solving linear systems. Options are 'LU' (default) or any method supported by scipy.linalg.lu.
       verbose : bool, optional
           If True, prints iteration information (default: True).

   Returns:
   numpy.ndarray
       Matrix of eigenvectors.
   numpy.ndarray
       Matrix of transformed eigenvectors.
   tuple
       Tuple containing eigenvalues at each iteration.

   Notes:
   This function implements the Orthogonal Subspace Iteration Method (OSIM) to compute eigenvectors and eigenvalues of a matrix A.

   Examples:
   >>> import numpy as np
   >>> from iteral import stationary as st
   >>> A = np.array([[1, 0], [0, 1]])
   >>> V = np.array([[1], [0]])
   >>> V, BV, iter = st.osim(A, V, tol=1e-8, maxit=1000, stop='eig', method='LU')

   You can also pass keyword arguments using a dictionary. For example:
   >>> kwargs = {'tol': 1e-8, 'maxit': 1000, 'stop': 'eig', 'method': 'LU'}
   >>> V, BV, iter = osim(A, V, **kwargs)

   You can also pass keyword arguments using two separate dictionaries for parameters and interface. For example:
   >>> parameters = {'tol': 1e-8, 'maxit': 1000, 'stop': 'eig', 'method': 'LU'}
   >>> interface = {'verbose': True}
   >>> V, BV, iter = st.osim(A, V, parameters=parameters, interface=interface)


