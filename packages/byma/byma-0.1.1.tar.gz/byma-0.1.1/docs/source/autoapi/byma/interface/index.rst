:py:mod:`byma.interface`
========================

.. py:module:: byma.interface

.. autoapi-nested-parse::

   BaseInterface Module
   ====================

   This module provides a base interface for defining default classes and options. It includes functionality for setting default parameters, updating interface options, and retrieving updated options.



Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   BaseInterface/index.rst
   NonlinearHeat/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   byma.interface.BaseInterface
   byma.interface.NonlinearHeat




.. py:class:: BaseInterface(default_cls, default_opts, **kwargs)


   Defines a base interface

   .. py:method:: set_defaults(default_cls, default_opts={})
      :staticmethod:

      Decorator for setting default interface and parameters.

      Parameters
      ----------
      default_cls : obj
          The default class instance.
      default_opts : dict, optional
          Default options for the interface (default is an empty dictionary).

      Returns
      -------
      callable
          A decorator function that sets default interface and parameters.


   .. py:method:: opts(**kwargs)
      :staticmethod:

      Method for setting options for the interface.

      Parameters
      ----------
      kwargs : dict
          Additional keyword arguments.

      Returns
      -------
      dict
          A dictionary containing updated interface and parameters.



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




