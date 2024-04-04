import numpy as np
from ...interface.BaseInterface import BaseInterface as bs
from .NonStationary import NonStationary as NonSt
import scipy.sparse as sp

_DEFAULT_OPTS = {
    'stop': 'normal', 
    'maxit': 1e4, 
    'tol': 1e-8, 
    'verbose': False,
    'mode': None, 
    'method': 'normal',
    }


def _returns(x, fnorm, dxnorm, mode, method):
    """
    Helper function to format the return value based on the mode.

    Parameters
    ----------
    x : array_like
        Root obtained after iterations.
    fnorm : float
        Norm of the residuals.
    dxnorm : float
        Norm of the correction.
    mode : str
        Mode of the output ('full', 'partial', None).
    method : str
        Stopping method used.

    Returns
    -------
    tuple
        Tuple containing the formatted output based on the mode.
    """
    
    if mode == 'full':
        return x, dxnorm, fnorm
    elif mode == 'partial':
        if method == 'normal': 
            return x, dxnorm 
        else: 
            return x, fnorm
        
    elif ((mode == None) or (mode == False)):
        return x, dxnorm, fnorm

@bs.set_defaults(default_cls = NonSt, default_opts=_DEFAULT_OPTS)
def newton(x, f, df, **kwargs):
    """
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
    """
    _opts = bs.opts(**kwargs)
    verbose = _opts['verbose']
    mode = _opts['mode']
    tol = _opts['tol']
    maxit = int(_opts['maxit'])
    stop = _opts['stop']
    
    if maxit <= 0 or not isinstance(maxit, int):
        raise ValueError("Maximum number of iterations 'maxit' must be a positive integer.")
    if tol <= 0:
        raise ValueError("Tolerance 'tol' must be a positive value.")
    
    if verbose:
        print('------ Newton Method summary ------')
        print(f'tollerence: {tol}')
        print(f'maximum iter: {maxit}')
        print(f'stopping criteria: {stop}')
        print(f'starting guess: {x}')
    
        print('------ Start iteration ------')
        
    normdx = []
    normf = []
    for iter in range(maxit):
        f_value = f(x)
        df_value = df(x)
        
        if sp.issparse(df_value) and sp.issparse(df_value):
            dx = sp.linalg.spsolve(df_value, -f_value)
            dxnorm = sp.linalg.norm(dx)
        else:
            dx = np.linalg.solve(df_value, -f_value)
            dxnorm = np.linalg.norm(dx)
        
        x += dx
        
        if sp.issparse(df_value) and sp.issparse(df_value):
            fnorm = sp.linalg.norm(f(x))
        else:
            fnorm = np.linalg.norm(f(x))
            
        normdx.append(dxnorm)
        normf.append(fnorm)
        
        if  verbose != 0 and verbose != False:
            if (iter % verbose == 0):
                print(f"Newton status at iteration {iter + 1}: ||dx|| = {dxnorm} and ||F|| = {fnorm}")
        
        if (fnorm < tol and stop == 'residual-check'):
            if verbose:
                print(f'Newton converged in {iter + 1} iterations with ||F|| = {fnorm}')
            return _returns(x, fnorm=fnorm, dxnorm=normdx, mode=mode, method=stop)
        
        if (dxnorm < tol and stop == 'normal'):
            if verbose:
                print(f'Newton converged in {iter + 1} iterations with ||dx|| = {dxnorm}')
            return _returns(x, fnorm=fnorm, dxnorm=normdx, mode=mode, method=stop)
        

    if verbose:
        print(f'Newton did not converge within {maxit} iterations')

    return _returns(x, fnorm=fnorm, dxnorm=normdx, mode=mode, method=stop)
