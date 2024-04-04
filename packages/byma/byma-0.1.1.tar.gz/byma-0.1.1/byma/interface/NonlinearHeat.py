import numpy as np
import scipy.sparse as sp


class NonlinearHeat():
    """
    Damped stationary heat equation with discretization using finite difference method.

    The equation is given by:

    .. math::
        u_{xx} + \mu(u - \\frac{1}{3}u^3)   x \in [0,1]
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

    """
    
    def __init__(self):
        pass

    def GL1(self, x, mu):
        """
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

        """
        A = self.linGL1(n = len(x) + 1)
        return A @ x + mu * (x - x**3)

    def fGL1(self, **kwargs):
        """
        Computes the resulting sparse matrix for the damped stationary heat equation.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments including 'u', 'n', and 'mu'.

        Returns
        -------
        numpy.ndarray
            Resulting sparse matrix.

        """
        u = kwargs.get('u')
        n = kwargs.get('n')
        assert type(n) == int, 'integer only'
        assert np.ndim(u) == 1, '1d only'
        
        mu = kwargs.get("mu", np.pi**2)
        A = self.linGL1(n = n)
        vec = mu*u  - (mu /3) * (u ** 3)
        
        return (A @ u + vec)
    
    def linGL1(self, n, **kwargs):
        """
        Computes a 1D float vector for the linearized version of the heat equation.

        Parameters
        ----------
        n : int
            Number of grid points.

        Returns
        -------
        numpy.ndarray
            1D float vector.

        """
        assert type(n) == int, 'integer only'
        
        top = np.full(n - 2, 1)
        mid = np.full(n - 1, -2)
        bot = np.full(n - 2, 1)
        h = 1/(n - 1)
        
        return (h**(-2)) * sp.csr_matrix(sp.diags([ top , mid , bot ] , [1 , 0 , -1]))
    
    def JacGL1(self, **kwargs):
        """
        Computes the Jacobian matrix for the damped stationary heat equation.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments including 'u', 'n', and 'mu'.

        Returns
        -------
        numpy.ndarray
            Jacobian matrix.

        """
        u = kwargs.get('u')
        n = kwargs.get('n', int(5))
        mu = kwargs.get("mu", np.pi)
        assert type(n) == int, 'integer only'
        # assert np.ndim(u) == 1, '1d only'
        
        A = self.linGL1(n=n)
        
        # top = np.full(n - 2, 1)
        # bot = np.full(n - 2, - 1)
        # B = ((2*h)**(-1)) * sp.csr_matrix(sp.diags([ top , bot ] , [1 , -1]))
        # vec = mu * B @ (1 - u**2)
       
        # ttop = np.full(n - 3, 1)
        # top = np.full(n - 2, - 2)
        # bot = np.full(n - 2, - 2)
        # bbot = np.full(n - 3, - 1)
        # C = ((2*(h**3))**(-1)) * sp.csr_matrix(sp.diags([ ttop, top , bot, bbot ] , [2, 1 , -1, -2]))
        # print(C == B @ A)
        
        # return (B @ A) @ u + vec
        return A + mu * (np.eye(n - 1) - np.diag(u**2))