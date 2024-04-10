# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "13/05/2022"


import os
from silx.image.phantomgenerator import PhantomGenerator
from scipy.ndimage import shift as scipy_shift
import numpy
import pytest
from nabu.stitching.config import (
    PreProcessedZStitchingConfiguration,
    PostProcessedZStitchingConfiguration,
)
from nabu.utils import Progress
from nabu.stitching.config import KEY_IMG_REG_METHOD, NormalizationBySample
from nabu.stitching.overlap import ZStichOverlapKernel, OverlapStitchingStrategy
from nabu.stitching.z_stitching import (
    PostProcessZStitcher,
    PreProcessZStitcher,
    stitch_vertically_raw_frames,
    ZStitcher,
)
from nxtomo.nxobject.nxdetector import ImageKey
from nxtomo.utils.transformation import UDDetTransformation, LRDetTransformation
from nxtomo.application.nxtomo import NXtomo
from nabu.stitching.alignment import AlignmentAxis1, AlignmentAxis2
from tomoscan.factory import Factory as TomoscanFactory
from tomoscan.utils.volume import concatenate as concatenate_volumes
from tomoscan.esrf.scan.nxtomoscan import NXtomoScan
from tomoscan.esrf.volume import HDF5Volume, EDFVolume
from tomoscan.esrf.volume.jp2kvolume import JP2KVolume, has_minimal_openjpeg
from tomoscan.esrf.volume.tiffvolume import TIFFVolume, has_tifffile
from nabu.stitching.utils import ShiftAlgorithm
import h5py


strategies_to_test_weights = (
    OverlapStitchingStrategy.CLOSEST,
    OverlapStitchingStrategy.COSINUS_WEIGHTS,
    OverlapStitchingStrategy.LINEAR_WEIGHTS,
    OverlapStitchingStrategy.MEAN,
)


def build_raw_volume():
    """util to create some raw volume"""
    raw_volume = numpy.stack(
        [
            PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float32) * 256.0,
            PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float32) * 128.0,
            PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float32) * 32.0,
            PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float32) * 16.0,
        ]
    )
    assert raw_volume.shape == (4, 120, 120)
    raw_volume = numpy.rollaxis(raw_volume, axis=1, start=0)
    assert raw_volume.shape == (120, 4, 120)
    return raw_volume


@pytest.mark.parametrize("strategy", strategies_to_test_weights)
def test_overlap_z_stitcher(strategy):
    frame_width = 128
    frame_height = frame_width
    frame_1 = PhantomGenerator.get2DPhantomSheppLogan(n=frame_width)
    stitcher = ZStichOverlapKernel(
        stitching_strategy=strategy,
        overlap_size=frame_height,
        frame_width=128,
    )
    stitched_frame = stitcher.stitch(frame_1, frame_1)[0]
    assert stitched_frame.shape == (frame_height, frame_width)
    # check result is close to the expected one
    numpy.testing.assert_allclose(frame_1, stitched_frame, atol=10e-10)

    # check sum of weights ~ 1.0
    numpy.testing.assert_allclose(
        stitcher.weights_img_1 + stitcher.weights_img_2,
        numpy.ones_like(stitcher.weights_img_1),
    )


@pytest.mark.parametrize("dtype", (numpy.float16, numpy.float32))
def test_z_stitch_raw_frames(dtype):
    """
    test z_stitch_raw_frames: insure a stitching with 3 frames and different overlap can be done
    """
    ref_frame_width = 256
    frame_ref = PhantomGenerator.get2DPhantomSheppLogan(n=ref_frame_width).astype(dtype)

    # split the frame into several part
    frame_1 = frame_ref[0:100]
    frame_2 = frame_ref[80:164]
    frame_3 = frame_ref[154:]

    kernel_1 = ZStichOverlapKernel(frame_width=ref_frame_width, overlap_size=20)
    kernel_2 = ZStichOverlapKernel(frame_width=ref_frame_width, overlap_size=10)

    stitched = stitch_vertically_raw_frames(
        frames=(frame_1, frame_2, frame_3),
        output_dtype=dtype,
        overlap_kernels=(kernel_1, kernel_2),
        raw_frames_compositions=None,
        overlap_frames_compositions=None,
        key_lines=(
            (
                90,  # frame_1 height - kernel_1 height / 2.0
                10,  # kernel_1 height / 2.0
            ),
            (
                79,  # frame_2 height - kernel_2 height / 2.0 ou 102-20 ?
                5,  # kernel_2 height / 2.0
            ),
        ),
    )

    assert stitched.shape == frame_ref.shape
    numpy.testing.assert_array_almost_equal(frame_ref, stitched)


def test_z_stitch_raw_frames_2():
    """
    test z_stitch_raw_frames: insure a stitching with 3 frames and different overlap can be done
    """
    ref_frame_width = 256
    frame_ref = PhantomGenerator.get2DPhantomSheppLogan(n=ref_frame_width).astype(numpy.float32)

    # split the frame into several part
    frame_1 = frame_ref.copy()
    frame_2 = frame_ref.copy()
    frame_3 = frame_ref.copy()

    kernel_1 = ZStichOverlapKernel(frame_width=ref_frame_width, overlap_size=10)
    kernel_2 = ZStichOverlapKernel(frame_width=ref_frame_width, overlap_size=10)

    stitched = stitch_vertically_raw_frames(
        frames=(frame_1, frame_2, frame_3),
        output_dtype=numpy.float32,
        overlap_kernels=(kernel_1, kernel_2),
        raw_frames_compositions=None,
        overlap_frames_compositions=None,
        key_lines=((20, 20), (105, 105)),
    )

    assert stitched.shape == frame_ref.shape
    numpy.testing.assert_array_almost_equal(frame_ref, stitched)


_stitching_configurations = (
    # simple case where shifts are provided
    {
        "n_proj": 4,
        "raw_pos": ((0, 0, 0), (-90, 0, 0), (-180, 0, 0)),  # requested shift to
        "input_pos": ((0, 0, 0), (-90, 0, 0), (-180, 0, 0)),  # requested shift to
        "raw_shifts": ((0, 0), (-90, 0), (-180, 0)),
    },
    # simple case where shift is found from z position
    {
        "n_proj": 4,
        "raw_pos": ((90, 0, 0), (0, 0, 0), (-90, 0, 0)),
        "input_pos": ((90, 0, 0), (0, 0, 0), (-90, 0, 0)),
        "check_bb": ((40, 140), (-50, 50), (-140, -40)),
        "axis_0_params": {
            KEY_IMG_REG_METHOD: ShiftAlgorithm.NONE,
        },
        "axis_2_params": {
            KEY_IMG_REG_METHOD: ShiftAlgorithm.NONE,
        },
        "raw_shifts": ((0, 0), (-90, 0), (-180, 0)),
    },
)


@pytest.mark.parametrize("configuration", _stitching_configurations)
@pytest.mark.parametrize("dtype", (numpy.float32, numpy.int16))
def test_PreProcessZStitcher(tmp_path, dtype, configuration):
    """
    test PreProcessZStitcher class and insure a full stitching can be done automatically.
    """
    n_proj = configuration["n_proj"]
    ref_frame_width = 280
    raw_frame_height = 100
    ref_frame = PhantomGenerator.get2DPhantomSheppLogan(n=ref_frame_width).astype(dtype) * 256.0

    # add some mark for image registration
    ref_frame[:, 96] = -3.2
    ref_frame[:, 125] = 9.1
    ref_frame[:, 165] = 4.4
    ref_frame[:, 200] = -2.5
    # create raw data
    frame_0_shift, frame_1_shift, frame_2_shift = configuration["raw_shifts"]
    frame_0 = scipy_shift(ref_frame, shift=frame_0_shift)[:raw_frame_height]
    frame_1 = scipy_shift(ref_frame, shift=frame_1_shift)[:raw_frame_height]
    frame_2 = scipy_shift(ref_frame, shift=frame_2_shift)[:raw_frame_height]

    frames = frame_0, frame_1, frame_2
    frame_0_input_pos, frame_1_input_pos, frame_2_input_pos = configuration["input_pos"]
    frame_0_raw_pos, frame_1_raw_pos, frame_2_raw_pos = configuration["raw_pos"]

    # create a Nxtomo for each of those raw data
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    z_position = (
        frame_0_raw_pos[0],
        frame_1_raw_pos[0],
        frame_2_raw_pos[0],
    )
    scans = []
    for (i_frame, frame), z_pos in zip(enumerate(frames), z_position):
        nx_tomo = NXtomo()
        nx_tomo.sample.z_translation = [z_pos] * n_proj
        nx_tomo.sample.rotation_angle = numpy.linspace(0, 180, num=n_proj, endpoint=False)
        nx_tomo.instrument.detector.image_key_control = [ImageKey.PROJECTION] * n_proj
        nx_tomo.instrument.detector.x_pixel_size = 1.0
        nx_tomo.instrument.detector.y_pixel_size = 1.0
        nx_tomo.instrument.detector.distance = 2.3
        nx_tomo.energy = 19.2
        nx_tomo.instrument.detector.data = numpy.asarray([frame] * n_proj)

        file_path = os.path.join(raw_data_dir, f"nxtomo_{i_frame}.nx")
        entry = f"entry000{i_frame}"
        nx_tomo.save(file_path=file_path, data_path=entry)
        scans.append(NXtomoScan(scan=file_path, entry=entry))

    # if requested: check bounding box
    check_bb = configuration.get("check_bb", None)
    if check_bb is not None:
        for scan, expected_bb in zip(scans, check_bb):
            assert scan.get_bounding_box(axis="z") == expected_bb
    output_file_path = os.path.join(output_dir, "stitched.nx")
    output_data_path = "stitched"
    z_stich_config = PreProcessedZStitchingConfiguration(
        stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
        overwrite_results=True,
        axis_0_pos_px=(
            frame_0_input_pos[0],
            frame_1_input_pos[0],
            frame_2_input_pos[0],
        ),
        axis_1_pos_px=(
            frame_0_input_pos[1],
            frame_1_input_pos[1],
            frame_2_input_pos[1],
        ),
        axis_2_pos_px=(
            frame_0_input_pos[2],
            frame_1_input_pos[2],
            frame_2_input_pos[2],
        ),
        axis_0_pos_mm=None,
        axis_1_pos_mm=None,
        axis_2_pos_mm=None,
        input_scans=scans,
        output_file_path=output_file_path,
        output_data_path=output_data_path,
        axis_0_params=configuration.get("axis_0_params", {}),
        axis_1_params=configuration.get("axis_1_params", {}),
        axis_2_params=configuration.get("axis_2_params", {}),
        output_nexus_version=None,
        slices=None,
        slurm_config=None,
        slice_for_cross_correlation="middle",
        pixel_size=None,
    )
    stitcher = PreProcessZStitcher(z_stich_config)
    output_identifier = stitcher.stitch()
    assert output_identifier.file_path == output_file_path
    assert output_identifier.data_path == output_data_path

    created_nx_tomo = NXtomo().load(
        file_path=output_identifier.file_path,
        data_path=output_identifier.data_path,
        detector_data_as="as_numpy_array",
    )

    assert created_nx_tomo.instrument.detector.data.ndim == 3
    mean_abs_error = configuration.get("mean_abs_error", None)
    if mean_abs_error is not None:
        assert (
            numpy.mean(numpy.abs(ref_frame - created_nx_tomo.instrument.detector.data[0, :ref_frame_width, :]))
            < mean_abs_error
        )
    else:
        numpy.testing.assert_array_almost_equal(
            ref_frame, created_nx_tomo.instrument.detector.data[0, :ref_frame_width, :]
        )

    # check also other metadata are here
    assert created_nx_tomo.instrument.detector.distance.value == 2.3
    assert created_nx_tomo.energy.value == 19.2
    numpy.testing.assert_array_equal(
        created_nx_tomo.instrument.detector.image_key_control,
        numpy.asarray([ImageKey.PROJECTION.PROJECTION] * n_proj),
    )

    # check configuration has been saved
    with h5py.File(output_identifier.file_path, mode="r") as h5f:
        assert "stitching_configuration" in h5f[output_identifier.data_path]


slices_to_test_pre = (
    {
        "slices": (None,),
        "complete": True,
    },
    {
        "slices": (("first",), ("middle",), ("last",)),
        "complete": False,
    },
    {
        "slices": ((0, 1, 2), slice(3, -1, 1)),
        "complete": True,
    },
)


@pytest.mark.parametrize("configuration_dist", slices_to_test_pre)
def test_DistributePreProcessZStitcher(tmp_path, configuration_dist):
    slices = configuration_dist["slices"]
    complete = configuration_dist["complete"]

    n_projs = 100
    raw_data = numpy.arange(100 * 128 * 128).reshape((100, 128, 128))

    # create raw data
    frame_0 = raw_data[:, 60:]
    assert frame_0.ndim == 3
    frame_0_pos = 40
    frame_1 = raw_data[:, 0:80]
    assert frame_1.ndim == 3
    frame_1_pos = 94
    frames = (frame_0, frame_1)
    z_positions = (frame_0_pos, frame_1_pos)

    # create a Nxtomo for each of those raw data
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    scans = []
    for (i_frame, frame), z_pos in zip(enumerate(frames), z_positions):
        nx_tomo = NXtomo()
        nx_tomo.sample.z_translation = [z_pos] * n_projs
        nx_tomo.sample.rotation_angle = numpy.linspace(0, 180, num=n_projs, endpoint=False)
        nx_tomo.instrument.detector.image_key_control = [ImageKey.PROJECTION] * n_projs
        nx_tomo.instrument.detector.x_pixel_size = 1.0
        nx_tomo.instrument.detector.y_pixel_size = 1.0
        nx_tomo.instrument.detector.distance = 2.3
        nx_tomo.energy = 19.2
        nx_tomo.instrument.detector.data = frame

        file_path = os.path.join(raw_data_dir, f"nxtomo_{i_frame}.nx")
        entry = f"entry000{i_frame}"
        nx_tomo.save(file_path=file_path, data_path=entry)
        scans.append(NXtomoScan(scan=file_path, entry=entry))

    stitched_nx_tomo = []
    for s in slices:
        output_file_path = os.path.join(output_dir, "stitched_section.nx")
        output_data_path = f"stitched_{s}"
        z_stich_config = PreProcessedZStitchingConfiguration(
            axis_0_pos_px=z_positions,
            axis_1_pos_px=None,
            axis_2_pos_px=(0, 0),
            axis_0_pos_mm=None,
            axis_1_pos_mm=None,
            axis_2_pos_mm=None,
            axis_0_params={},
            axis_1_params={},
            axis_2_params={},
            stitching_strategy=OverlapStitchingStrategy.CLOSEST,
            overwrite_results=True,
            input_scans=scans,
            output_file_path=output_file_path,
            output_data_path=output_data_path,
            output_nexus_version=None,
            slices=s,
            slurm_config=None,
            slice_for_cross_correlation="middle",
            pixel_size=None,
        )
        stitcher = PreProcessZStitcher(z_stich_config)
        output_identifier = stitcher.stitch()
        assert output_identifier.file_path == output_file_path
        assert output_identifier.data_path == output_data_path

        created_nx_tomo = NXtomo().load(
            file_path=output_identifier.file_path,
            data_path=output_identifier.data_path,
            detector_data_as="as_numpy_array",
        )
        stitched_nx_tomo.append(created_nx_tomo)
    assert len(stitched_nx_tomo) == len(slices)
    final_nx_tomo = NXtomo.concatenate(stitched_nx_tomo)
    assert isinstance(final_nx_tomo.instrument.detector.data, numpy.ndarray)
    final_nx_tomo.save(
        file_path=os.path.join(output_dir, "final_stitched.nx"),
        data_path="entry0000",
    )

    if complete:
        len(final_nx_tomo.instrument.detector.data) == 128
        # test middle
        numpy.testing.assert_array_almost_equal(raw_data[1], final_nx_tomo.instrument.detector.data[1, :, :])
    else:
        len(final_nx_tomo.instrument.detector.data) == 3
        # test middle
        numpy.testing.assert_array_almost_equal(raw_data[49], final_nx_tomo.instrument.detector.data[1, :, :])
    # in the case of first, middle and last frames
    # test first
    numpy.testing.assert_array_almost_equal(raw_data[0], final_nx_tomo.instrument.detector.data[0, :, :])

    # test last
    numpy.testing.assert_array_almost_equal(raw_data[-1], final_nx_tomo.instrument.detector.data[-1, :, :])


_VOL_CLASSES_TO_TEST_FOR_POSTPROC_STITCHING = [HDF5Volume, EDFVolume]
# avoid testing glymur because doesn't handle float
# if has_minimal_openjpeg:
#     _VOL_CLASSES_TO_TEST_FOR_POSTPROC_STITCHING.append(JP2KVolume)
if has_tifffile:
    _VOL_CLASSES_TO_TEST_FOR_POSTPROC_STITCHING.append(TIFFVolume)


@pytest.mark.parametrize("progress", (None, Progress("z-stitching")))
@pytest.mark.parametrize("volume_class", (_VOL_CLASSES_TO_TEST_FOR_POSTPROC_STITCHING))
def test_PostProcessZStitcher(
    tmp_path,
    volume_class,
    progress,
):
    """
    test PreProcessZStitcher class and insure a full stitching can be done automatically.

    :param bool clear_input_volumes_data: if True save the volume then clear volume.data (used to check internal management of loading volumes - used to check behavior with HDF5)
    :param volume_class: class to be used (same class for input and output for now)
    :param axis_0_pos: position of the different TomoObj along axis 0 (Also know as z axis)
    """
    # create some random data.
    raw_volume = build_raw_volume()

    # create folder to save data (and debug)
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    # create a simple case where the volume have 10 voxel of overlap and a height (z) of 30 Voxels, 40 and 30 Voxels
    vol_1_constructor_params = {
        "data": raw_volume[0:30, :, :],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-15.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_2_constructor_params = {
        "data": raw_volume[20:80, :, :],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-50.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_3_constructor_params = {
        "data": raw_volume[60:, :, :],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-90.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    raw_volumes = []
    axis_0_positions = []
    for i_vol, vol_params in enumerate([vol_1_constructor_params, vol_2_constructor_params, vol_3_constructor_params]):
        if volume_class == HDF5Volume:
            vol_params.update(
                {
                    "file_path": os.path.join(raw_data_dir, f"raw_volume_{i_vol}.hdf5"),
                    "data_path": "volume",
                }
            )
        else:
            vol_params.update(
                {
                    "folder": os.path.join(raw_data_dir, f"raw_volume_{i_vol}"),
                }
            )
        axis_0_positions.append(vol_params["metadata"]["processing_options"]["reconstruction"]["position"][0])

        volume = volume_class(**vol_params)
        volume.save()
        raw_volumes.append(volume)

    volume_1, volume_2, volume_3 = raw_volumes

    output_volume = HDF5Volume(
        file_path=os.path.join(output_dir, "stitched_volume.hdf5"),
        data_path="stitched_volume",
    )

    z_stich_config = PostProcessedZStitchingConfiguration(
        stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
        overwrite_results=True,
        input_volumes=(volume_1, volume_2, volume_3),
        output_volume=output_volume,
        slices=None,
        slurm_config=None,
        axis_0_pos_px=axis_0_positions,
        axis_0_pos_mm=None,
        axis_0_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_1_pos_px=None,
        axis_1_pos_mm=None,
        axis_1_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_2_pos_px=None,
        axis_2_pos_mm=None,
        axis_2_params={"img_reg_method": ShiftAlgorithm.NONE},
        slice_for_cross_correlation="middle",
        voxel_size=None,
    )

    stitcher = PostProcessZStitcher(z_stich_config, progress=progress)
    output_identifier = stitcher.stitch()
    assert output_identifier.file_path == output_volume.file_path
    assert output_identifier.data_path == output_volume.data_path

    output_volume.data = None
    output_volume.metadata = None
    output_volume.load_data(store=True)
    output_volume.load_metadata(store=True)

    assert raw_volume.shape == output_volume.data.shape

    numpy.testing.assert_array_almost_equal(raw_volume, output_volume.data)

    metadata = output_volume.metadata
    assert metadata["program"] == "nabu-stitching"
    assert "configuration" in metadata
    assert output_volume.position[0] == -60.0
    assert output_volume.pixel_size == (1.0, 1.0, 1.0)


slices_to_test_post = (
    {
        "slices": (None,),
        "complete": True,
    },
    {
        "slices": (("first",), ("middle",), ("last",)),
        "complete": False,
    },
    {
        "slices": ((0, 1, 2), slice(3, -1, 1)),
        "complete": True,
    },
)


@pytest.mark.parametrize("flip_ud", (True, False))
@pytest.mark.parametrize("configuration_dist", slices_to_test_post)
def test_DistributePostProcessZStitcher(tmp_path, configuration_dist, flip_ud):
    # create some random data.
    slices = configuration_dist["slices"]
    complete = configuration_dist["complete"]

    raw_volume = numpy.ones((80, 40, 120), dtype=numpy.float16)
    raw_volume[:, 0, :] = (
        PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float16)[30:110, :] * 80 * 40 * 120
    )
    raw_volume[:, 8, :] = (
        PhantomGenerator.get2DPhantomSheppLogan(n=120).astype(numpy.float16)[30:110, :] * 80 * 40 * 120 + 2
    )
    raw_volume[12] = 1.0
    raw_volume[:, 23] = 1.2
    # create folder to save data (and debug)
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    def flip_input_data(data):
        if flip_ud:
            data = numpy.flipud(data)
        return data

    volume_1 = HDF5Volume(
        file_path=os.path.join(raw_data_dir, "volume_1.hdf5"),
        data_path="volume",
        data=flip_input_data(raw_volume[-60:, :, :]),
        metadata={
            "processing_options": {
                "reconstruction": {
                    "position": (-30.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    )
    volume_1.save()

    volume_2 = HDF5Volume(
        file_path=os.path.join(raw_data_dir, "volume_2.hdf5"),
        data_path="volume",
        data=flip_input_data(raw_volume[:60, :, :]),
        metadata={
            "processing_options": {
                "reconstruction": {
                    "position": (-50.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    )
    volume_2.save()

    reconstructed_sub_volumes = []
    for i_slice, s in enumerate(slices):
        output_volume = HDF5Volume(
            file_path=os.path.join(output_dir, f"stitched_subvolume_{i_slice}.hdf5"),
            data_path="stitched_volume",
        )
        volumes = (volume_2, volume_1)
        z_stich_config = PostProcessedZStitchingConfiguration(
            stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
            axis_0_pos_px=tuple(
                volume.metadata["processing_options"]["reconstruction"]["position"][0] for volume in volumes
            ),
            axis_0_pos_mm=None,
            axis_0_params={},
            axis_1_pos_px=None,
            axis_1_pos_mm=None,
            axis_1_params={},
            axis_2_pos_px=(0, 0),
            axis_2_pos_mm=None,
            axis_2_params={},
            overwrite_results=True,
            input_volumes=volumes,
            output_volume=output_volume,
            slices=s,
            slurm_config=None,
            slice_for_cross_correlation="middle",
            voxel_size=None,
            flip_ud=flip_ud,
        )

        stitcher = PostProcessZStitcher(z_stich_config)
        vol_id = stitcher.stitch()
        reconstructed_sub_volumes.append(TomoscanFactory.create_tomo_object_from_identifier(identifier=vol_id))

    final_vol = HDF5Volume(
        file_path=os.path.join(output_dir, "final_volume"),
        data_path="volume",
    )
    if complete:
        concatenate_volumes(output_volume=final_vol, volumes=tuple(reconstructed_sub_volumes), axis=1)
        final_vol.load_data(store=True)
        with h5py.File("debug.hdf5", mode="w") as h5f:
            h5f["raw_volume"] = raw_volume
            h5f["final_vol"] = final_vol.data
            h5f["volume1"] = volume_1.data
            h5f["volume2"] = volume_2.data
        numpy.testing.assert_almost_equal(
            raw_volume,
            final_vol.data,
        )


def test_get_overlap_areas():
    """test get_overlap_areas function"""
    f_upper = numpy.linspace(7, 15, num=9, endpoint=True)
    f_lower = numpy.linspace(0, 12, num=13, endpoint=True)

    o_1, o_2 = ZStitcher.get_overlap_areas(
        upper_frame=f_upper,
        lower_frame=f_lower,
        upper_frame_key_line=3,
        lower_frame_key_line=10,
        overlap_size=4,
        stitching_axis=0,
    )

    numpy.testing.assert_array_equal(o_1, o_2)
    numpy.testing.assert_array_equal(o_1, numpy.linspace(8, 11, num=4, endpoint=True))


def test_frame_flip(tmp_path):
    """check it with some NXtomo fliped"""
    ref_frame_width = 280
    n_proj = 10
    raw_frame_width = 100
    ref_frame = PhantomGenerator.get2DPhantomSheppLogan(n=ref_frame_width).astype(numpy.float32) * 256.0
    # create raw data
    frame_0_shift = (0, 0)
    frame_1_shift = (-90, 0)
    frame_2_shift = (-180, 0)

    frame_0 = scipy_shift(ref_frame, shift=frame_0_shift)[:raw_frame_width]
    frame_1 = scipy_shift(ref_frame, shift=frame_1_shift)[:raw_frame_width]
    frame_2 = scipy_shift(ref_frame, shift=frame_2_shift)[:raw_frame_width]
    frames = frame_0, frame_1, frame_2

    x_flips = [False, True, True]
    y_flips = [False, False, True]

    def apply_flip(args):
        frame, flip_x, flip_y = args
        if flip_x:
            frame = numpy.fliplr(frame)
        if flip_y:
            frame = numpy.flipud(frame)
        return frame

    frames = map(apply_flip, zip(frames, x_flips, y_flips))

    # create a Nxtomo for each of those raw data
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    z_position = (90, 0, -90)

    scans = []
    for (i_frame, frame), z_pos, x_flip, y_flip in zip(enumerate(frames), z_position, x_flips, y_flips):
        nx_tomo = NXtomo()
        nx_tomo.sample.z_translation = [z_pos] * n_proj
        nx_tomo.sample.rotation_angle = numpy.linspace(0, 180, num=n_proj, endpoint=False)
        nx_tomo.instrument.detector.image_key_control = [ImageKey.PROJECTION] * n_proj
        nx_tomo.instrument.detector.x_pixel_size = 1.0
        nx_tomo.instrument.detector.y_pixel_size = 1.0
        nx_tomo.instrument.detector.distance = 2.3
        if x_flip:
            nx_tomo.instrument.detector.transformations.add_transformation(LRDetTransformation())
        if y_flip:
            nx_tomo.instrument.detector.transformations.add_transformation(UDDetTransformation())
        nx_tomo.energy = 19.2
        nx_tomo.instrument.detector.data = numpy.asarray([frame] * n_proj)

        file_path = os.path.join(raw_data_dir, f"nxtomo_{i_frame}.nx")
        entry = f"entry000{i_frame}"
        nx_tomo.save(file_path=file_path, data_path=entry)
        scans.append(NXtomoScan(scan=file_path, entry=entry))

    output_file_path = os.path.join(output_dir, "stitched.nx")
    output_data_path = "stitched"
    assert len(scans) == 3
    z_stich_config = PreProcessedZStitchingConfiguration(
        axis_0_pos_px=(0, -90, -180),
        axis_1_pos_px=None,
        axis_2_pos_px=(0, 0, 0),
        axis_0_pos_mm=None,
        axis_1_pos_mm=None,
        axis_2_pos_mm=None,
        axis_0_params={},
        axis_1_params={},
        axis_2_params={},
        stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
        overwrite_results=True,
        input_scans=scans,
        output_file_path=output_file_path,
        output_data_path=output_data_path,
        output_nexus_version=None,
        slices=None,
        slurm_config=None,
        slice_for_cross_correlation="middle",
        pixel_size=None,
    )
    stitcher = PreProcessZStitcher(z_stich_config)
    output_identifier = stitcher.stitch()
    assert output_identifier.file_path == output_file_path
    assert output_identifier.data_path == output_data_path

    created_nx_tomo = NXtomo().load(
        file_path=output_identifier.file_path,
        data_path=output_identifier.data_path,
        detector_data_as="as_numpy_array",
    )

    assert created_nx_tomo.instrument.detector.data.ndim == 3
    # insure flipping has been taking into account
    numpy.testing.assert_array_almost_equal(ref_frame, created_nx_tomo.instrument.detector.data[0, :ref_frame_width, :])

    assert len(created_nx_tomo.instrument.detector.transformations) == 0


@pytest.mark.parametrize("alignment_axis_2", ("left", "right", "center"))
def test_vol_z_stitching_with_alignment_axis_2(tmp_path, alignment_axis_2):
    """
    test z volume stitching with different width (and so that requires image alignment over axis 2)
    """
    # create some random data.
    raw_volume = build_raw_volume()
    # create folder to save data (and debug)
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    # create a simple case where the volume have 10 voxel of overlap and a height (z) of 30 Voxels, 40 and 30 Voxels
    vol_1_constructor_params = {
        "data": raw_volume[0:30, :, 4:-4],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-15.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_2_constructor_params = {
        "data": raw_volume[20:80, :, :],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-50.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_3_constructor_params = {
        "data": raw_volume[60:, :, 10:-10],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-90.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    raw_volumes = []
    axis_0_positions = []
    for i_vol, vol_params in enumerate([vol_1_constructor_params, vol_2_constructor_params, vol_3_constructor_params]):
        vol_params.update(
            {
                "file_path": os.path.join(raw_data_dir, f"raw_volume_{i_vol}.hdf5"),
                "data_path": "volume",
            }
        )
        axis_0_positions.append(vol_params["metadata"]["processing_options"]["reconstruction"]["position"][0])
        volume = HDF5Volume(**vol_params)
        volume.save()
        raw_volumes.append(volume)

    volume_1, volume_2, volume_3 = raw_volumes

    output_volume = HDF5Volume(
        file_path=os.path.join(output_dir, "stitched_volume.hdf5"),
        data_path="stitched_volume",
    )

    z_stich_config = PostProcessedZStitchingConfiguration(
        stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
        overwrite_results=True,
        input_volumes=(volume_1, volume_2, volume_3),
        output_volume=output_volume,
        slices=None,
        slurm_config=None,
        axis_0_pos_px=axis_0_positions,
        axis_0_pos_mm=None,
        axis_0_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_1_pos_px=None,
        axis_1_pos_mm=None,
        axis_1_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_2_pos_px=None,
        axis_2_pos_mm=None,
        axis_2_params={"img_reg_method": ShiftAlgorithm.NONE},
        slice_for_cross_correlation="middle",
        voxel_size=None,
        alignment_axis_2=AlignmentAxis2.from_value(alignment_axis_2),
    )

    stitcher = PostProcessZStitcher(z_stich_config, progress=None)
    output_identifier = stitcher.stitch()
    assert output_identifier.file_path == output_volume.file_path
    assert output_identifier.data_path == output_volume.data_path

    output_volume.load_data(store=True)
    output_volume.load_metadata(store=True)

    assert output_volume.data.shape == (120, 4, 120)

    import h5py

    with h5py.File("input.h5", mode="w") as h5f:
        h5f["data"] = raw_volume

    with h5py.File("output.h5", mode="w") as h5f:
        h5f["data"] = output_volume.data

    if alignment_axis_2 == "center":
        numpy.testing.assert_array_almost_equal(raw_volume[:, :, 10:-10], output_volume.data[:, :, 10:-10])
    elif alignment_axis_2 == "left":
        numpy.testing.assert_array_almost_equal(raw_volume[:, :, :-20], output_volume.data[:, :, :-20])
    elif alignment_axis_2 == "right":
        numpy.testing.assert_array_almost_equal(raw_volume[:, :, 20:], output_volume.data[:, :, 20:])


@pytest.mark.parametrize("alignment_axis_1", ("front", "center", "back"))
def test_vol_z_stitching_with_alignment_axis_1(tmp_path, alignment_axis_1):
    """
    test z volume stitching with different number of frames (and so that requires image alignment over axis 0)
    """
    # create some random data.
    raw_volume = build_raw_volume()

    # create folder to save data (and debug)
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    # create a simple case where the volume have 10 voxel of overlap and a height (z) of 30 Voxels, 40 and 30 Voxels
    vol_1_constructor_params = {
        "data": raw_volume[
            0:30,
            1:3,
        ],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-15.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_2_constructor_params = {
        "data": raw_volume[20:80, :, :],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-50.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_3_constructor_params = {
        "data": raw_volume[
            60:,
            1:3,
        ],
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-90.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    raw_volumes = []
    axis_0_positions = []
    for i_vol, vol_params in enumerate([vol_1_constructor_params, vol_2_constructor_params, vol_3_constructor_params]):
        vol_params.update(
            {
                "file_path": os.path.join(raw_data_dir, f"raw_volume_{i_vol}.hdf5"),
                "data_path": "volume",
            }
        )
        axis_0_positions.append(vol_params["metadata"]["processing_options"]["reconstruction"]["position"][0])
        volume = HDF5Volume(**vol_params)
        volume.save()
        raw_volumes.append(volume)

    volume_1, volume_2, volume_3 = raw_volumes

    output_volume = HDF5Volume(
        file_path=os.path.join(output_dir, "stitched_volume.hdf5"),
        data_path="stitched_volume",
    )

    z_stich_config = PostProcessedZStitchingConfiguration(
        stitching_strategy=OverlapStitchingStrategy.LINEAR_WEIGHTS,
        overwrite_results=True,
        input_volumes=(volume_1, volume_2, volume_3),
        output_volume=output_volume,
        slices=None,
        slurm_config=None,
        axis_0_pos_px=axis_0_positions,
        axis_0_pos_mm=None,
        axis_0_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_1_pos_px=None,
        axis_1_pos_mm=None,
        axis_1_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_2_pos_px=None,
        axis_2_pos_mm=None,
        axis_2_params={"img_reg_method": ShiftAlgorithm.NONE},
        slice_for_cross_correlation="middle",
        voxel_size=None,
        alignment_axis_1=AlignmentAxis1.from_value(alignment_axis_1),
    )

    stitcher = PostProcessZStitcher(z_stich_config, progress=None)
    output_identifier = stitcher.stitch()
    assert output_identifier.file_path == output_volume.file_path
    assert output_identifier.data_path == output_volume.data_path

    output_volume.load_data(store=True)
    output_volume.load_metadata(store=True)

    assert output_volume.data.shape == (120, 4, 120)

    if alignment_axis_1 == "middle":
        numpy.testing.assert_array_almost_equal(raw_volume[:, 10:-10, :], output_volume.data[:, 10:-10, :])
    elif alignment_axis_1 == "front":
        numpy.testing.assert_array_almost_equal(raw_volume[:, :-20, :], output_volume.data[:, :-20, :])
    elif alignment_axis_1 == "middle":
        numpy.testing.assert_array_almost_equal(raw_volume[:, 20:, :], output_volume.data[:, 20:, :])


def test_normalization_by_sample(tmp_path):
    """
    simple test of a volume stitching.
    Raw volumes have 'extra' values (+2, +5, +9) that must be removed at the end thanks to the normalization
    """
    from copy import deepcopy

    raw_volume = build_raw_volume()
    # create folder to save data (and debug)
    raw_data_dir = tmp_path / "raw_data"
    raw_data_dir.mkdir()
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()

    # create a simple case where the volume have 10 voxel of overlap and a height (z) of 30 Voxels, 40 and 30 Voxels
    vol_1_constructor_params = {
        "data": raw_volume[0:30, :, :] + 3,
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-15.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_2_constructor_params = {
        "data": raw_volume[20:80, :, :] + 5,
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-50.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    vol_3_constructor_params = {
        "data": raw_volume[60:, :, :] + 12,
        "metadata": {
            "processing_options": {
                "reconstruction": {
                    "position": (-90.0, 0.0, 0.0),
                    "voxel_size_cm": (100.0, 100.0, 100.0),
                }
            },
        },
    }

    raw_volumes = []
    axis_0_positions = []
    for i_vol, vol_params in enumerate([vol_1_constructor_params, vol_2_constructor_params, vol_3_constructor_params]):
        vol_params.update(
            {
                "file_path": os.path.join(raw_data_dir, f"raw_volume_{i_vol}.hdf5"),
                "data_path": "volume",
            }
        )

        axis_0_positions.append(vol_params["metadata"]["processing_options"]["reconstruction"]["position"][0])

        volume = HDF5Volume(**vol_params)
        volume.save()
        raw_volumes.append(volume)

    volume_1, volume_2, volume_3 = raw_volumes

    output_volume = HDF5Volume(
        file_path=os.path.join(output_dir, "stitched_volume.hdf5"),
        data_path="stitched_volume",
    )

    normalization_by_sample = NormalizationBySample()
    normalization_by_sample.set_is_active(True)
    normalization_by_sample.width = 1
    normalization_by_sample.margin = 0
    normalization_by_sample.side = "left"
    normalization_by_sample.method = "median"

    z_stich_config = PostProcessedZStitchingConfiguration(
        stitching_strategy=OverlapStitchingStrategy.CLOSEST,
        overwrite_results=True,
        input_volumes=(volume_1, volume_2, volume_3),
        output_volume=output_volume,
        slices=None,
        slurm_config=None,
        axis_0_pos_px=axis_0_positions,
        axis_0_pos_mm=None,
        axis_0_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_1_pos_px=None,
        axis_1_pos_mm=None,
        axis_1_params={"img_reg_method": ShiftAlgorithm.NONE},
        axis_2_pos_px=None,
        axis_2_pos_mm=None,
        axis_2_params={"img_reg_method": ShiftAlgorithm.NONE},
        slice_for_cross_correlation="middle",
        voxel_size=None,
        normalization_by_sample=normalization_by_sample,
    )

    stitcher = PostProcessZStitcher(z_stich_config, progress=None)
    output_identifier = stitcher.stitch()

    assert output_identifier.file_path == output_volume.file_path
    assert output_identifier.data_path == output_volume.data_path

    output_volume.data = None
    output_volume.metadata = None
    output_volume.load_data(store=True)
    output_volume.load_metadata(store=True)

    assert raw_volume.shape == output_volume.data.shape

    numpy.testing.assert_array_almost_equal(raw_volume, output_volume.data)

    metadata = output_volume.metadata
    assert metadata["program"] == "nabu-stitching"
    assert "configuration" in metadata
    assert output_volume.position[0] == -60.0
    assert output_volume.pixel_size == (1.0, 1.0, 1.0)
