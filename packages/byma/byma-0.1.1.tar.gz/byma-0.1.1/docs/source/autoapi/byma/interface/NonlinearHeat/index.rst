:py:mod:`byma.interface.NonlinearHeat`
======================================

.. py:module:: byma.interface.NonlinearHeat


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   byma.interface.NonlinearHeat.NonlinearHeat




.. py:class:: NonlinearHeat


   Damped stationary heat equation with discretization using finite difference method.

   The equation is given by:

   .. math::
       u_{xx} + \mu(u - \frac{1}{3}u^3)   x \in [0,1]
       u(0) = 1, u(1) = 0

   The linearized version is:

   .. math::
       u_{xx} + \mu u    x \in [0,1]
       u(0) = 1, u(1) = 0

   Functions:

   - `GL1(x, mu)`: Checks if x is a zero of the right-hand side.
   - `fGL1(u, n, mu)`: Computes the resulting sparse matrix.
   - `linGL1(n)`: Computes a 1d float vector for the linearized version.
   - `JacGL1(u, n, mu)`: Computes the Jacobian matrix.


   .. py:method:: GL1(x, mu)

      Computes the finite difference method for the damped stationary heat equation.

      Parameters
      ----------
      x : numpy.ndarray
          1D vector.
      mu : float
          Scalar parameter.

      Returns
      -------
      numpy.ndarray
          Result of the computation.



   .. py:method:: fGL1(**kwargs)

      Computes the resulting sparse matrix for the damped stationary heat equation.

      Parameters
      ----------
      **kwargs : dict
          Keyword arguments including 'u', 'n', and 'mu'.

      Returns
      -------
      numpy.ndarray
          Resulting sparse matrix.



   .. py:method:: linGL1(n, **kwargs)

      Computes a 1D float vector for the linearized version of the heat equation.

      Parameters
      ----------
      n : int
          Number of grid points.

      Returns
      -------
      numpy.ndarray
          1D float vector.



   .. py:method:: JacGL1(**kwargs)

      Computes the Jacobian matrix for the damped stationary heat equation.

      Parameters
      ----------
      **kwargs : dict
          Keyword arguments including 'u', 'n', and 'mu'.

      Returns
      -------
      numpy.ndarray
          Jacobian matrix.




