import numpy as np
from math import sqrt, pi

from ..utils import updiv, get_cuda_srcfile, _sizeof, nextpow2, convert_index
from ..cuda.utils import copy_array
from ..cuda.processing import CudaProcessing
from ..cuda.kernel import CudaKernel
from .filtering import SinoFilter
import pycuda.driver as cuda
from pycuda import gpuarray as garray
from .fbp import Backprojector

class PolarBackprojector(Backprojector):
    """
    Cuda Backprojector with output in polar coordinates.
    """

    cuda_fname = "backproj.cu"
    cuda_kernel_name = "backproj_polar"


    # patch parent method: force slice_shape to (n_angles, n_x)
    def _set_angles(self, angles, n_angles):
        Backprojector._set_angles(self, angles, n_angles)
        self.slice_shape = (self.n_angles, self.n_x)

    # patch parent method:
    def _set_slice_roi(self, slice_roi):
        if slice_roi is not None:
            raise ValueError("slice_roi is not supported with this class")
        Backprojector._set_slice_roi(self, slice_roi)

    # patch parent method: update kernel args
    def _compile_kernels(self):
        n_y = self.n_y
        self.n_y = self.n_angles
        Backprojector._compile_kernels()
        self.n_y = n_y

