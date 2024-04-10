import numpy as np
import pytest
from scipy.ndimage import shift
from nabu.pipeline.params import fbp_filters
from nabu.utils import clip_circle
from nabu.testutils import get_data, generate_tests_scenarios, __do_long_tests__
from nabu.cuda.utils import get_cuda_context, __has_pycuda__
from nabu.opencl.utils import get_opencl_context, __has_pyopencl__

from nabu.processing.fft_cuda import has_skcuda, has_vkfft as has_vkfft_cu
from nabu.processing.fft_opencl import has_vkfft as has_vkfft_cl

__has_pycuda__ = __has_pycuda__ and (has_skcuda() or has_vkfft_cu())
__has_pyopencl__ = __has_pyopencl__ and has_vkfft_cl()

if __has_pycuda__:
    from nabu.reconstruction.fbp import CudaBackprojector
if __has_pyopencl__:
    from nabu.reconstruction.fbp_opencl import OpenCLBackprojector


scenarios = generate_tests_scenarios({"backend": ["cuda", "opencl"]})
if __do_long_tests__:
    scenarios = generate_tests_scenarios(
        {
            "backend": ["cuda", "opencl"],
            "input_on_gpu": [False, True],
            "output_on_gpu": [False, True],
            "use_textures": [True, False],
        }
    )


@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls
    cls.sino_512 = get_data("mri_sino500.npz")["data"]
    cls.ref_512 = get_data("mri_rec_astra.npz")["data"]
    # always use contiguous arrays
    cls.sino_511 = np.ascontiguousarray(cls.sino_512[:, :-1])
    # Could be set to 5.0e-2 when using textures. When not using textures, interpolation slightly differs
    cls.tol = 5.1e-2

    if __has_pycuda__:
        cls.cuda_ctx = get_cuda_context(cleanup_at_exit=False)
    if __has_pyopencl__:
        cls.opencl_ctx = get_opencl_context("all")
    yield
    if __has_pycuda__:
        cls.cuda_ctx.pop()


@pytest.mark.usefixtures("bootstrap")
class TestFBP:
    @staticmethod
    def clip_to_inner_circle(img, radius_factor=0.99):
        radius = int(radius_factor * max(img.shape) / 2)
        return clip_circle(img, radius=radius)

    def _get_backprojector(self, config, *bp_args, **bp_kwargs):
        if config["backend"] == "cuda":
            if not (__has_pycuda__):
                pytest.skip("Need pycuda + (scikit-cuda or pyvkfft)")
            Backprojector = CudaBackprojector
            ctx = self.cuda_ctx
        else:
            if not (__has_pyopencl__):
                pytest.skip("Need pyopencl + pyvkfft")
            Backprojector = OpenCLBackprojector
            ctx = self.opencl_ctx
        if config.get("use_textures", True) is False:
            # patch "extra_options"
            extra_options = bp_kwargs.pop("extra_options", {})
            extra_options["use_textures"] = False
            bp_kwargs["extra_options"] = extra_options
        return Backprojector(*bp_args, **bp_kwargs, backend_options={"ctx": ctx})

    @staticmethod
    def apply_fbp(config, backprojector, sinogram):
        if config.get("input_on_gpu", False):
            sinogram = backprojector._processing.set_array("sinogram", sinogram)
        if config.get("output_on_gpu", False):
            output = backprojector._processing.allocate_array("output", backprojector.slice_shape, dtype="f")
        else:
            output = None
        res = backprojector.fbp(sinogram, output=output)
        if config.get("output_on_gpu", False):
            res = res.get()
        return res

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_512(self, config):
        """
        Simple test of a FBP on a 512x512 slice
        """
        B = self._get_backprojector(config, (500, 512))
        res = self.apply_fbp(config, B, self.sino_512)

        delta_clipped = self.clip_to_inner_circle(res - self.ref_512)
        err_max = np.max(np.abs(delta_clipped))

        assert err_max < self.tol, "Something wrong with config=%s" % (str(config))

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_511(self, config):
        """
        Test FBP of a 511x511 slice where the rotation axis is at (512-1)/2.0
        """
        B = self._get_backprojector(config, (500, 511), rot_center=255.5)
        res = self.apply_fbp(config, B, self.sino_511)
        ref = self.ref_512[:-1, :-1]

        delta_clipped = self.clip_to_inner_circle(res - ref)
        err_max = np.max(np.abs(delta_clipped))

        assert err_max < self.tol, "Something wrong with config=%s" % (str(config))

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_roi(self, config):
        """
        Test FBP in region of interest
        """
        sino = self.sino_511

        B0 = self._get_backprojector(config, sino.shape, rot_center=255.5)
        ref = B0.fbp(sino)

        def backproject_roi(roi, reference):
            B = self._get_backprojector(config, sino.shape, rot_center=255.5, slice_roi=roi)
            res = self.apply_fbp(config, B, sino)
            err_max = np.max(np.abs(res - reference))
            return err_max

        cases = {
            # Test 1: use slice_roi=(0, -1, 0, -1), i.e plain FBP of whole slice
            1: [(0, None, 0, None), ref],
            # Test 2: horizontal strip
            2: [(0, None, 50, 55), ref[50:55, :]],
            # Test 3: vertical strip
            3: [(60, 65, 0, None), ref[:, 60:65]],
            # Test 4: rectangular inner ROI
            4: [(157, 162, 260, -10), ref[260:-10, 157:162]],
        }
        for roi, ref in cases.values():
            err_max = backproject_roi(roi, ref)
            assert err_max < self.tol, "Something wrong with ROI = %s for config=%s" % (
                str(roi),
                str(config),
            )

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_axis_corr(self, config):
        """
        Test the "axis correction" feature
        """
        sino = self.sino_512

        # Create a sinogram with a drift in the rotation axis
        def create_drifted_sino(sino, drifts):
            out = np.zeros_like(sino)
            for i in range(sino.shape[0]):
                out[i] = shift(sino[i], drifts[i])
            return out

        drifts = np.linspace(0, 20, sino.shape[0])
        sino = create_drifted_sino(sino, drifts)

        B = self._get_backprojector(config, sino.shape, extra_options={"axis_correction": drifts})
        res = self.apply_fbp(config, B, sino)

        delta_clipped = clip_circle(res - self.ref_512, radius=200)
        err_max = np.max(np.abs(delta_clipped))
        # Max error is relatively high, migh be due to interpolation of scipy shift in sinogram
        assert err_max < 10.0, "Max error is too high"

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_clip_circle(self, config):
        """
        Test the "clip outer circle" parameter in (extra options)
        """
        sino = self.sino_512
        tol = 1e-5

        for rot_center in [None, sino.shape[1] / 2.0 - 10, sino.shape[1] / 2.0 + 15]:
            B = self._get_backprojector(
                config, sino.shape, rot_center=rot_center, extra_options={"clip_outer_circle": True}
            )
            res = self.apply_fbp(config, B, sino)

            B0 = self._get_backprojector(
                config, sino.shape, rot_center=rot_center, extra_options={"clip_outer_circle": False}
            )
            res_noclip = B0.fbp(sino)
            ref = self.clip_to_inner_circle(res_noclip, radius_factor=1)

            abs_diff = np.abs(res - ref)
            err_max = np.max(abs_diff)
            assert err_max < tol, "Max error is too high for rot_center=%s ; %s" % (str(rot_center), str(config))

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_centered_axis(self, config):
        """
        Test the "centered_axis" parameter (in extra options)
        """
        sino = np.pad(self.sino_512, ((0, 0), (100, 0)))
        rot_center = (self.sino_512.shape[1] - 1) / 2.0 + 100

        B0 = self._get_backprojector(config, self.sino_512.shape)
        ref = B0.fbp(self.sino_512)

        # Check that "centered_axis" worked

        B = self._get_backprojector(config, sino.shape, rot_center=rot_center, extra_options={"centered_axis": True})
        res = self.apply_fbp(config, B, sino)
        # The outside region (outer circle) is different as "res" is a wider slice
        diff = self.clip_to_inner_circle(res[50:-50, 50:-50] - ref)
        err_max = np.max(np.abs(diff))
        assert err_max < 5e-2, "centered_axis without clip_circle: something wrong"

        # Check that "clip_outer_circle" works when used jointly with "centered_axis"
        B = self._get_backprojector(
            config,
            sino.shape,
            rot_center=rot_center,
            extra_options={
                "centered_axis": True,
                "clip_outer_circle": True,
            },
        )
        res2 = self.apply_fbp(config, B, sino)
        diff = res2 - self.clip_to_inner_circle(res, radius_factor=1)
        err_max = np.max(np.abs(diff))
        assert err_max < 1e-5, "centered_axis with clip_circle: something wrong"

    @pytest.mark.parametrize("config", scenarios)
    def test_fbp_filters(self, config):
        for filter_name in set(fbp_filters.values()):
            if filter_name in [None, "ramlak"]:
                continue
            B = self._get_backprojector(config, self.sino_512.shape, filter_name=filter_name)
            self.apply_fbp(config, B, self.sino_512)
            # not sure what to check in this case

    @pytest.mark.parametrize("config", scenarios)
    def test_differentiated_backprojection(self, config):
        # test Hilbert + DBP
        sino_diff = np.diff(self.sino_512, axis=1, prepend=0).astype("f")
        # Need to translate the axis a little bit, because of non-centered differentiation.
        # prepend -> +0.5 ; append -> -0.5
        B = self._get_backprojector(config, sino_diff.shape, filter_name="hilbert", rot_center=255.5 + 0.5)
        rec = self.apply_fbp(config, B, sino_diff)
        # Looks good, but all frequencies are not recovered. Use a metric like SSIM or FRC ?
