import numpy as np
import scipy.sparse as sp
from ..iteral.nonstationary import newton
from ..interface.BaseInterface import BaseInterface as bs
from .Bifurcation import Bifurcation as Bf

_DEFAULT_OPTS = {
    'maxit_cont' : 1000,
    'verbose': True,
    'mode': None, 
    'method': 'normal',
    }


def _returns(x, branch, target, mode, dxnorms, mu0):
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
    
    if target == None:
        if mode == 'full':
            return branch, dxnorms, mu0 
        elif mode == 'partial':
            return branch, mu0
        else:
            return x, mu0
    else:
        if mode == 'full':
            return branch, dxnorms
        elif mode == 'partial':
            return branch
        else:
            return x


def step(x, df, dfmu, dx, dmu, **kwargs):
        """
    Perform one step of the continuation.

    :param x: array_like
        Current state.
    :param df: callable
        Function to evaluate the Jacobian matrix with respect to state variable x.
    :param dfmu: callable
        Function to evaluate the Jacobian matrix derivative with respect to parameter mu.
    :param dx: array_like
        Current tangent with respect to state variable.
    :param dmu: float or array_like
        Incremental change in the parameter value.
    :param kwargs: dict
        Additional keyword arguments.

    :return: tuple
        A tuple containing the updated state x and the norm of the correction and the derivative of x w.r.t parameter

    :description:
    This function performs one step of the continuation, updating the state variable x and the tangent dx using the provided functions for evaluating the Jacobian matrix and its derivative with respect to the parameter.
    """
        
        # Predictor
        x += dmu * dx
        kwargs['mode'] = 'partial'
        kwargs['stop'] = 'normal'
  
        # Corrector 
        x, dxnorm = newton(x = x, f = dfmu, df = df, **kwargs)

        # Compute the tangent
        dfx1 = df(x)
        dfmu1 = dfmu(x)
        if sp.issparse(dfx1) and sp.issparse(dfmu1):
            dx = sp.linalg.spsolve(dfx1, -dfmu1)
            
        else:
            dx = np.linalg.solve(dfx1, -dfmu1)
            
        return x, dxnorm, dx

@bs.set_defaults(default_cls = Bf, default_opts=_DEFAULT_OPTS)
def cont(x0, dx0, start, df, dfmu, dmu=None, target=None, **kwargs):
    """
    Perform a continuation in parameter value from a starting value to a target value or until the maximum iteration is met, with constant step size.

    This function performs a continuation in parameter space from a starting value to a target value, or until the maximum iteration is met, adjusting the state variable x along the way. The continuation is carried out using the provided functions for evaluating the Jacobian matrix and its derivative with respect to the parameter.

    :param x0: array_like
        Initial state.
    :param dx0: array_like
        Initial tangent with respect to state variable.
    :param start: float
        Starting parameter value.
    :param df: callable
        Function to evaluate the Jacobian matrix with respect to state variable x and parameter mu.
    :param dfmu: callable
        Function to evaluate the Jacobian matrix derivative with respect to parameter mu.
    :param dmu: float or array_like, optional
        Incremental change in the parameter value for each iteration. If None and target is None, raises ValueError.
    :param target: float or None, optional
        Target parameter value. If None, continuation is performed until maxit_con iterations.
    :param kwargs: dict
        Additional keyword arguments for customization.
            maxit_con : int, optional
                Maximum number of continuation steps. Default is 1000.
            method : str, optional
                Continuation method ('normal' or 'pseudo-arclength'). Default is 'normal'.
            mode : str, optional
                Return mode ('partial' or 'full'). Default is 'partial'.
            Other keyword arguments : Additional parameters specific to the step function used internally.

    :return: tuple or array_like
        Depending on the mode specified in kwargs, returns either a tuple or an array.
            - In 'partial' mode, returns a tuple containing the final state x and the final parameter value mu.
            - In 'full' mode, returns an array containing all the states x, an array of the norm of the correction at each step, and the final parameter value mu (if target is None).

    :raises:
        ValueError: If either 'dmu' or 'target' should be not 'None' but are not provided.
        ValueError: If the provided continuation method is invalid. Choose either 'normal' or 'pseudo-arclength'.

    Examples
    =============
        >>> # Define the functions df and dfmu
        >>> def df(x, mu0):
        >>>     # Compute the Jacobian matrix with respect to state variable x and parameter mu
        >>>     pass
        >>> def dfmu(x, mu0):
        >>>     # Compute the Jacobian matrix derivative with respect to parameter mu
        >>>     pass
        >>> 
        >>> # Define the initial state and tangent
        >>> x0 = np.array([1.0, 2.0])
        >>> dx0 = np.array([0.1, 0.1])
        >>> 
        >>> # Perform continuation from start value to target value
        >>> start = 0.0
        >>> target = 1.0
        >>> result = cont(x0, dx0, start, df, dfmu, target=target, maxit_con=1000, method='normal', mode='full')
        >>> print(result)
    """
    _opts = bs.opts(**kwargs)
    mode_con = _opts['mode']
    method = _opts['method']
    maxit_con = _opts['maxit_cont']
    verbose = _opts['verbose']
    
    x = x0
    dx = dx0
    mu = start

    # Set some parameters
    if (target is None) and (dmu is None):
        raise ValueError("Either 'dmu' or 'target' should be not 'None'")
    
    else:
        mus = np.linspace(mu, target, maxit_con)
        
    # Perform the continuation
    branch = []
    dxnorms = []
    
    if verbose:
        print('------ Continuation Method summary ------')
        print(f'starting solution: {x0}')
        print(f'starting parameter: {start}')
        print(f'maximum iter: {maxit_con}')
        print(f'method: {method}')
    
        print('------ Start iteration ------')

    for j in range(maxit_con):
        
        if target is None:
            mu0 = mu0 + dmu if isinstance(dmu, float) else mu0 + dmu[j]
        else:
            mu0 = mus[j]
            dmu = mu - mu0 if mu != start else mu0 - mus[j]

        df1 = lambda x: df(x = x, mu = mu0)
        dfmu1 = lambda x: dfmu(x = x, mu = mu0)
        
        if method == 'normal':
            x, dxnorm, dx = step(x, df=df1, dfmu=dfmu1, dx=dx, dmu=dmu, **kwargs)
        elif method == 'pseudo-arclength':
            raise ValueError("Pseudo-arclength'conitnuation is not yet avialible")
        else:
            raise ValueError("Invalid continuation method. Choose either 'normal' or 'pseudo-arclength'.")

        branch.append(x)
        dxnorms.append(dxnorm)

    mode = mode_con
    return _returns(x, branch, target, mode, dxnorms, mu0)