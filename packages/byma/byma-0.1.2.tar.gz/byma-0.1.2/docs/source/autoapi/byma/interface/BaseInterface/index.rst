:py:mod:`byma.interface.BaseInterface`
======================================

.. py:module:: byma.interface.BaseInterface


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   byma.interface.BaseInterface.BaseInterface




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



