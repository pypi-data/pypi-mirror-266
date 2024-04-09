from contextlib import contextmanager
from time import time
import numba
import numpy as np


@numba.njit
def ceildiv(a, b):
    return -(a // -b)


@contextmanager
def timer(name):
    print(f'{name}...')
    start = time()
    yield
    print(f'{name} took {time() - start} seconds')


@numba.njit(parallel=True)
def check_equality(a, b):
    assert a.shape == b.shape
    end = a.shape[0]
    nthreads = 64
    block_size = ceildiv(end, nthreads)
    results = np.ones(nthreads, dtype=np.bool_)
    for t in numba.prange(64):
        start = t * block_size
        end = min((t + 1) * block_size, end)
        result = True
        for i in range(start, end):
            result = result & (a[i] == b[i])
        results[t] = result
    assert np.all(results)