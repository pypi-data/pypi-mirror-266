%%cython --compile-args=-fopenmp --link-args=-fopenmp -a
#%%cython -a
#cython: embedsignature=True, language_level=3, binding=True
#cython: boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False,
## This is for developping:
## cython: profile=True, warn.undeclared=True, warn.unused=True, warn.unused_result=False, warn.unused_arg=True

import numpy as np
from cython.parallel import prange
"""
def bin2_cython(float[:, ::1] img):
    cdef:
        float[:, ::1] res
        int i, j, Ny, Nx
          
    shp = img.shape
    Ny, Nx = (img.shape[0]//2, img.shape[1]//2)
    res = np.zeros((Ny, Nx), dtype="f")
    for i in prange(Ny, nogil=True): 
        for j in range(Nx):
            res[i, j] = 0.25 * (img[2*i, 2*j] + img[2*i+1, 2*j] + img[2*i, 2*j+1] + img[2*i+1, 2*j+1])
    return np.asarray(res)
"""


def bin2_cython(unsigned short[:, ::1] img):
    cdef:
        float[:, ::1] res
        int i, j, Ny, Nx
          
    shp = img.shape
    Ny, Nx = (img.shape[0]//2, img.shape[1]//2)
    res = np.zeros((Ny, Nx), dtype="f")
    for i in prange(Ny, nogil=True): 
        for j in range(Nx):
            res[i, j] = 0.25 * (img[2*i, 2*j] + img[2*i+1, 2*j] + img[2*i, 2*j+1] + img[2*i+1, 2*j+1])
    return np.asarray(res)