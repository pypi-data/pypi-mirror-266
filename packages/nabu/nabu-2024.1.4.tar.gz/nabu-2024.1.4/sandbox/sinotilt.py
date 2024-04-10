import numpy as np
from math import sqrt, pi

from nabu.utils import updiv, get_cuda_srcfile, _sizeof, nextpow2, convert_index
from nabu.cuda.utils import copy_array
from nabu.cuda.kernel import CudaKernel
import pycuda.driver as cuda
from pycuda import gpuarray as garray


# PATCH
import os
def get_cuda_srcfile(filename):
    # ~ cuda_src_folder = "/home/pierre/workspace/git/nabu/sandbox"
    cuda_src_folder = "/mntdirect/_scisoft/users/paleo/tmp/nabu_test/sandbox"
    return os.path.join(cuda_src_folder, filename)


class SinoTilter:
    def __init__(
        self,
        sino_shape,
        axis_tilt,
        angles=None,
        rot_center=None,
        axis_tilt_center=None
    ):

        self._init_geometry(sino_shape, angles, rot_center, axis_tilt, axis_tilt_center)
        self._allocate_memory()
        self._compute_angles()
        self._compile_kernels()
        self._bind_textures()


    def _init_geometry(self, sino_shape, angles, rot_center, axis_tilt, axis_tilt_center):
        self.sino_shape = sino_shape
        if len(sino_shape) == 3:
            n_slices, n_angles, dwidth = sino_shape
        else:
            raise ValueError("Expected 3D sinogram")
        n_sinos = n_slices
        self.dwidth = dwidth
        self.n_slices = n_slices
        self._set_slice_shape(None)
        self.n_sinos = n_sinos
        self.rot_center = rot_center or (self.dwidth - 1)/2.
        self.axis_pos = self.rot_center
        self._set_angles(angles, n_angles)
        if axis_tilt is None:
            axis_tilt = 0
        self.axis_tilt = axis_tilt
        if axis_tilt_center is None:
            y1 = (self.n_y - 1)/2.
            z1 = self.n_slices
            axis_tilt_center = (y1, z1)
        self.axis_tilt_center = axis_tilt_center


    def _set_slice_shape(self, slice_shape):
        n_y = self.dwidth
        n_x = self.dwidth
        if slice_shape is not None:
            if np.isscalar(slice_shape):
                slice_shape = (slice_shape, slice_shape)
            n_y, n_x = slice_shape
        self.n_x = n_x
        self.n_y = n_y
        self.slice_shape = (n_y, n_x)
        if self.n_slices > 1:
            self.slice_shape = (self.n_slices,) + self.slice_shape


    def _set_angles(self, angles, n_angles):
        self.n_angles = n_angles
        if angles is None:
            angles = n_angles
        if np.isscalar(angles):
            angles = np.linspace(0, np.pi, angles, False)
        else:
            assert len(angles) == self.n_angles
        self.angles = angles


    def _allocate_memory(self):
        self._d_sino_cua = cuda.np_to_array(np.zeros(self.sino_shape, "f"), "C")
        # 1D textures are not supported in pycuda
        self.h_sin = np.zeros((1, self.n_angles), "f")
        self.h_cos = np.zeros((1, self.n_angles), "f")
        self._d_sino = garray.zeros(self.sino_shape, "f")
        self._d_out = garray.zeros(self.sino_shape[1:], "f")
        self._d_proc = garray.zeros(self.sino_shape[1:], np.int32)


    def _compute_angles(self):
        self.h_cos[0] = np.cos(self.angles).astype("f")
        self.h_sin[0] = np.sin(self.angles).astype("f")
        self._d_sin = garray.to_gpu(self.h_sin[0])
        self._d_cos = garray.to_gpu(self.h_cos[0])


    def _get_kernel_options(self):
        sourcemodule_options = []
        block = (16, 16, 1)
        grid = (
            updiv(self.n_x, block[0]),
            updiv(self.n_y, block[1]),
            1
        )
        sourcemodule_options.append("-DBACKPROJ3D")
        shared_size = int(np.prod(block)) * 2
        shared_size *= 4 # sizeof(float32)
        self._kernel_options = {
            "file_name": get_cuda_srcfile("sino_tilt.cu"),
            "kernel_name": "sino_tilt",
            "kernel_signature": "PiiiifPPffffP",
            "texture_name": "tex_projections3D",
            "sourcemodule_options": sourcemodule_options,
            "grid": grid,
            "block": block,
            "shared_size": shared_size
        }


    def _compile_kernels(self):
        self._get_kernel_options()
        kern_opts = self._kernel_options
        # Configure backprojector
        self.gpu_projector = CudaKernel(
            kern_opts["kernel_name"],
            filename=kern_opts["file_name"],
            options=kern_opts["sourcemodule_options"]
        )
        self.texref_proj = self.gpu_projector.module.get_texref(
            kern_opts["texture_name"]
        )
        self.texref_proj.set_filter_mode(cuda.filter_mode.LINEAR)
        self.gpu_projector.prepare(kern_opts["kernel_signature"], [self.texref_proj])
        # Prepare kernel arguments
        self.kern_proj_args = [
            self._d_out,
            None, # z
            self.n_angles,
            self.dwidth,
            self.n_slices,
            self.axis_pos,
            self._d_cos,
            self._d_sin,
            np.cos(self.axis_tilt),
            np.sin(self.axis_tilt),
            self.axis_tilt_center[0],
            self.axis_tilt_center[1],
            self._d_proc
        ]
        self.kern_proj_kwargs = {
            "grid": kern_opts["grid"],
            "block": kern_opts["block"],
            "shared_size": kern_opts["shared_size"],
        }


    def _bind_textures(self):
        self.texref_proj.set_array(self._d_sino_cua)


    def transform(self, sino, z, output=None, do_checks=True):
        copy_array(self._d_sino_cua, sino, check=do_checks)
        self.kern_proj_args[1] = z
        if output is not None:
            self.kern_proj_args[0] = output # output has to be a gpuarray
        self.gpu_projector(
            *self.kern_proj_args,
            **self.kern_proj_kwargs
        )
        if output is not None:
            self.kern_proj_args[0] = self._d_out
            return output
        else:
            return self._d_out.get()


