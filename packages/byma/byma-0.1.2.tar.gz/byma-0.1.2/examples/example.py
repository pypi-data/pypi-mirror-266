import numpy as np
from byma.iteral import stationary as st
from byma.interface import NonlinearHeat
import matplotlib.pyplot as plt
import byma.pyplot.plots as pplt


if __name__ == '__main__':
    
    n = 4
    x = np.linspace(0, 1, n + 1)[1:-1]
    
    func = NonlinearHeat()
    V = np.random.rand(n - 1, 3)
    A = func.linGL1(n = n)
    eig, _ = np.linalg.eig(- A.toarray())
    
    V, BV, eigs = st.osim(A = - A, V = V, method = 'LU', verbose = 10)
    
    settings = {
        'title': "Orthogonal Subspace Iteration Method",
        'save_title': 'osim_eig_check',
        'xlabel': 'iterations',
        'ylabel': 'log-error',
        'label' : 'log-error',
        'scale': 'loglog'
    }
    
    error = []
    
    for e in eigs:
        error.append(np.linalg.norm(e - eig[:3]))
    
    pplt.plot(x = np.arange(len(error))  , y = error, settings = settings)
    
    
    