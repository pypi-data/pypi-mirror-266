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
__date__ = "10/05/2022"


import os
from copy import copy
from datetime import datetime
from typing import Optional, Union, Iterable
import numpy
from math import ceil
from contextlib import AbstractContextManager
import h5py
import logging
from scipy.ndimage import shift as shift_scipy
from functools import lru_cache as cache

from silx.io.utils import get_data
from silx.io.url import DataUrl
from silx.io.dictdump import dicttonx

from nxtomo.nxobject.nxdetector import ImageKey
from nxtomo.nxobject.nxtransformations import NXtransformations
from nxtomo.paths.nxtomo import get_paths as _get_nexus_paths
from nxtomo.utils.transformation import build_matrix, LRDetTransformation, UDDetTransformation

from tomoscan.io import HDF5File
from tomoscan.esrf.scan.utils import cwd_context
from tomoscan.identifier import BaseIdentifier
from tomoscan.esrf import NXtomoScan, EDFTomoScan
from tomoscan.volumebase import VolumeBase
from tomoscan.esrf.volume import HDF5Volume
from tomoscan.serie import Serie
from tomoscan.factory import Factory as TomoscanFactory
from tomoscan.utils.volume import concatenate as concatenate_volumes
from tomoscan.esrf.scan.utils import (
    get_compacted_dataslices,
)  # this version has a 'return_url_set' needed here. At one point they should be merged together
from pyunitsystem.metricsystem import MetricSystem

from nxtomo.application.nxtomo import NXtomo
from silx.io.dictdump import dicttonx

from nabu.io.utils import DatasetReader
from nabu.stitching.frame_composition import ZFrameComposition
from nabu.stitching.utils import find_projections_relative_shifts, find_volumes_relative_shifts, ShiftAlgorithm
from nabu.stitching.config import (
    CROSS_CORRELATION_SLICE_FIELD,
    PreProcessedZStitchingConfiguration,
    PostProcessedZStitchingConfiguration,
    ZStitchingConfiguration,
    KEY_IMG_REG_METHOD,
    KEY_RESCALE_MIN_PERCENTILES,
    KEY_RESCALE_MAX_PERCENTILES,
    KEY_THRESHOLD_FREQUENCY,
)
from nabu.stitching.alignment import align_horizontally, AlignmentAxis1
from nabu.utils import Progress
from nabu import version as nabu_version
from nabu.io.writer import get_datetime
from .overlap import (
    ZStichOverlapKernel,
    check_overlaps,
)
from .. import version as nabu_version
from nabu.io.writer import get_datetime
from nabu.misc.utils import rescale_data
from nabu.stitching.alignment import PaddedRawData
from nabu.stitching.sample_normalization import normalize_frame as normalize_frame_by_sample

_logger = logging.getLogger(__name__)


def z_stitching(configuration: ZStitchingConfiguration, progress=None) -> BaseIdentifier:
    """
    Apply stitching from provided configuration.
    Return a DataUrl with the created NXtomo or Volume
    """
    if isinstance(configuration, PreProcessedZStitchingConfiguration):
        stitcher = PreProcessZStitcher(configuration=configuration, progress=progress)
    elif isinstance(configuration, PostProcessedZStitchingConfiguration):
        stitcher = PostProcessZStitcher(configuration=configuration, progress=progress)
    else:
        raise TypeError(
            f"configuration is expected to be in {(PreProcessedZStitchingConfiguration, PostProcessedZStitchingConfiguration)}. {type(configuration)} provided"
        )
    return stitcher.stitch()


class ZStitcher:
    @staticmethod
    def param_is_auto(param):
        return param in ("auto", ("auto",))

    def __init__(self, configuration, progress: Progress = None) -> None:
        if not isinstance(configuration, ZStitchingConfiguration):
            raise TypeError

        # flag to check if the serie has been ordered yet or not
        self._configuration = copy(configuration)
        # copy configuration because we will edit it
        self._frame_composition = None
        self._progress = progress
        self._overlap_kernels = []
        # kernels to create the stitching on overlaps.

        self._axis_0_rel_shifts = []
        self._axis_2_rel_shifts = []
        # shift between upper and lower frames

        self._stitching_width = None
        # stitching width: larger volume width. Other volume will be pad

        # z serie must be defined from daughter class
        assert hasattr(self, "_z_serie")

        def shifts_is_scalar(shifts):
            return isinstance(shifts, ShiftAlgorithm) or numpy.isscalar(shifts)

        # 'expend' shift algorithm
        if shifts_is_scalar(self.configuration.axis_0_pos_px):
            self.configuration.axis_0_pos_px = [
                self.configuration.axis_0_pos_px,
            ] * (len(self.z_serie) - 1)
        if shifts_is_scalar(self.configuration.axis_1_pos_px):
            self.configuration.axis_1_pos_px = [
                self.configuration.axis_1_pos_px,
            ] * (len(self.z_serie) - 1)
        if shifts_is_scalar(self.configuration.axis_2_pos_px):
            self.configuration.axis_2_pos_px = [
                self.configuration.axis_2_pos_px,
            ] * (len(self.z_serie) - 1)
        if numpy.isscalar(self.configuration.axis_0_params):
            self.configuration.axis_0_params = [
                self.configuration.axis_0_params,
            ] * (len(self.z_serie) - 1)
        if numpy.isscalar(self.configuration.axis_1_params):
            self.configuration.axis_1_params = [
                self.configuration.axis_1_params,
            ] * (len(self.z_serie) - 1)
        if numpy.isscalar(self.configuration.axis_2_params):
            self.configuration.axis_2_params = [
                self.configuration.axis_2_params,
            ] * (len(self.z_serie) - 1)

    @property
    def frame_composition(self):
        return self._frame_composition

    def get_final_axis_positions_in_px(self) -> dict:
        """
        :return: dict with tomo object identifier (str) as key and a tuple of position in pixel (axis_0_pos, axis_1_pos, axis_2_pos)
        :rtype: dict
        """
        final_shifts_axis_0 = [
            0,
        ]
        final_shifts_axis_0.extend(self._axis_0_rel_shifts)
        final_shifts_axis_0 = numpy.array(final_shifts_axis_0)

        final_shifts_axis_2 = [
            0,
        ]
        final_shifts_axis_2.extend(self._axis_2_rel_shifts)
        final_shifts_axis_2 = numpy.array(final_shifts_axis_2)

        estimated_shifts_axis_0 = self._axis_0_estimated_shifts.copy()
        estimated_shifts_axis_0.insert(0, 0)

        final_pos = {}
        previous_shift = 0
        for tomo_obj, pos_axis_0, pos_axis_2, final_shift_axis_0, estimated_shift_axis_0, final_shift_axis_2 in zip(
            self.z_serie,
            self.configuration.axis_0_pos_px,
            self.configuration.axis_2_pos_px,
            estimated_shifts_axis_0,
            final_shifts_axis_0,
            final_shifts_axis_2,
        ):
            # warning estimated_shift is the estimatation from the overlap. So playes no role here
            final_pos[tomo_obj.get_identifier().to_str()] = (
                pos_axis_0 - (final_shift_axis_0 - estimated_shift_axis_0) + previous_shift,
                None,  # axis 1 is not handled for now
                pos_axis_2 + final_shift_axis_2,
            )
            previous_shift += final_shift_axis_0 - estimated_shift_axis_0
        return final_pos

    def from_abs_pos_to_rel_pos(self, abs_position: tuple):
        """
        return relative position from on object to the other but in relative this time
        :param tuple abs_position: tuple containing the absolute positions
        :return: len(abs_position) - 1 relative position
        :rtype: tuple
        """
        return tuple([pos_obj_b - pos_obj_a for (pos_obj_a, pos_obj_b) in zip(abs_position[:-1], abs_position[1:])])

    def from_rel_pos_to_abs_pos(self, rel_positions: tuple, init_pos: int):
        """
        return absolute positions from a tuple of relative position and an initial position
        :param tuple rel_positions: tuple containing the absolute positions
        :return: len(rel_positions) + 1 relative position
        :rtype: tuple
        """
        abs_pos = [
            init_pos,
        ]
        for rel_pos in rel_positions:
            abs_pos.append(abs_pos[-1] + rel_pos)
        return abs_pos

    def stitch(self, store_composition: bool = True) -> BaseIdentifier:
        """
        Apply expected stitch from configuration and return the DataUrl of the object created

        :param bool store_composition: if True then store the composition used for stitching in frame_composition.
                                       So it can be reused by third part (like tomwer) to display composition made
        """
        raise NotImplementedError("base class")

    def settle_flips(self):
        """
        User can provide some information on existing flips at frame level.
        The goal of this step is to get one flip_lr and on flip_ud value per scan or volume
        """
        if numpy.isscalar(self.configuration.flip_lr):
            self.configuration.flip_lr = tuple([self.configuration.flip_lr] * len(self.z_serie))
        else:
            if not len(self.configuration.flip_lr) == len(self.z_serie):
                raise ValueError("flip_lr expects a scalar value or one value per element to stitch")
            self.configuration.flip_lr = tuple(self.configuration.flip_lr)
            for elmt in self.configuration.flip_lr:
                if not isinstance(elmt, bool):
                    raise TypeError

        if numpy.isscalar(self.configuration.flip_ud):
            self.configuration.flip_ud = tuple([self.configuration.flip_ud] * len(self.z_serie))
        else:
            if not len(self.configuration.flip_ud) == len(self.z_serie):
                raise ValueError("flip_ud expects a scalar value or one value per element to stitch")
            self.configuration.flip_ud = tuple(self.configuration.flip_ud)
            for elmt in self.configuration.flip_ud:
                if not isinstance(elmt, bool):
                    raise TypeError

    def _compute_shifts(self):
        """
        after this stage the final shifts must be determine
        """
        raise NotImplementedError("base class")

    def _createOverlapKernels(self):
        """
        after this stage the overlap kernels must be created and with the final overlap size
        """
        if self._axis_0_rel_shifts is None or len(self._axis_0_rel_shifts) == 0:
            raise RuntimeError(
                "axis 0 shifts have not been defined yet. Please define them before calling this function"
            )

        overlap_size = self.configuration.axis_0_params.get("overlap_size", None)
        if overlap_size in (None, "None", ""):
            overlap_size = -1
        else:
            overlap_size = int(overlap_size)

        self._stitching_width = max([get_obj_width(obj) for obj in self.z_serie])

        for axis_0_shift in self._axis_0_rel_shifts:
            if overlap_size == -1:
                height = abs(axis_0_shift)
            else:
                height = overlap_size

            self._overlap_kernels.append(
                ZStichOverlapKernel(
                    frame_width=self._stitching_width,
                    stitching_strategy=self.configuration.stitching_strategy,
                    overlap_size=height,
                    extra_params=self.configuration.stitching_kernels_extra_params,
                )
            )

    @property
    def z_serie(self) -> Serie:
        return self._z_serie

    @property
    def configuration(self) -> ZStitchingConfiguration:
        return self._configuration

    @property
    def progress(self) -> Optional[Progress]:
        return self._progress

    @staticmethod
    def get_overlap_areas(
        upper_frame: numpy.ndarray,
        lower_frame: numpy.ndarray,
        upper_frame_key_line: int,
        lower_frame_key_line: int,
        overlap_size: int,
        stitching_axis: int,
    ):
        """
        return the requested area from lower_frame and upper_frame.

        Lower_frame contains at the end of it the 'real overlap' with the upper_frame.
        Upper_frame contains the 'real overlap' at the end of it.

        For some reason the user can ask the stitching height to be smaller than the `real overlap`.

        Here are some drawing to have a better of view of those regions:

        .. image:: images/stitching/z_stitch_real_overlap.png
            :width: 600

        .. image:: z_stitch_stitch_height.png
            :width: 600
        """
        assert stitching_axis in (0, 1, 2)
        for pf, pn in zip((lower_frame_key_line, upper_frame_key_line), ("lower_frame", "upper_frame")):
            if not isinstance(pf, (int, numpy.number)):
                raise TypeError(f"{pn} is expected to be a number. {type(pf)} provided")
        assert overlap_size >= 0

        lf_start = ceil(lower_frame_key_line - overlap_size / 2)
        lf_end = ceil(lower_frame_key_line + overlap_size / 2)
        uf_start = ceil(upper_frame_key_line - overlap_size / 2)
        uf_end = ceil(upper_frame_key_line + overlap_size / 2)

        lf_start, lf_end = min(lf_start, lf_end), max(lf_start, lf_end)
        uf_start, uf_end = min(uf_start, uf_end), max(uf_start, uf_end)
        if lf_start < 0 or uf_start < 0:
            raise ValueError(
                f"requested overlap ({overlap_size}) is incoherent with key line positions ({lower_frame_key_line}, {upper_frame_key_line}) - expected to be smaller."
            )
        overlap_upper = upper_frame[uf_start:uf_end]
        overlap_lower = lower_frame[lf_start:lf_end]
        if not overlap_upper.shape == overlap_lower.shape:
            # maybe in the future: try to reduce one according to the other ????
            raise RuntimeError(
                f"lower and upper frame have different overlap size ({overlap_upper.shape} vs {overlap_lower.shape})"
            )
        return overlap_upper, overlap_lower

    @staticmethod
    def _data_bunch_iterator(slices, bunch_size):
        """util to get indices by bunch until we reach n_frames"""
        if isinstance(slices, slice):
            # note: slice step is handled at a different level
            start = end = slices.start

            while True:
                start, end = end, min((end + bunch_size), slices.stop)
                yield (start, end)
                if end >= slices.stop:
                    break
        # in the case of non-contiguous frames
        elif isinstance(slices, Iterable):
            for s in slices:
                yield (s, s + 1)
        else:
            raise TypeError(f"slices is provided as {type(slices)}. When Iterable or slice is expected")

    def rescale_frames(self, frames: tuple):
        """
        rescale_frames if requested by the configuration
        """
        _logger.info("apply rescale frames")

        def cast_percentile(percentile) -> int:
            if isinstance(percentile, str):
                percentile.replace(" ", "").rstrip("%")
            return int(percentile)

        rescale_min_percentile = cast_percentile(self.configuration.rescale_params.get(KEY_RESCALE_MIN_PERCENTILES, 0))
        rescale_max_percentile = cast_percentile(
            self.configuration.rescale_params.get(KEY_RESCALE_MAX_PERCENTILES, 100)
        )

        new_min = numpy.percentile(frames[0], rescale_min_percentile)
        new_max = numpy.percentile(frames[0], rescale_max_percentile)

        def rescale(data):
            # FIXME: takes time because browse several time the dataset, twice for percentiles and twices to get min and max when calling rescale_data...
            data_min = numpy.percentile(data, rescale_min_percentile)
            data_max = numpy.percentile(data, rescale_max_percentile)
            return rescale_data(data, new_min=new_min, new_max=new_max, data_min=data_min, data_max=data_max)

        return tuple([rescale(data) for data in frames])

    def normalize_frame_by_sample(self, frames: tuple):
        """
        normalize frame from a sample picked on the left or the right
        """
        _logger.info("apply normalization by a sample")
        return tuple(
            [
                normalize_frame_by_sample(
                    frame=frame,
                    side=self.configuration.normalization_by_sample.side,
                    method=self.configuration.normalization_by_sample.method,
                    margin_before_sample=self.configuration.normalization_by_sample.margin,
                    sample_width=self.configuration.normalization_by_sample.width,
                )
                for frame in frames
            ]
        )

    @staticmethod
    def stitch_frames(
        frames: Union[tuple, numpy.ndarray],
        x_relative_shifts: tuple,
        y_relative_shifts: tuple,
        output_dtype: numpy.ndarray,
        stitching_axis: int,
        overlap_kernels: tuple,
        output_dataset: Optional[Union[h5py.Dataset, numpy.ndarray]] = None,
        dump_frame_fct=None,
        check_inputs=True,
        shift_mode="nearest",
        i_frame=None,
        return_composition_cls=False,
        alignment="center",
        pad_mode="constant",
        new_width: Optional[int] = None,
    ) -> numpy.ndarray:
        """
        shift frames according to provided `shifts` (as y, x tuples) then stitch all the shifted frames together and
        save them to output_dataset.

        :param tuple frames: element must be a DataUrl or a 2D numpy array
        """
        if check_inputs:
            if len(frames) < 2:
                raise ValueError(f"Not enought frames provided for stitching ({len(frames)} provided)")
            if len(frames) != len(x_relative_shifts) + 1:
                raise ValueError(
                    f"Incoherent number of shift provided ({len(x_relative_shifts)}) compare to number of frame ({len(frames)}). len(frames) - 1 expected"
                )
            if len(x_relative_shifts) != len(overlap_kernels):
                raise ValueError(
                    f"expect to have the same number of x_relative_shifts ({len(x_relative_shifts)}) and y_overlap ({len(overlap_kernels)})"
                )
            if len(y_relative_shifts) != len(overlap_kernels):
                raise ValueError(
                    f"expect to have the same number of y_relative_shifts ({len(y_relative_shifts)}) and y_overlap ({len(overlap_kernels)})"
                )

            relative_positions = [(0, 0)]
            for y_rel_pos, x_rel_pos in zip(y_relative_shifts, x_relative_shifts):
                relative_positions.append(
                    (
                        y_rel_pos + relative_positions[-1][0],
                        x_rel_pos + relative_positions[-1][1],
                    )
                )
            check_overlaps(
                frames=tuple(frames),
                positions=tuple(relative_positions),
                axis=0,
                raise_error=False,
            )

        def check_frame_is_2d(frame):
            if frame.ndim != 2:
                raise ValueError(f"2D frame expected when {frame.ndim}D provided")

        # step_0 load data if from url
        data = []
        for frame in frames:
            if isinstance(frame, DataUrl):
                data_frame = get_data(frame)
                if check_inputs:
                    check_frame_is_2d(data_frame)
                data.append(data_frame)
            elif isinstance(frame, numpy.ndarray):
                if check_inputs:
                    check_frame_is_2d(frame)
                data.append(frame)
            else:
                raise TypeError(f"frames are expected to be DataUrl or 2D numpy array. Not {type(frame)}")

        # step 1: shift each frames (except the first one)
        x_shifted_data = [data[0]]
        for frame, x_relative_shift in zip(data[1:], x_relative_shifts):
            # note: for now we only shift data in x. the y shift is handled in the FrameComposition
            x_relative_shift = numpy.asarray(x_relative_shift).astype(numpy.int8)
            if x_relative_shift == 0:
                shifted_frame = frame
            else:
                # TO speed up: should use the Fourier transform
                shifted_frame = shift_scipy(
                    frame,
                    mode=shift_mode,
                    shift=[0, -x_relative_shift],
                    order=1,
                )
            x_shifted_data.append(shifted_frame)

        # step 2: create stitched frame
        res = stitch_vertically_raw_frames(
            frames=x_shifted_data,
            key_lines=(
                [
                    (int(frame.shape[stitching_axis] - abs(y_relative_shift / 2)), int(abs(y_relative_shift / 2)))
                    for y_relative_shift, frame in zip(y_relative_shifts, frames)
                ]
            ),
            overlap_kernels=overlap_kernels,
            check_inputs=check_inputs,
            output_dtype=output_dtype,
            return_composition_cls=return_composition_cls,
            alignment=alignment,
            pad_mode=pad_mode,
            new_width=new_width,
        )
        if return_composition_cls:
            stitched_frame, _ = res
        else:
            stitched_frame = res

        # step 3: dump stitched frame
        if output_dataset is not None and i_frame is not None:
            dump_frame_fct(
                output_dataset=output_dataset,
                index=i_frame,
                stitched_frame=stitched_frame,
            )
        return res

    @staticmethod
    @cache(maxsize=None)
    def _get_UD_flip_matrix():
        return UDDetTransformation().as_matrix()

    @staticmethod
    @cache(maxsize=None)
    def _get_LR_flip_matrix():
        return LRDetTransformation().as_matrix()

    @staticmethod
    @cache(maxsize=None)
    def _get_UD_AND_LR_flip_matrix():
        return numpy.matmul(
            ZStitcher._get_UD_flip_matrix(),
            ZStitcher._get_LR_flip_matrix(),
        )


class PreProcessZStitcher(ZStitcher):
    def __init__(self, configuration, progress=None) -> None:
        # z serie must be defined first
        self._z_serie = Serie("z-serie", iterable=configuration.input_scans, use_identifiers=False)
        self._reading_orders = []
        self._x_flips = []
        self._y_flips = []
        # some scan can have been taken in the opposite order (so must be read on the opposite order one from the other)
        self._axis_0_estimated_shifts = None
        super().__init__(configuration, progress)

        # 'expend' auto shift request if only set once for all
        if numpy.isscalar(self.configuration.axis_0_pos_px):
            self.configuration.axis_0_pos_px = [
                self.configuration.axis_0_pos_px,
            ] * (len(self.z_serie) - 1)
        if numpy.isscalar(self.configuration.axis_1_pos_px):
            self.configuration.axis_1_pos_px = [
                self.configuration.axis_1_pos_px,
            ] * (len(self.z_serie) - 1)
        if numpy.isscalar(self.configuration.axis_2_pos_px):
            self.configuration.axis_2_pos_px = [
                self.configuration.axis_2_pos_px,
            ] * (len(self.z_serie) - 1)

        if self.configuration.axis_0_params is None:
            self.configuration.axis_0_params = {}
        if self.configuration.axis_1_params is None:
            self.configuration.axis_1_params = {}
        if self.configuration.axis_2_params is None:
            self.configuration.axis_2_params = {}

    @staticmethod
    def _dump_frame(output_dataset: h5py.Dataset, index: int, stitched_frame: numpy.ndarray):
        output_dataset[index] = stitched_frame

    @property
    def reading_orders(self):
        """
        as scan can be take on one direction or the order (rotation goes from X to Y then from Y to X)
        we might need to read data from one direction or another
        """
        return self._reading_orders

    @property
    def x_flips(self) -> list:
        return self._x_flips

    @property
    def y_flips(self) -> list:
        return self._y_flips

    def stitch(self, store_composition=True) -> BaseIdentifier:
        """
        :param bool return_composition: if True then return the frame composition (used by the GUI for example to display a background with the same class)
        """
        if self.progress is not None:
            self.progress.set_name("order scans")
        self._order_scans()
        if self.progress is not None:
            self.progress.set_name("check inputs")
        self._check_inputs()
        self.settle_flips()
        self._compute_positions_as_px()
        self._compute_axis_0_estimated_shifts()
        if self.progress is not None:
            self.progress.set_name("compute flat field")
        self._compute_reduced_flats_and_darks()
        if self.progress is not None:
            self.progress.set_name("compute shifts")
        self._compute_shifts()
        self._createOverlapKernels()
        if self.progress is not None:
            self.progress.set_name("stitch projections, save them and create NXtomo")
        self._create_nx_tomo(store_composition=store_composition)
        if self.progress is not None:
            self.progress.set_name("dump configuration")
        self._dump_stitching_configuration()
        stitched_scan = self.configuration.get_output_object()
        return stitched_scan.get_identifier()

    def _order_scans(self):
        """
        ensure scans are in z decreasing order
        """

        def get_min_z(scan):
            return scan.get_bounding_box(axis=0).min

        # order scans from higher z to lower z
        # if axis 0 position is provided then use directly it
        if self.configuration.axis_0_pos_px is not None and len(self.configuration.axis_0_pos_px) > 0:
            order = numpy.argsort(self.configuration.axis_0_pos_px)[::-1]
            sorted_z_serie = Serie(
                self.z_serie.name,
                numpy.take_along_axis(numpy.array(self.z_serie[:]), order, axis=0),
                use_identifiers=False,
            )
        else:
            # else use bounding box
            sorted_z_serie = Serie(
                self.z_serie.name,
                sorted(self.z_serie[:], key=get_min_z, reverse=True),
                use_identifiers=False,
            )
        if sorted_z_serie != self.z_serie:
            if sorted_z_serie[:] != self.z_serie[::-1]:
                raise ValueError("Unable to get comprehensive input. Z (decreasing) ordering is not respected.")
            else:
                _logger.warning(
                    f"z decreasing order haven't been respected. Need to reorder z serie ({[str(scan) for scan in sorted_z_serie[:]]}). Will also reorder overlap height, stitching height and invert shifts"
                )
                if self.configuration.axis_0_pos_mm is not None:
                    self.configuration.axis_0_pos_mm = self.configuration.axis_0_pos_mm[::-1]
                if self.configuration.axis_0_pos_px is not None:
                    self.configuration.axis_0_pos_px = self.configuration.axis_0_pos_px[::-1]
                if self.configuration.axis_1_pos_mm is not None:
                    self.configuration.axis_1_pos_mm = self.configuration.axis_1_pos_mm[::-1]
                if self.configuration.axis_1_pos_px is not None:
                    self.configuration.axis_1_pos_px = self.configuration.axis_1_pos_px[::-1]
                if self.configuration.axis_2_pos_mm is not None:
                    self.configuration.axis_2_pos_mm = self.configuration.axis_2_pos_mm[::-1]
                if self.configuration.axis_2_pos_px is not None:
                    self.configuration.axis_2_pos_px = self.configuration.axis_2_pos_px[::-1]
                if not numpy.isscalar(self._configuration.flip_ud):
                    self._configuration.flip_ud = self._configuration.flip_ud[::-1]
                if not numpy.isscalar(self._configuration.flip_lr):
                    self._configuration.flip_ud = self._configuration.flip_lr[::-1]

        self._z_serie = sorted_z_serie

    def _check_inputs(self):
        """
        insure input data is coherent
        """
        n_scans = len(self.z_serie)
        if n_scans == 0:
            raise ValueError("no scan to stich together")

        for scan in self.z_serie:
            from tomoscan.scanbase import TomoScanBase

            if not isinstance(scan, TomoScanBase):
                raise TypeError(f"z-preproc stitching expects instances of {TomoScanBase}. {type(scan)} provided.")

        # check output file path and data path are provided
        if self.configuration.output_file_path in (None, ""):
            raise ValueError("outptu_file_path should be provided to the configuration")
        if self.configuration.output_data_path in (None, ""):
            raise ValueError("output_data_path should be provided to the configuration")

        # check number of shift provided
        for axis_pos_px, axis_name in zip(
            (
                self.configuration.axis_0_pos_px,
                self.configuration.axis_1_pos_px,
                self.configuration.axis_2_pos_px,
                self.configuration.axis_0_pos_mm,
                self.configuration.axis_1_pos_mm,
                self.configuration.axis_2_pos_mm,
            ),
            (
                "axis_0_pos_px",
                "axis_1_pos_px",
                "axis_2_pos_px",
                "axis_0_pos_mm",
                "axis_1_pos_mm",
                "axis_2_pos_mm",
            ),
        ):
            if isinstance(axis_pos_px, Iterable) and len(axis_pos_px) != (n_scans):
                raise ValueError(f"{axis_name} expect {n_scans} shift defined. Get {len(axis_pos_px)}")

        self._reading_orders = []
        # the first scan will define the expected reading orderd, and expected flip.
        # if all scan are flipped then we will keep it this way
        self._reading_orders.append(1)

        # check scans are coherent (nb projections, rotation angle, energy...)
        for scan_0, scan_1 in zip(self.z_serie[0:-1], self.z_serie[1:]):
            if len(scan_0.projections) != len(scan_1.projections):
                raise ValueError(f"{scan_0} and {scan_1} have a different number of projections")
            if isinstance(scan_0, NXtomoScan) and isinstance(scan_1, NXtomoScan):
                # check rotation (only of is an NXtomoScan)
                scan_0_angles = numpy.asarray(scan_0.rotation_angle)
                scan_0_projections_angles = scan_0_angles[
                    numpy.asarray(scan_0.image_key_control) == ImageKey.PROJECTION.value
                ]
                scan_1_angles = numpy.asarray(scan_1.rotation_angle)
                scan_1_projections_angles = scan_1_angles[
                    numpy.asarray(scan_1.image_key_control) == ImageKey.PROJECTION.value
                ]
                if not numpy.allclose(scan_0_projections_angles, scan_1_projections_angles, atol=10e-1):
                    if numpy.allclose(
                        scan_0_projections_angles,
                        scan_1_projections_angles[::-1],
                        atol=10e-1,
                    ):
                        reading_order = -1 * self._reading_orders[-1]
                    else:
                        raise ValueError(f"Angles from {scan_0} and {scan_1} are different")
                else:
                    reading_order = 1 * self._reading_orders[-1]
                self._reading_orders.append(reading_order)
            # check energy
            if scan_0.energy is None:
                _logger.warning(f"no energy found for {scan_0}")
            elif not numpy.isclose(scan_0.energy, scan_1.energy, rtol=1e-03):
                _logger.warning(
                    f"different energy found between {scan_0} ({scan_0.energy}) and {scan_1} ({scan_1.energy})"
                )
            # check FOV
            if not scan_0.field_of_view == scan_1.field_of_view:
                raise ValueError(f"{scan_0} and {scan_1} have different field of view")
            # check distance
            if scan_0.distance is None:
                _logger.warning(f"no distance found for {scan_0}")
            elif not numpy.isclose(scan_0.distance, scan_1.distance, rtol=10e-3):
                raise ValueError(f"{scan_0} and {scan_1} have different sample / detector distance")
            # check pixel size
            if not numpy.isclose(scan_0.x_pixel_size, scan_1.x_pixel_size):
                raise ValueError(
                    f"{scan_0} and {scan_1} have different x pixel size. {scan_0.x_pixel_size} vs {scan_1.x_pixel_size}"
                )
            if not numpy.isclose(scan_0.y_pixel_size, scan_1.y_pixel_size):
                raise ValueError(
                    f"{scan_0} and {scan_1} have different y pixel size. {scan_0.y_pixel_size} vs {scan_1.y_pixel_size}"
                )
            if scan_0.dim_1 != scan_1.dim_1:
                raise ValueError(
                    f"projections width are expected to be the same. Not the canse for {scan_0} ({scan_0.dim_1} and {scan_1} ({scan_1.dim_1}))"
                )

        for scan in self.z_serie:
            # check x, y and z translation are constant (only if is an NXtomoScan)
            if isinstance(scan, NXtomoScan):
                if scan.x_translation is not None and not numpy.isclose(
                    min(scan.x_translation), max(scan.x_translation)
                ):
                    _logger.warning(
                        "x translations appears to be evolving over time. Might end up with wrong stitching"
                    )
                if scan.y_translation is not None and not numpy.isclose(
                    min(scan.y_translation), max(scan.y_translation)
                ):
                    _logger.warning(
                        "y translations appears to be evolving over time. Might end up with wrong stitching"
                    )
                if scan.z_translation is not None and not numpy.isclose(
                    min(scan.z_translation), max(scan.z_translation)
                ):
                    _logger.warning(
                        "z translations appears to be evolving over time. Might end up with wrong stitching"
                    )

    def _compute_positions_as_px(self):
        """insure we have or we can deduce an estimated position as pixel"""

        def get_position_as_px_on_axis(axis, pos_as_px, pos_as_mm):
            if pos_as_px is not None:
                if pos_as_mm is not None:
                    raise ValueError(
                        f"position of axis {axis} is provided twice: as mm and as px. Please provide one only ({pos_as_mm} vs {pos_as_px})"
                    )
                else:
                    return pos_as_px

            elif pos_as_mm is not None:
                # deduce from position given in configuration and pixel size
                axis_N_pos_px = []
                for scan, pos_in_mm in zip(self.z_serie, pos_as_mm):
                    pixel_size_m = self.configuration.pixel_size or scan.pixel_size
                    axis_N_pos_px.append((pos_in_mm / MetricSystem.MILLIMETER.value) / pixel_size_m)
                return axis_N_pos_px
            else:
                # deduce from motor position and pixel size
                axis_N_pos_px = []
                base_position_m = self.z_serie[0].get_bounding_box(axis=axis).min
                for scan in self.z_serie:
                    pixel_size_m = self.configuration.pixel_size or scan.pixel_size
                    scan_axis_bb = scan.get_bounding_box(axis=axis)
                    axis_N_mean_pos_m = (scan_axis_bb.max - scan_axis_bb.min) / 2 + scan_axis_bb.min
                    axis_N_mean_rel_pos_m = axis_N_mean_pos_m - base_position_m
                    axis_N_pos_px.append(int(axis_N_mean_rel_pos_m / pixel_size_m))
                return axis_N_pos_px

        self.configuration.axis_0_pos_px = get_position_as_px_on_axis(
            axis=0,
            pos_as_px=self.configuration.axis_0_pos_px,
            pos_as_mm=self.configuration.axis_0_pos_mm,
        )
        self.configuration.axis_0_pos_mm = None

        self.configuration.axis_2_pos_px = get_position_as_px_on_axis(
            axis=2,
            pos_as_px=self.configuration.axis_2_pos_px,
            pos_as_mm=self.configuration.axis_2_pos_mm,
        )
        self.configuration.axis_2_pos_mm = None

        # add some log
        if self.configuration.axis_1_pos_mm is not None or self.configuration.axis_1_pos_px is not None:
            _logger.warning("axis 1 position is not handled by the z-stitcher. Will be ignored")
        axis_0_pos = ", ".join([f"{pos}px" for pos in self.configuration.axis_0_pos_px])
        axis_2_pos = ", ".join([f"{pos}px" for pos in self.configuration.axis_2_pos_px])
        _logger.info(f"axis 0 position to be used: " + axis_0_pos)
        _logger.info(f"axis 2 position to be used: " + axis_2_pos)

    def _compute_reduced_flats_and_darks(self):
        """
        make sure reduced dark and flats are existing otherwise compute them
        """
        for scan in self.z_serie:
            try:
                reduced_darks, darks_infos = scan.load_reduced_darks(return_info=True)
            except:
                _logger.info("no reduced dark found. Try to compute them.")
            if reduced_darks in (None, {}):
                reduced_darks, darks_infos = scan.compute_reduced_darks(return_info=True)
                try:
                    # if we don't have write in the folder containing the .nx for example
                    scan.save_reduced_darks(reduced_darks, darks_infos=darks_infos)
                except Exception as e:
                    pass
            scan.set_reduced_darks(reduced_darks, darks_infos=darks_infos)

            try:
                reduced_flats, flats_infos = scan.load_reduced_flats(return_info=True)
            except:
                _logger.info("no reduced flats found. Try to compute them.")
            if reduced_flats in (None, {}):
                reduced_flats, flats_infos = scan.compute_reduced_flats(return_info=True)
                try:
                    # if we don't have write in the folder containing the .nx for example
                    scan.save_reduced_flats(reduced_flats, flats_infos=flats_infos)
                except Exception as e:
                    pass
            scan.set_reduced_flats(reduced_flats, flats_infos=flats_infos)

    def _compute_shifts(self):
        """
        compute all shift requested (set to 'auto' in the configuration)
        """
        n_scans = len(self.configuration.input_scans)
        if n_scans == 0:
            raise ValueError("no scan to stich provided")

        projection_for_shift = self.configuration.slice_for_cross_correlation or "middle"
        y_rel_shifts = self._axis_0_estimated_shifts
        x_rel_shifts = self.from_abs_pos_to_rel_pos(self.configuration.axis_2_pos_px)

        final_rel_shifts = []
        for (
            scan_0,
            scan_1,
            order_s0,
            order_s1,
            x_rel_shift,
            y_rel_shift,
        ) in zip(
            self.z_serie[:-1],
            self.z_serie[1:],
            self.reading_orders[:-1],
            self.reading_orders[1:],
            x_rel_shifts,
            y_rel_shifts,
        ):
            x_cross_algo = self.configuration.axis_2_params.get(KEY_IMG_REG_METHOD, None)
            y_cross_algo = self.configuration.axis_0_params.get(KEY_IMG_REG_METHOD, None)

            # compute relative shift
            found_shift_y, found_shift_x = find_projections_relative_shifts(
                upper_scan=scan_0,
                lower_scan=scan_1,
                projection_for_shift=projection_for_shift,
                x_cross_correlation_function=x_cross_algo,
                y_cross_correlation_function=y_cross_algo,
                x_shifts_params=self.configuration.axis_2_params,
                y_shifts_params=self.configuration.axis_0_params,
                invert_order=order_s1 != order_s0,
                estimated_shifts=(y_rel_shift, x_rel_shift),
            )
            final_rel_shifts.append(
                (found_shift_y, found_shift_x),
            )

        # set back values. Now position should start at 0
        self._axis_0_rel_shifts = [final_shift[0] for final_shift in final_rel_shifts]
        self._axis_2_rel_shifts = [final_shift[1] for final_shift in final_rel_shifts]
        _logger.info(f"axis 2 relative shifts (x in radio ref) to be used will be {self._axis_0_rel_shifts}")
        print(f"axis 2 relative shifts (x in radio ref) to be used will be {self._axis_0_rel_shifts}")
        _logger.info(f"axis 0 relative shifts (y in radio ref) y to be used will be {self._axis_2_rel_shifts}")
        print(f"axis 0 relative shifts (y in radio ref) y to be used will be {self._axis_2_rel_shifts}")

    @staticmethod
    def _get_bunch_of_data(
        bunch_start: int,
        bunch_end: int,
        step: int,
        scans: tuple,
        scans_projections_indexes: tuple,
        reading_orders: tuple,
        flip_lr_arr: tuple,
        flip_ud_arr: tuple,
    ):
        """
        goal is to load contiguous projections as much as possible...

        :param int bunch_start: begining of the bunch
        :param int bunch_end: end of the bunch
        :param int scans: ordered scan for which we want to get data
        :param scans_projections_indexes: tuple with scans and scan projection indexes to be loaded
        :param tuple flip_lr_arr: extra information from the user to left-right flip frames
        :param tuple flip_ud_arr: extra information from the user to up-down flip frames
        :return: list of list. For each frame we want to stitch contains the (flat fielded) frames to stich together
        """
        assert len(scans) == len(scans_projections_indexes)
        assert isinstance(flip_lr_arr, tuple)
        assert isinstance(flip_ud_arr, tuple)
        assert isinstance(step, int)
        scans_proj_urls = []
        # for each scan store the real indices and the data url

        for scan, scan_projection_indexes in zip(scans, scans_projections_indexes):
            scan_proj_urls = {}
            # for each scan get the list of url to be loaded
            for i_proj in range(bunch_start, bunch_end):
                if i_proj % step != 0:
                    continue
                proj_index_in_full_scan = scan_projection_indexes[i_proj]
                scan_proj_urls[proj_index_in_full_scan] = scan.projections[proj_index_in_full_scan]
            scans_proj_urls.append(scan_proj_urls)

        # then load data
        all_scan_final_data = numpy.empty((bunch_end - bunch_start, len(scans)), dtype=object)
        from nabu.preproc.flatfield import FlatFieldArrays

        for i_scan, (scan_urls, scan_flip_lr, scan_flip_ud, reading_order) in enumerate(
            zip(scans_proj_urls, flip_lr_arr, flip_ud_arr, reading_orders)
        ):
            i_frame = 0
            _, set_of_compacted_slices = get_compacted_dataslices(scan_urls, return_url_set=True)
            for _, url in set_of_compacted_slices.items():
                scan = scans[i_scan]
                url = DataUrl(
                    file_path=url.file_path(),
                    data_path=url.data_path(),
                    scheme="silx",
                    data_slice=url.data_slice(),
                )
                raw_radios = get_data(url)[::reading_order]
                radio_indices = url.data_slice()
                if isinstance(radio_indices, slice):
                    step = radio_indices.step if radio_indices is not None else 1
                    radio_indices = numpy.arange(
                        start=radio_indices.start,
                        stop=radio_indices.stop,
                        step=step,
                        dtype=numpy.int16,
                    )

                missing = []
                if len(scan.reduced_flats) == 0:
                    missing = "flats"
                if len(scan.reduced_darks) == 0:
                    missing = "darks"

                if len(missing) > 0:
                    _logger.warning(f"missing {'and'.join(missing)}. Unable to do flat field correction")
                    ff_arrays = None
                    data = raw_radios
                else:
                    has_reduced_metadata = (
                        scan.reduced_flats_infos is not None
                        and len(scan.reduced_flats_infos.machine_electric_current) > 0
                        and scan.reduced_darks_infos is not None
                        and len(scan.reduced_darks_infos.machine_electric_current) > 0
                    )
                    if not has_reduced_metadata:
                        _logger.warning("no metadata about current found. Won't normalize according to machine current")

                    ff_arrays = FlatFieldArrays(
                        radios_shape=(len(radio_indices), scan.dim_2, scan.dim_1),
                        flats=scan.reduced_flats,
                        darks=scan.reduced_darks,
                        radios_indices=radio_indices,
                        radios_srcurrent=scan.electric_current[radio_indices] if has_reduced_metadata else None,
                        flats_srcurrent=(
                            scan.reduced_flats_infos.machine_electric_current if has_reduced_metadata else None
                        ),
                    )
                    # note: we need to cast radios to float 32. Darks and flats are cast to anyway
                    data = ff_arrays.normalize_radios(raw_radios.astype(numpy.float32))

                transformations = list(scans[i_scan].get_detector_transformations(tuple()))
                if scan_flip_lr:
                    transformations.append(LRDetTransformation())
                if scan_flip_ud:
                    transformations.append(UDDetTransformation())

                transformation_matrix_det_space = build_matrix(transformations)
                if transformation_matrix_det_space is None or numpy.allclose(
                    transformation_matrix_det_space, numpy.identity(3)
                ):
                    flip_ud = False
                    flip_lr = False
                elif numpy.array_equal(transformation_matrix_det_space, ZStitcher._get_UD_flip_matrix()):
                    flip_ud = True
                    flip_lr = False
                elif numpy.allclose(transformation_matrix_det_space, ZStitcher._get_LR_flip_matrix()):
                    flip_ud = False
                    flip_lr = True
                elif numpy.allclose(transformation_matrix_det_space, ZStitcher._get_UD_AND_LR_flip_matrix()):
                    flip_ud = True
                    flip_lr = True
                else:
                    raise ValueError("case not handled... For now only handle up-down flip as left-right flip")

                for frame in data:
                    if flip_ud:
                        frame = numpy.flipud(frame)
                    if flip_lr:
                        frame = numpy.fliplr(frame)
                    all_scan_final_data[i_frame, i_scan] = frame
                    i_frame += 1

        return all_scan_final_data

    def _compute_axis_0_estimated_shifts(self):
        axis_0_pos_px = self.configuration.axis_0_pos_px
        self._axis_0_estimated_shifts = []
        # compute overlap along axis 0
        for upper_scan, lower_scan, upper_scan_axis_0_pos, lower_scan_axis_0_pos in zip(
            self.z_serie[:-1], self.z_serie[1:], axis_0_pos_px[:-1], axis_0_pos_px[1:]
        ):
            upper_scan_pos = upper_scan_axis_0_pos - upper_scan.dim_2 / 2
            lower_scan_high_pos = lower_scan_axis_0_pos + lower_scan.dim_2 / 2
            # simple test of overlap. More complete test are runned by check_overlaps later
            if lower_scan_high_pos <= upper_scan_pos:
                raise ValueError(f"no overlap found between {upper_scan} and {lower_scan}")
            self._axis_0_estimated_shifts.append(
                int(lower_scan_high_pos - upper_scan_pos)  # overlap are expected to be int for now
            )

    def _create_nx_tomo(self, store_composition: bool = False):
        """
        create final NXtomo with stitched frames.
        Policy: save all projections flat fielded. So this NXtomo will only contain projections (no dark and no flat).
        But nabu will be able to reconstruct it with field `flatfield` set to False
        """
        nx_tomo = NXtomo()

        nx_tomo.energy = self.z_serie[0].energy
        start_times = list(filter(None, [scan.start_time for scan in self.z_serie]))
        end_times = list(filter(None, [scan.end_time for scan in self.z_serie]))

        if len(start_times) > 0:
            nx_tomo.start_time = (
                numpy.asarray([numpy.datetime64(start_time) for start_time in start_times]).min().astype(datetime)
            )
        else:
            _logger.warning("Unable to find any start_time from input")
        if len(end_times) > 0:
            nx_tomo.end_time = (
                numpy.asarray([numpy.datetime64(end_time) for end_time in end_times]).max().astype(datetime)
            )
        else:
            _logger.warning("Unable to find any end_time from input")

        title = ";".join([scan.sequence_name or "" for scan in self.z_serie])
        nx_tomo.title = f"stitch done from {title}"

        self._slices_to_stitch, n_proj = self.configuration.settle_slices()

        # handle detector (without frames)
        nx_tomo.instrument.detector.field_of_view = self.z_serie[0].field_of_view
        nx_tomo.instrument.detector.distance = self.z_serie[0].distance
        nx_tomo.instrument.detector.x_pixel_size = self.z_serie[0].x_pixel_size
        nx_tomo.instrument.detector.y_pixel_size = self.z_serie[0].y_pixel_size
        nx_tomo.instrument.detector.image_key_control = [ImageKey.PROJECTION] * n_proj
        nx_tomo.instrument.detector.tomo_n = n_proj
        # note: stitching process insure unflipping of frames. So make sure transformations is defined as an empty set
        nx_tomo.instrument.detector.transformations = NXtransformations()

        if isinstance(self.z_serie[0], NXtomoScan):
            # note: first scan is always the reference as order to read data (so no rotation_angle inversion here)
            rotation_angle = numpy.asarray(self.z_serie[0].rotation_angle)
            nx_tomo.sample.rotation_angle = rotation_angle[
                numpy.asarray(self.z_serie[0].image_key_control) == ImageKey.PROJECTION.value
            ]
        elif isinstance(self.z_serie[0], EDFTomoScan):
            nx_tomo.sample.rotation_angle = numpy.linspace(
                start=0, stop=self.z_serie[0].scan_range, num=self.z_serie[0].tomo_n
            )
        else:
            raise NotImplementedError(
                f"scan type ({type(self.z_serie[0])} is not handled)",
                NXtomoScan,
                isinstance(self.z_serie[0], NXtomoScan),
            )

        # do a sub selection of the rotation angle if a we are only computing a part of the slices
        def apply_slices_selection(array, slices):
            if isinstance(slices, slice):
                return array[slices.start : slices.stop : 1]
            elif isinstance(slices, Iterable):
                return list([array[index] for index in slices])
            else:
                raise RuntimeError("slices must be instance of a slice or of an iterable")

        nx_tomo.sample.rotation_angle = apply_slices_selection(
            array=nx_tomo.sample.rotation_angle, slices=self._slices_to_stitch
        )

        # handle sample
        n_frames = n_proj
        if False not in [isinstance(scan, NXtomoScan) for scan in self.z_serie]:
            # we consider the new x, y and z position to be at the center of the one created
            x_translation = [scan.x_translation for scan in self.z_serie if scan.x_translation is not None]
            nx_tomo.sample.x_translation = [numpy.asarray(x_translation).mean()] * n_frames
            y_translation = [scan.y_translation for scan in self.z_serie if scan.y_translation is not None]
            nx_tomo.sample.y_translation = [numpy.asarray(y_translation).mean()] * n_frames
            z_translation = [scan.z_translation for scan in self.z_serie if scan.z_translation is not None]
            nx_tomo.sample.z_translation = [numpy.asarray(z_translation).mean()] * n_frames

            nx_tomo.sample.name = self.z_serie[0].sample_name

        # compute stiched frame shape
        stitched_frame_shape = (
            n_proj,
            (
                numpy.asarray([scan.dim_2 for scan in self.z_serie]).sum()
                - numpy.asarray([abs(overlap) for overlap in self._axis_0_rel_shifts]).sum()
            ),
            self._stitching_width,
        )

        # get expected output dataset first (just in case output and input files are the same)
        first_proj_idx = sorted(self.z_serie[0].projections.keys())[0]
        first_proj_url = self.z_serie[0].projections[first_proj_idx]
        if h5py.is_hdf5(first_proj_url.file_path()):
            first_proj_url = DataUrl(
                file_path=first_proj_url.file_path(),
                data_path=first_proj_url.data_path(),
                scheme="h5py",
            )

        # first save the NXtomo entry without the frame
        # dicttonx will fail if the folder does not exists
        dir_name = os.path.dirname(self.configuration.output_file_path)
        if dir_name not in (None, ""):
            os.makedirs(dir_name, exist_ok=True)
        nx_tomo.save(
            file_path=self.configuration.output_file_path,
            data_path=self.configuration.output_data_path,
            nexus_path_version=self.configuration.output_nexus_version,
            overwrite=self.configuration.overwrite_results,
        )

        transformation_matrices = {
            scan.get_identifier()
            .to_str()
            .center(80, "-"): numpy.array2string(build_matrix(scan.get_detector_transformations(tuple())))
            for scan in self.z_serie
        }
        _logger.info(
            "scan detector transformation matrices are:\n"
            "\n".join(["/n".join(item) for item in transformation_matrices.items()])
        )

        _logger.info(
            f"reading order is {self.reading_orders}",
        )

        def get_output_data_type():
            return numpy.float32  # because we will apply flat field correction on it and they are not raw data
            # scan = self.z_serie[0]
            # radio_url = tuple(scan.projections.values())[0]
            # assert isinstance(radio_url, DataUrl)
            # data = get_data(radio_url)
            # return data.dtype

        output_dtype = get_output_data_type()
        # append frames ("instrument/detactor/data" dataset)
        with HDF5File(self.configuration.output_file_path, mode="a") as h5f:
            # note: nx_tomo.save already handles the possible overwrite conflict by removing
            # self.configuration.output_file_path or raising an error

            stitched_frame_path = "/".join(
                [
                    self.configuration.output_data_path,
                    _get_nexus_paths(self.configuration.output_nexus_version).PROJ_PATH,
                ]
            )
            projection_dataset = h5f.create_dataset(
                name=stitched_frame_path,
                shape=stitched_frame_shape,
                dtype=output_dtype,
            )
            # TODO: we could also create in several time and create a virtual dataset from it.
            scans_projections_indexes = []
            for scan, reverse in zip(self.z_serie, self.reading_orders):
                scans_projections_indexes.append(sorted(scan.projections.keys(), reverse=(reverse == -1)))
            if self.progress:
                self.progress.set_max_advancement(len(scan.projections.keys()))

            if isinstance(self._slices_to_stitch, slice):
                step = self._slices_to_stitch.step or 1
            else:
                step = 1
            i_proj = 0
            for bunch_start, bunch_end in PreProcessZStitcher._data_bunch_iterator(
                slices=self._slices_to_stitch, bunch_size=50
            ):
                for data_frames in PreProcessZStitcher._get_bunch_of_data(
                    bunch_start,
                    bunch_end,
                    step=step,
                    scans=self.z_serie,
                    scans_projections_indexes=scans_projections_indexes,
                    flip_ud_arr=self.configuration.flip_ud,
                    flip_lr_arr=self.configuration.flip_lr,
                    reading_orders=self.reading_orders,
                ):
                    if self.configuration.rescale_frames:
                        data_frames = self.rescale_frames(data_frames)
                    if self.configuration.normalization_by_sample.is_active():
                        data_frames = self.normalize_frame_by_sample(data_frames)

                    sf = ZStitcher.stitch_frames(
                        frames=data_frames,
                        x_relative_shifts=self._axis_2_rel_shifts,
                        y_relative_shifts=self._axis_0_rel_shifts,
                        output_dataset=projection_dataset,
                        overlap_kernels=self._overlap_kernels,
                        i_frame=i_proj,
                        output_dtype=output_dtype,
                        dump_frame_fct=self._dump_frame,
                        return_composition_cls=store_composition if i_proj == 0 else False,
                        stitching_axis=0,
                        pad_mode=self.configuration.pad_mode,
                        alignment=self.configuration.alignment_axis_2,
                        new_width=self._stitching_width,
                        check_inputs=i_proj == 0,  # on process check on the first iteration
                    )
                    if i_proj == 0 and store_composition:
                        _, self._frame_composition = sf
                    if self.progress is not None:
                        self.progress.increase_advancement()

                    i_proj += 1

            # create link to this dataset that can be missing
            # "data/data" link
            if "data" in h5f[self.configuration.output_data_path]:
                data_group = h5f[self.configuration.output_data_path]["data"]
                if not stitched_frame_path.startswith("/"):
                    stitched_frame_path = "/" + stitched_frame_path
                data_group["data"] = h5py.SoftLink(stitched_frame_path)
                if "default" not in h5f[self.configuration.output_data_path].attrs:
                    h5f[self.configuration.output_data_path].attrs["default"] = "data"
                for attr_name, attr_value in zip(
                    ("NX_class", "SILX_style/axis_scale_types", "signal"),
                    ("NXdata", ["linear", "linear"], "data"),
                ):
                    if attr_name not in data_group.attrs:
                        data_group.attrs[attr_name] = attr_value

        return nx_tomo

    def _dump_stitching_configuration(self):
        """dump configuration used for stitching at the NXtomo entry"""
        process_name = "stitching_configuration"
        config_dict = self.configuration.to_dict()
        # adding nabu specific information
        nabu_process_info = {
            "@NX_class": "NXentry",
            f"{process_name}@NX_class": "NXprocess",
            f"{process_name}/program": "nabu-stitching",
            f"{process_name}/version": nabu_version,
            f"{process_name}/date": get_datetime(),
            f"{process_name}/configuration": config_dict,
        }

        dicttonx(
            nabu_process_info,
            h5file=self.configuration.output_file_path,
            h5path=self.configuration.output_data_path,
            update_mode="replace",
            mode="a",
        )


class PostProcessZStitcher(ZStitcher):
    def __init__(self, configuration, progress: Progress = None) -> None:
        self._input_volumes = configuration.input_volumes
        self.__output_data_type = None

        self._z_serie = Serie("z-serie", iterable=self._input_volumes, use_identifiers=False)
        super().__init__(configuration, progress)

    @staticmethod
    def _dump_frame(output_dataset: h5py.Dataset, index: int, stitched_frame: numpy.ndarray):
        # fix numpy array direction to be coherent with input data
        # stitched_frame is received a `z-down` frame and we want to return in the same orientation (`z-up`)
        output_dataset[:, index, :] = stitched_frame

    def stitch(self, store_composition=True) -> BaseIdentifier:
        """
        Apply expected stitch from configuration and return the DataUrl of the object created
        """
        if self.progress is not None:
            self.progress.set_name("order volumes")
        self._order_volumes()
        if self.progress is not None:
            self.progress.set_name("check inputs")
        self._check_inputs()
        self.settle_flips()
        if self.progress is not None:
            self.progress.set_name("compute shifts")
        self._compute_positions_as_px()
        self._compute_axis_0_estimated_shifts()
        self._compute_shifts()
        self._createOverlapKernels()
        if self.progress is not None:
            self.progress.set_name("stitch volumes")
        self._create_stitched_volume(store_composition=store_composition)
        if self.progress is not None:
            self.progress.set_name("dump configuration")
        self._dump_stitching_configuration()
        return self.configuration.output_volume.get_identifier()

    def _order_volumes(self):
        """
        ensure scans are in z increasing order
        """

        def get_min_z(volume):
            try:
                bb = volume.get_bounding_box(axis="z")
            except ValueError:  #  if missing information
                bb = None
            if bb is not None:
                return bb.min
            else:
                # if can't find bounding box (missing metadata to the volume
                # try to get it from the scan
                metadata = volume.metadata or volume.load_metadata()
                scan_location = metadata.get("nabu_config", {}).get("dataset", {}).get("location", None)
                scan_entry = metadata.get("nabu_config", {}).get("dataset", {}).get("hdf5_entry", None)
                if scan_location is not None:
                    # this work around (until most volume have position metadata) works only for Hdf5volume
                    with cwd_context(os.path.dirname(volume.file_path)):
                        o_scan = NXtomoScan(scan_location, scan_entry)
                        bb_acqui = o_scan.get_bounding_box(axis=None)
                        # for next step volume position will be required.
                        # if you can find it set it directly
                        volume.position = (numpy.array(bb_acqui.max) - numpy.array(bb_acqui.min)) / 2.0 + numpy.array(
                            bb_acqui.min
                        )
                        # for now translation are stored in pixel size ref instead of real_pixel_size
                        volume.pixel_size = o_scan.x_real_pixel_size
                        if bb_acqui is not None:
                            return bb_acqui.min[0]
                raise ValueError("Unable to find volume position. Unable to deduce z position")

        try:
            # order volumes from higher z to lower z
            # if axis 0 position is provided then use directly it
            if self.configuration.axis_0_pos_px is not None and len(self.configuration.axis_0_pos_px) > 0:
                order = numpy.argsort(self.configuration.axis_0_pos_px)
                sorted_z_serie = Serie(
                    self.z_serie.name,
                    numpy.take_along_axis(numpy.array(self.z_serie[:]), order, axis=0)[::-1],
                    use_identifiers=False,
                )
            else:
                # else use bounding box
                sorted_z_serie = Serie(
                    self.z_serie.name,
                    sorted(self.z_serie[:], key=get_min_z, reverse=True),
                    use_identifiers=False,
                )
        except ValueError:
            _logger.warning(
                "Unable to find volume positions in metadata. Expect the volume to be ordered already (decreasing along axis 0.)"
            )
        else:
            if sorted_z_serie == self.z_serie:
                pass
            elif sorted_z_serie != self.z_serie:
                if sorted_z_serie[:] != self.z_serie[::-1]:
                    raise ValueError(
                        "Unable to get comprehensive input. ordering along axis 0 is not respected (decreasing)."
                    )
                else:
                    _logger.warning(
                        f"z decreasing order haven't been respected. Need to reorder z serie ({[str(scan) for scan in sorted_z_serie[:]]}). Will also reorder positions"
                    )
                    if self.configuration.axis_0_pos_mm is not None:
                        self.configuration.axis_0_pos_mm = self.configuration.axis_0_pos_mm[::-1]
                    if self.configuration.axis_0_pos_px is not None:
                        self.configuration.axis_0_pos_px = self.configuration.axis_0_pos_px[::-1]
                    if self.configuration.axis_1_pos_mm is not None:
                        self.configuration.axis_1_pos_mm = self.configuration.axis_1_pos_mm[::-1]
                    if self.configuration.axis_1_pos_px is not None:
                        self.configuration.axis_1_pos_px = self.configuration.axis_1_pos_px[::-1]
                    if self.configuration.axis_2_pos_mm is not None:
                        self.configuration.axis_2_pos_mm = self.configuration.axis_2_pos_mm[::-1]
                    if self.configuration.axis_2_pos_px is not None:
                        self.configuration.axis_2_pos_px = self.configuration.axis_2_pos_px[::-1]
                    if not numpy.isscalar(self._configuration.flip_ud):
                        self._configuration.flip_ud = self._configuration.flip_ud[::-1]
                    if not numpy.isscalar(self._configuration.flip_lr):
                        self._configuration.flip_ud = self._configuration.flip_lr[::-1]

                    self._z_serie = sorted_z_serie

    def _compute_positions_as_px(self):
        """compute if necessary position other axis 0 from volume metadata"""

        def get_position_as_px_on_axis(axis, pos_as_px, pos_as_mm):
            if pos_as_px is not None:
                if pos_as_mm is not None:
                    raise ValueError(
                        f"position of axis {axis} is provided twice: as mm and as px. Please provide one only ({pos_as_mm} vs {pos_as_px})"
                    )
                else:
                    return pos_as_px

            elif pos_as_mm is not None:
                # deduce from position given in configuration and pixel size
                axis_N_pos_px = []
                for volume, pos_in_mm in zip(self.z_serie, pos_as_mm):
                    voxel_size_m = self.configuration.voxel_size or volume.voxel_size
                    axis_N_pos_px.append((pos_in_mm / MetricSystem.MILLIMETER.value) / voxel_size_m[0])
                return axis_N_pos_px
            else:
                # deduce from motor position and pixel size
                axis_N_pos_px = []
                base_position_m = self.z_serie[0].get_bounding_box(axis=axis).min
                for volume in self.z_serie:
                    voxel_size_m = self.configuration.voxel_size or volume.voxel_size
                    volume_axis_bb = volume.get_bounding_box(axis=axis)
                    axis_N_mean_pos_m = (volume_axis_bb.max - volume_axis_bb.min) / 2 + volume_axis_bb.min
                    axis_N_mean_rel_pos_m = axis_N_mean_pos_m - base_position_m
                    axis_N_pos_px.append(int(axis_N_mean_rel_pos_m / voxel_size_m[0]))
                return axis_N_pos_px

        self.configuration.axis_0_pos_px = get_position_as_px_on_axis(
            axis=0,
            pos_as_px=self.configuration.axis_0_pos_px,
            pos_as_mm=self.configuration.axis_0_pos_mm,
        )
        self.configuration.axis_0_pos_mm = None

        self.configuration.axis_2_pos_px = get_position_as_px_on_axis(
            axis=2,
            pos_as_px=self.configuration.axis_2_pos_px,
            pos_as_mm=self.configuration.axis_2_pos_mm,
        )
        self.configuration.axis_2_pos_mm = None

    def _compute_axis_0_estimated_shifts(self):
        axis_0_pos_px = self.configuration.axis_0_pos_px
        self._axis_0_estimated_shifts = []
        # compute overlap along axis 0
        for upper_volume, lower_volume, upper_volume_axis_0_pos, lower_volume_axis_0_pos in zip(
            self.z_serie[:-1], self.z_serie[1:], axis_0_pos_px[:-1], axis_0_pos_px[1:]
        ):
            upper_volume_low_pos = upper_volume_axis_0_pos - upper_volume.get_volume_shape()[0] / 2
            lower_volume_high_pos = lower_volume_axis_0_pos + lower_volume.get_volume_shape()[0] / 2
            self._axis_0_estimated_shifts.append(
                int(lower_volume_high_pos - upper_volume_low_pos)  # overlap are expected to be int for now
            )

    def _compute_shifts(self):
        n_volumes = len(self.configuration.input_volumes)
        if n_volumes == 0:
            raise ValueError("no scan to stich provided")

        slice_for_shift = self.configuration.slice_for_cross_correlation or "middle"
        y_rel_shifts = self._axis_0_estimated_shifts
        x_rel_shifts = self.from_abs_pos_to_rel_pos(self.configuration.axis_2_pos_px)
        dim_axis_1 = max([volume.get_volume_shape()[1] for volume in self.z_serie])

        final_rel_shifts = []
        for (
            upper_volume,
            lower_volume,
            x_rel_shift,
            y_rel_shift,
            flip_ud_upper,
            flip_ud_lower,
        ) in zip(
            self.z_serie[:-1],
            self.z_serie[1:],
            x_rel_shifts,
            y_rel_shifts,
            self.configuration.flip_ud[:-1],
            self.configuration.flip_ud[1:],
        ):
            x_cross_algo = self.configuration.axis_2_params.get(KEY_IMG_REG_METHOD, None)
            y_cross_algo = self.configuration.axis_0_params.get(KEY_IMG_REG_METHOD, None)

            # compute relative shift
            found_shift_y, found_shift_x = find_volumes_relative_shifts(
                upper_volume=upper_volume,
                lower_volume=lower_volume,
                dtype=self.get_output_data_type(),
                dim_axis_1=dim_axis_1,
                slice_for_shift=slice_for_shift,
                x_cross_correlation_function=x_cross_algo,
                y_cross_correlation_function=y_cross_algo,
                x_shifts_params=self.configuration.axis_2_params,
                y_shifts_params=self.configuration.axis_0_params,
                estimated_shifts=(y_rel_shift, x_rel_shift),
                flip_ud_lower_frame=flip_ud_lower,
                flip_ud_upper_frame=flip_ud_upper,
                alignment_axis_1=self.configuration.alignment_axis_1,
                alignment_axis_2=self.configuration.alignment_axis_2,
            )
            final_rel_shifts.append(
                (found_shift_y, found_shift_x),
            )

        # set back values. Now position should start at 0
        self._axis_0_rel_shifts = [final_shift[0] for final_shift in final_rel_shifts]
        self._axis_2_rel_shifts = [final_shift[1] for final_shift in final_rel_shifts]
        _logger.info(f"axis 2 relative shifts (x in radio ref) to be used will be {self._axis_2_rel_shifts}")
        print(f"axis 2 relative shifts (x in radio ref) to be used will be {self._axis_2_rel_shifts}")
        _logger.info(f"axis 0 relative shifts (y in radio ref) y to be used will be {self._axis_0_rel_shifts}")
        print(f"axis 0 relative shifts (y in radio ref) y to be used will be {self._axis_0_rel_shifts}")

    def _dump_stitching_configuration(self):
        voxel_size = self._input_volumes[0].voxel_size

        def get_position():
            # the z-serie is z-ordered from higher to lower. We can reuse this with pixel size and shape to
            # compute the position of the stitched volume
            if voxel_size is None:
                return None
            return numpy.array(self._input_volumes[0].position) + voxel_size * (
                numpy.array(self._input_volumes[0].get_volume_shape()) / 2.0
                - numpy.array(self.configuration.output_volume.get_volume_shape()) / 2.0
            )

        self.configuration.output_volume.voxel_size = voxel_size or ""
        try:
            self.configuration.output_volume.position = get_position()
        except Exception:
            self.configuration.output_volume.position = numpy.array([0, 0, 0])

        self.configuration.output_volume.metadata.update(
            {
                "program": "nabu-stitching",
                "version": nabu_version,
                "date": get_datetime(),
                "configuration": self.configuration.to_dict(),
            }
        )
        self.configuration.output_volume.save_metadata()

    def _check_inputs(self):
        """
        insure input data is coherent
        """
        # check input volume
        if self.configuration.output_volume is None:
            raise ValueError("input volume should be provided")

        n_volumes = len(self.z_serie)
        if n_volumes == 0:
            raise ValueError("no scan to stich together")

        if not isinstance(self.configuration.output_volume, VolumeBase):
            raise TypeError(f"make sure we return a volume identifier not {(type(self.configuration.output_volume))}")

        # check axis 0 position
        if isinstance(self.configuration.axis_0_pos_px, Iterable) and len(self.configuration.axis_0_pos_px) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_0_pos_px)}")
        if isinstance(self.configuration.axis_0_pos_mm, Iterable) and len(self.configuration.axis_0_pos_mm) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_0_pos_mm)}")

        # check axis 1 position
        if isinstance(self.configuration.axis_1_pos_px, Iterable) and len(self.configuration.axis_1_pos_px) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_1_pos_px)}")
        if isinstance(self.configuration.axis_1_pos_mm, Iterable) and len(self.configuration.axis_1_pos_mm) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_1_pos_mm)}")

        # check axis 2 position
        if isinstance(self.configuration.axis_2_pos_px, Iterable) and len(self.configuration.axis_2_pos_px) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_2_pos_px)}")
        if isinstance(self.configuration.axis_2_pos_mm, Iterable) and len(self.configuration.axis_2_pos_mm) != (
            n_volumes
        ):
            raise ValueError(f"expect {n_volumes} overlap defined. Get {len(self.configuration.axis_2_pos_mm)}")

        self._reading_orders = []
        # the first scan will define the expected reading orderd, and expected flip.
        # if all scan are flipped then we will keep it this way
        self._reading_orders.append(1)

    def get_output_data_type(self):
        if self.__output_data_type is None:

            def find_output_data_type():
                first_vol = self._input_volumes[0]
                if first_vol.data is not None:
                    return first_vol.data.dtype
                elif isinstance(first_vol, HDF5Volume):
                    with DatasetReader(first_vol.data_url) as vol_dataset:
                        return vol_dataset.dtype
                else:
                    return first_vol.load_data(store=False).dtype

            self.__output_data_type = find_output_data_type()
        return self.__output_data_type

    def _create_stitched_volume(self, store_composition: bool):
        overlap_kernels = self._overlap_kernels
        self._slices_to_stitch, n_slices = self.configuration.settle_slices()

        # sync overwrite_results with volume overwrite parameter
        self.configuration.output_volume.overwrite = self.configuration.overwrite_results

        # init final volume
        final_volume = self.configuration.output_volume
        final_volume_shape = (
            int(
                numpy.asarray([volume.get_volume_shape()[0] for volume in self._input_volumes]).sum()
                - numpy.asarray([abs(overlap) for overlap in self._axis_0_rel_shifts]).sum(),
            ),
            n_slices,
            self._stitching_width,
        )

        data_type = self.get_output_data_type()

        if self.progress:
            self.progress.set_max_advancement(final_volume_shape[1])

        y_index = 0
        if isinstance(self._slices_to_stitch, slice):
            step = self._slices_to_stitch.step or 1
        else:
            step = 1
        with PostProcessZStitcher._FinalDatasetContext(
            volume=final_volume, volume_shape=final_volume_shape, dtype=data_type
        ) as output_dataset:
            # note: output_dataset is a HDF5 dataset if final volume is an HDF5 volume else is a numpy array
            with PostProcessZStitcher._RawDatasetsContext(
                self._input_volumes,
                alignment_axis_1=self.configuration.alignment_axis_1,
            ) as raw_datasets:
                # note: raw_datasets can be numpy arrays or HDF5 dataset (in the case of HDF5Volume)
                # to speed up we read by bunch of dataset. For numpy array this doesn't change anything
                # but for HDF5 dataset this can speed up a lot the processing (depending on HDF5 dataset chuncks)
                # note: we read trhough axis 1
                for bunch_start, bunch_end in PostProcessZStitcher._data_bunch_iterator(
                    slices=self._slices_to_stitch, bunch_size=50
                ):
                    for data_frames in PostProcessZStitcher._get_bunch_of_data(
                        bunch_start,
                        bunch_end,
                        step=step,
                        volumes=raw_datasets,
                        flip_lr_arr=self.configuration.flip_lr,
                        flip_ud_arr=self.configuration.flip_ud,
                    ):
                        if self.configuration.rescale_frames:
                            data_frames = self.rescale_frames(data_frames)
                        if self.configuration.normalization_by_sample.is_active():
                            data_frames = self.normalize_frame_by_sample(data_frames)

                        sf = ZStitcher.stitch_frames(
                            frames=data_frames,
                            x_relative_shifts=self._axis_2_rel_shifts,
                            y_relative_shifts=self._axis_0_rel_shifts,
                            overlap_kernels=overlap_kernels,
                            output_dataset=output_dataset,
                            dump_frame_fct=self._dump_frame,
                            i_frame=y_index,
                            output_dtype=data_type,
                            return_composition_cls=store_composition if y_index == 0 else False,
                            stitching_axis=0,
                            check_inputs=y_index == 0,  # on process check on the first iteration
                        )
                        if y_index == 0 and store_composition:
                            _, self._frame_composition = sf

                        if self.progress is not None:
                            self.progress.increase_advancement()
                        y_index += 1

    @staticmethod
    def _get_bunch_of_data(
        bunch_start: int,
        bunch_end: int,
        step: int,
        volumes: tuple,
        flip_lr_arr: bool,
        flip_ud_arr: bool,
    ):
        """
        goal is to load contiguous frames as much as possible...
        return for each volume the bunch of slice along axis 1
        warning: they can have different shapes
        """

        def get_sub_volume(volume, flip_lr, flip_ud):
            sub_volume = volume[:, bunch_start:bunch_end:step, :]
            if flip_lr:
                sub_volume = numpy.fliplr(sub_volume)
            if flip_ud:
                sub_volume = numpy.flipud(sub_volume)
            return sub_volume

        sub_volumes = [
            get_sub_volume(volume, flip_lr, flip_ud)
            for volume, flip_lr, flip_ud in zip(volumes, flip_lr_arr, flip_ud_arr)
        ]
        # generator on it self: we want to iterate over the y axis
        n_slices_in_bunch = ceil((bunch_end - bunch_start) / step)
        assert isinstance(n_slices_in_bunch, int)
        for i in range(n_slices_in_bunch):
            yield [sub_volume[:, i, :] for sub_volume in sub_volumes]

    class _FinalDatasetContext(AbstractContextManager):
        """Manager to create the data volume and save it (data only !). target: used for volume stitching
        In the case of HDF5 we want to save this directly in the file to avoid
        keeping the full volume in memory.
        Insure also contain processing will be common between the different processing
        """

        def __init__(self, volume: VolumeBase, volume_shape: tuple, dtype: numpy.dtype) -> None:
            super().__init__()
            if not isinstance(volume, VolumeBase):
                raise TypeError(
                    f"Volume is expected to be an instance of {VolumeBase}. {type(volume)} provided instead"
                )

            self._volume = volume
            self._volume_shape = volume_shape
            self.__file_handler = None
            self._dtype = dtype

        def __enter__(self):
            # handle the specific case of HDF5. Goal: avoid getting the full stitched volume in memory
            if isinstance(self._volume, HDF5Volume):
                self.__file_handler = HDF5File(self._volume.data_url.file_path(), mode="a")
                # if need to delete an existing dataset
                if self._volume.overwrite and self._volume.data_path in self.__file_handler:
                    try:
                        del self.__file_handler[self._volume.data_path]
                    except Exception as e:
                        _logger.error(f"Fail to overwrite data. Reason is {e}")
                        data = None
                        self.__file_handler.close()
                        return data

                # create dataset
                try:
                    data = self.__file_handler.create_dataset(
                        self._volume.data_url.data_path(),
                        shape=self._volume_shape,
                        dtype=self._dtype,
                    )
                except Exception as e2:
                    _logger.error(f"Fail to create final dataset. Reason is {e2}")
                    data = None
                    self.__file_handler.close()
            # for other file format: create the full dataset in memory
            else:
                data = numpy.empty(self._volume_shape, dtype=self._dtype)
            return data

        def __exit__(self, *exc):
            if self.__file_handler is not None:
                return self.__file_handler.close()
            else:
                self._volume.save_data()

    class _RawDatasetsContext(AbstractContextManager):
        """
        return volume data for all input volume (target: used for volume stitching).
        If the volume is an HDF5Volume then the HDF5 dataset will be used (on disk)
        If the volume is of another type then it will be loaded in memory then used (more memory consuming)
        """

        def __init__(self, volumes: tuple, alignment_axis_1) -> None:
            super().__init__()
            for volume in volumes:
                if not isinstance(volume, VolumeBase):
                    raise TypeError(
                        f"Volumes are expected to be an instance of {VolumeBase}. {type(volume)} provided instead"
                    )

            self._volumes = volumes
            self.__file_handlers = []
            self._alignment_axis_1 = alignment_axis_1

        @property
        def alignment_axis_1(self):
            return self._alignment_axis_1

        def __enter__(self):
            # handle the specific case of HDF5. Goal: avoid getting the full stitched volume in memory
            datasets = []
            shapes = {volume.get_volume_shape()[1] for volume in self._volumes}
            axis_1_dim = max(shapes)
            axis_1_need_padding = len(shapes) > 1

            try:
                for volume in self._volumes:
                    if volume.data is not None:
                        data = volume.data
                    elif isinstance(volume, HDF5Volume):
                        file_handler = HDF5File(volume.data_url.file_path(), mode="r")
                        dataset = file_handler[volume.data_url.data_path()]
                        data = dataset
                        self.__file_handlers.append(file_handler)
                    # for other file format: load the full dataset in memory
                    else:
                        data = volume.load_data(store=False)
                        if data is None:
                            raise ValueError(f"No data found for volume {volume.get_identifier()}")
                    if axis_1_need_padding:
                        data = self.add_padding(data=data, axis_1_dim=axis_1_dim, alignment=self.alignment_axis_1)
                    datasets.append(data)
            except Exception as e:
                # if some errors happen during loading HDF5
                for file_handled in self.__file_handlers:
                    file_handled.close()
                raise e

            return datasets

        def __exit__(self, *exc):
            success = True
            for file_handler in self.__file_handlers:
                success = success and file_handler.close()
            return success

        def add_padding(self, data: Union[h5py.Dataset, numpy.ndarray], axis_1_dim, alignment: AlignmentAxis1):
            alignment = AlignmentAxis1.from_value(alignment)
            if alignment is AlignmentAxis1.BACK:
                axis_1_pad_width = (axis_1_dim - data.shape[1], 0)
            elif alignment is AlignmentAxis1.CENTER:
                half_width = int((axis_1_dim - data.shape[1]) / 2)
                axis_1_pad_width = (half_width, axis_1_dim - data.shape[1] - half_width)
            elif alignment is AlignmentAxis1.FRONT:
                axis_1_pad_width = (0, axis_1_dim - data.shape[1])
            else:
                raise ValueError(f"alignment {alignment} is not handled")

            return PaddedRawData(
                data=data,
                axis_1_pad_width=axis_1_pad_width,
            )


def stitch_vertically_raw_frames(
    frames: tuple,
    key_lines: tuple,
    overlap_kernels: Union[ZStichOverlapKernel, tuple],
    output_dtype: numpy.dtype = numpy.float32,
    check_inputs=True,
    raw_frames_compositions: Optional[ZFrameComposition] = None,
    overlap_frames_compositions: Optional[ZFrameComposition] = None,
    return_composition_cls=False,
    alignment="center",
    pad_mode="constant",
    new_width: Optional[int] = None,
) -> numpy.ndarray:
    """
    stitches raw frames (already shifted and flat fielded !!!) together using
    raw stitching (no pixel interpolation, y_overlap_in_px is expected to be a int).
    Sttiching is done vertically (along the y axis of the frame ref)

      |    --------------
      |    |            |
      |    |  Frame 1   |                        --------------
      |    |            |                        |  Frame 1    |
      |    --------------                        |             |
    Y |                         --> stitching    |~ stitching ~|
      |    --------------                        |             |
      |    |            |                        |  Frame 2    |
      |    |  Frame 2   |                         --------------
      |    |            |
      |    --------------
      \/

    returns stitched_projection, raw_img_1, raw_img_2, computed_overlap
    proj_0 and pro_1 are already expected to be in a row. Having stitching_height_in_px in common. At top of proj_0
    and at bottom of proj_1

    :param tuple frames: tuple of 2D numpy array. Expected to be Z up oriented at this stage
    :param tuple key_lines: for each jonction define the two lines to overlaid (from the upper and the lower frames). In the reference where 0 is the bottom line of the image.
    :param overlap_kernels: ZStichOverlapKernel overlap kernel to be used or a list of kernel (one per overlap). Define startegy and overlap heights
    :param numpy.dtype output_dtype: dataset dtype. For now must be provided because flat field corrcetion change data type (numpy.float32 for now)
    :param bool check_inputs: if True will do more test on inputs parameters like checking frame shapes, coherence of the request.. As it can be time consuming it is optional
    :param raw_frames_compositions: pre computed raw frame composition. If not provided will compute them. allow providing it to speed up calculation
    :param overlap_frames_compositions: pre computed stitched frame composition. If not provided will compute them. allow providing it to speed up calculation
    :param bool return_frame_compositions: if False return simply the stitched frames. Else return a tuple with stitching frame and the dictionnary with the composition frames...
    """
    assert overlap_kernels is not None, "overlap kernels must be provided"

    if check_inputs:

        def check_frame(proj):
            if not isinstance(proj, numpy.ndarray) and proj.ndim == 2:
                raise ValueError(f"frames are expected to be 2D numpy array")

        [check_frame(frame) for frame in frames]
        for frame_0, frame_1 in zip(frames[:-1], frames[1:]):
            if not (frame_0.ndim == frame_1.ndim == 2):
                raise ValueError("Frames are expected to be 2D")

        for frame_0, frame_1, kernel in zip(frames[:-1], frames[1:], overlap_kernels):
            if frame_0.shape[0] < kernel.overlap_size:
                raise ValueError(
                    f"frame_0 height ({frame_0.shape[0]}) is less than kernel overlap ({kernel.overlap_size})"
                )
            if frame_1.shape[0] < kernel.overlap_size:
                raise ValueError(
                    f"frame_1 height ({frame_1.shape[0]}) is less than kernel overlap ({kernel.overlap_size})"
                )
        if not len(key_lines) == len(overlap_kernels):
            raise ValueError("we expect to have the same number of key_lines then the number of kernel")
        else:
            for key_line in key_lines:
                for value in key_line:
                    if not isinstance(value, (int, numpy.integer)):
                        raise TypeError(f"key_line is expected to be an integer. {type(key_line)} provided")
                    elif value < 0:
                        raise ValueError(f"key lines are expected to be positive values. Get {value} as key line value")

    if new_width is None:
        new_width = max([frame.shape[-1] for frame in frames])
    frames = tuple(
        [
            align_horizontally(
                data=frame,
                alignment=alignment,
                new_width=new_width,
                pad_mode=pad_mode,
            )
            for frame in frames
        ]
    )

    # step 1: create numpy array that will contain stitching
    # if raw composition doesn't exists create it
    if raw_frames_compositions is None:
        raw_frames_compositions = ZFrameComposition.compute_raw_frame_compositions(
            frames=frames,
            overlap_kernels=overlap_kernels,
            key_lines=key_lines,
            stitching_axis=0,
        )
    new_frame_height = raw_frames_compositions.global_end_y[-1] - raw_frames_compositions.global_start_y[0]
    stitched_projection_shape = (
        # here we only handle frames because shift are already done
        int(new_frame_height),
        new_width,
    )
    stitch_array = numpy.empty(stitched_projection_shape, dtype=output_dtype)

    # step 2: set raw data
    # fill stitch array with raw data raw data
    raw_frames_compositions.compose(
        output_frame=stitch_array,
        input_frames=frames,
    )

    # step 3 set stitched data

    # 3.1 create stitched overlaps
    stitched_overlap = []
    for frame_0, frame_1, kernel, key_line in zip(frames[:-1], frames[1:], overlap_kernels, key_lines):
        assert kernel.overlap_size >= 0
        frame_0_overlap, frame_1_overlap = ZStitcher.get_overlap_areas(
            upper_frame=frame_0,
            lower_frame=frame_1,
            upper_frame_key_line=key_line[0],
            lower_frame_key_line=key_line[1],
            overlap_size=kernel.overlap_size,
            stitching_axis=0,
        )

        assert (
            frame_0_overlap.shape[0] == frame_1_overlap.shape[0] == kernel.overlap_size
        ), f"{frame_0_overlap.shape[0]} == {frame_1_overlap.shape[0]} == {kernel.overlap_size}"

        stitched_overlap.append(
            kernel.stitch(
                frame_0_overlap,
                frame_1_overlap,
            )[0]
        )
    # 3.2 fill stitched overlap on output array
    if overlap_frames_compositions is None:
        overlap_frames_compositions = ZFrameComposition.compute_stitch_frame_composition(
            frames=frames,
            overlap_kernels=overlap_kernels,
            key_lines=key_lines,
            stitching_axis=0,
        )
    overlap_frames_compositions.compose(
        output_frame=stitch_array,
        input_frames=stitched_overlap,
    )
    if return_composition_cls:
        return (
            stitch_array,
            {
                "raw_compositon": raw_frames_compositions,
                "overlap_compositon": overlap_frames_compositions,
            },
        )

    return stitch_array


class StitchingPostProcAggregation:
    """
    for remote stitching each process will stitch a part of the volume or projections.
    Then once all are finished we want to aggregate them all to a final volume or NXtomo.

    This is the goal of this class.
    Please be careful with API. This is already inheriting from a tomwer class

    :param ZStitchingConfiguration stitching_config: configuration of the stitching configuration
    :param Optional[tuple] futures: futures that just runned
    :param Optional[tuple] existing_objs: futures that just runned
    :param
    """

    def __init__(
        self,
        stitching_config: ZStitchingConfiguration,
        futures: Optional[tuple] = None,
        existing_objs_ids: Optional[tuple] = None,
    ) -> None:
        if not isinstance(stitching_config, (ZStitchingConfiguration)):
            raise TypeError(f"stitching_config should be an instance of {ZStitchingConfiguration}")
        if not ((existing_objs_ids is None) ^ (futures is None)):
            raise ValueError("Either existing_objs or futures should be provided (can't provide both)")
        self._futures = futures
        self._stitching_config = stitching_config
        self._existing_objs_ids = existing_objs_ids

    @property
    def futures(self):
        # TODO: deprecate it ?
        return self._futures

    def retrieve_tomo_objects(self) -> tuple():
        """
        Return tomo objects to be stitched together. Either from future or from existing_objs
        """
        if self._existing_objs_ids is not None:
            scan_ids = self._existing_objs_ids
        else:
            results = {}
            _logger.info(f"wait for slurm job to be completed")
            for obj_id, future in self.futures.items():
                results[obj_id] = future.result()

            failed = tuple(
                filter(
                    lambda x: x.exception() is not None,
                    self.futures.values(),
                )
            )
            if len(failed) > 0:
                # if some job failed: unseless to do the concatenation
                exceptions = " ; ".join([f"{job} : {job.exception()}" for job in failed])
                raise RuntimeError(f"some job failed. Won't do the concatenation. Exceptiosn are {exceptions}")

            canceled = tuple(
                filter(
                    lambda x: x.cancelled(),
                    self.futures.values(),
                )
            )
            if len(canceled) > 0:
                # if some job canceled: unseless to do the concatenation
                raise RuntimeError(f"some job failed. Won't do the concatenation. Jobs are {' ; '.join(canceled)}")
            scan_ids = results.keys()
        return [TomoscanFactory.create_tomo_object_from_identifier(scan_id) for scan_id in scan_ids]

    def dump_stiching_config_as_nx_process(self, file_path: str, data_path: str, overwrite: bool, process_name: str):
        dict_to_dump = {
            process_name: {
                "config": self._stitching_config.to_dict(),
                "program": "nabu-stitching",
                "version": nabu_version,
                "date": get_datetime(),
            },
            f"{process_name}@NX_class": "NXprocess",
        }

        dicttonx(
            dict_to_dump,
            h5file=file_path,
            h5path=data_path,
            update_mode="replace" if overwrite else "add",
            mode="a",
        )

    @property
    def stitching_config(self) -> ZStitchingConfiguration:
        return self._stitching_config

    def process(self) -> None:
        """
        main function
        """

        # concatenate result
        _logger.info("all job succeeded. Concatenate results")
        if isinstance(self._stitching_config, PreProcessedZStitchingConfiguration):
            # 1: case of a pre-processing stitching
            scans = self.retrieve_tomo_objects()
            nx_tomos = []
            for scan in scans:
                nx_tomos.append(
                    NXtomo().load(
                        file_path=scan.master_file,
                        data_path=scan.entry,
                    )
                )
            final_nx_tomo = NXtomo.concatenate(nx_tomos)
            final_nx_tomo.save(
                file_path=self.stitching_config.output_file_path,
                data_path=self.stitching_config.output_data_path,
                overwrite=self.stitching_config.overwrite_results,
            )

            # dump NXprocess if possible
            parts = self.stitching_config.output_data_path.split("/")
            process_name = parts[-1] + "_stitching"
            if len(parts) < 2:
                data_path = "/"
            else:
                data_path = "/".join(parts[:-1])

            self.dump_stiching_config_as_nx_process(
                file_path=self.stitching_config.output_file_path,
                data_path=data_path,
                process_name=process_name,
                overwrite=self.stitching_config.overwrite_results,
            )

        elif isinstance(self.stitching_config, PostProcessedZStitchingConfiguration):
            # 2: case of a post-processing stitching
            outputs_sub_volumes = self.retrieve_tomo_objects()
            concatenate_volumes(
                output_volume=self.stitching_config.output_volume,
                volumes=tuple(outputs_sub_volumes),
                axis=1,
            )

            if isinstance(self.stitching_config.output_volume, HDF5Volume):
                parts = self.stitching_config.output_volume.metadata_url.data_path().split("/")
                process_name = parts[-1] + "_stitching"
                if len(parts) < 2:
                    data_path = "/"
                else:
                    data_path = "/".join(parts[:-1])

                self.dump_stiching_config_as_nx_process(
                    file_path=self.stitching_config.output_volume.metadata_url.file_path(),
                    data_path=data_path,
                    process_name=process_name,
                    overwrite=self.stitching_config.overwrite_results,
                )
        else:
            raise TypeError(f"stitching_config type ({type(self.stitching_config)}) not handled")


def get_obj_width(obj: Union[NXtomoScan, VolumeBase]) -> int:
    """
    return tomo object width
    """
    if isinstance(obj, NXtomoScan):
        return obj.dim_1
    elif isinstance(obj, VolumeBase):
        return obj.get_volume_shape()[-1]
    else:
        raise TypeError(f"obj type ({type(obj)}) is not handled")
