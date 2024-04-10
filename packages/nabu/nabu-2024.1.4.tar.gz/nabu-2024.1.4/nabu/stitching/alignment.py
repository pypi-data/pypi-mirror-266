import h5py
import numpy
from typing import Union
from silx.utils.enum import Enum as _Enum
from tomoscan.volumebase import VolumeBase
from tomoscan.esrf.volume.hdf5volume import HDF5Volume
from nabu.io.utils import DatasetReader


class AlignmentAxis2(_Enum):
    CENTER = "center"
    LEFT = "left"
    RIGTH = "right"


class AlignmentAxis1(_Enum):
    FRONT = "front"
    CENTER = "center"
    BACK = "back"


def align_horizontally(data: numpy.ndarray, alignment: AlignmentAxis2, new_width: int, pad_mode="constant"):
    """
    Align data horizontally to make sure new data width will ne `new_width`.

    :param numpy.ndarray data: data to align
    :param HAlignment alignment: alignment strategy
    :param int new_width: output data width
    """
    current_width = data.shape[-1]
    alignment = AlignmentAxis2.from_value(alignment)

    if current_width > new_width:
        raise ValueError(f"data.shape[-1] ({data.shape[-1]}) > new_width ({new_width}). Unable to crop data")
    elif current_width == new_width:
        return data
    else:
        if alignment is AlignmentAxis2.CENTER:
            left_width = (new_width - current_width) // 2
            right_width = (new_width - current_width) - left_width
        elif alignment is AlignmentAxis2.LEFT:
            left_width = 0
            right_width = new_width - current_width
        elif alignment is AlignmentAxis2.RIGTH:
            left_width = new_width - current_width
            right_width = 0
        else:
            raise ValueError(f"alignment {alignment.value} is not handled")

        assert left_width >= 0, f"pad width must be positive - left width isn't ({left_width})"
        assert right_width >= 0, f"pad width must be positive - right width isn't ({right_width})"
        return numpy.pad(
            data,
            pad_width=((0, 0), (left_width, right_width)),
            mode=pad_mode,
        )


class PaddedRawData:
    """
    Util class to extend a data when necessary
    Must to aplpy to a volume and to an hdf5dataset - array
    The idea behind is to avoid loading all the data in memory
    """

    def __init__(self, data: Union[numpy.ndarray, h5py.Dataset], axis_1_pad_width: tuple) -> None:
        self._axis_1_pad_width = numpy.array(axis_1_pad_width)
        if not (self._axis_1_pad_width.size == 2 and self._axis_1_pad_width[0] >= 0 and self._axis_1_pad_width[1] >= 0):
            raise ValueError(f"'axis_1_pad_width' expects to positive elements. Get {axis_1_pad_width}")
        self._raw_data = data
        self._raw_data_end = None
        # note: for now we return only frames with zeros for padded frames.
        # in the future we could imagine having a method and miror existing volume or extend the closest frame, or get a mean value...
        self._empty_frame = None
        self._dtype = None
        self._shape = None
        self._raw_data_shape = self.raw_data.shape

    @staticmethod
    def get_empty_frame(shape, dtype):
        return numpy.zeros(
            shape=shape,
            dtype=dtype,
        )

    @property
    def empty_frame(self):
        if self._empty_frame is None:
            self._empty_frame = self.get_empty_frame(
                shape=(self.shape[0], 1, self.shape[2]),
                dtype=self.dtype,
            )
        return self._empty_frame

    @property
    def shape(self):
        if self._shape is None:
            self._shape = tuple(
                (
                    self._raw_data_shape[0],
                    numpy.sum(
                        numpy.array(self._axis_1_pad_width),
                    )
                    + self._raw_data_shape[1],
                    self._raw_data_shape[2],
                )
            )
        return self._shape

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def raw_data_start(self):
        return self._axis_1_pad_width[0]

    @property
    def raw_data_end(self):
        if self._raw_data_end is None:
            self._raw_data_end = self._axis_1_pad_width[0] + self._raw_data_shape[1]
        return self._raw_data_end

    @property
    def dtype(self):
        if self._dtype is None:
            self._dtype = self.raw_data.dtype
        return self._dtype

    def __getitem__(self, args):
        if not isinstance(args, tuple) and len(args) == 3:
            raise ValueError("only handles 3D slicing")
        elif not (args[0] == slice(None, None, None) and args[2] == slice(None, None, None)):
            raise ValueError(
                "slicing only handled along axis 1. First and third tuple item are expected to be empty slice as slice(None, None, None)"
            )
        else:
            if numpy.isscalar(args[1]):
                args = (
                    args[0],
                    slice(args[1], args[1] + 1, 1),
                    args[2],
                )

            start = args[1].start
            if start is None:
                start = 0
            stop = args[1].stop
            if stop is None:
                stop = self.shape[1]
            step = args[1].step
            # some test
            if start < 0 or stop < 0:
                raise ValueError("only positive position are handled")
            if start >= stop:
                raise ValueError("start >= stop")
            if stop > self.shape[1]:
                raise ValueError("stop > self.shape[1]")
            if step not in (1, None):
                raise ValueError("for now PaddedVolume only handles steps of 1")

            first_part_array = None
            if start < self.raw_data_start and (stop - start > 0):
                stop_first_part = min(stop, self.raw_data_start)
                first_part_array = numpy.repeat(self.empty_frame, repeats=stop_first_part - start, axis=1)
                start = stop_first_part

            third_part_array = None
            if stop > self.raw_data_end and (stop - start > 0):
                if stop > self.shape[1]:
                    raise ValueError("requested slice is out of boundaries")
                start_third_part = max(start, self.raw_data_end)
                third_part_array = numpy.repeat(self.empty_frame, repeats=stop - start_third_part, axis=1)
                stop = self.raw_data_end

            if start >= self.raw_data_start and stop >= self.raw_data_start and (stop - start > 0):
                second_part_array = self.raw_data[:, start - self.raw_data_start : stop - self.raw_data_start, :]
            else:
                second_part_array = None

            parts = tuple(filter(lambda a: a is not None, (first_part_array, second_part_array, third_part_array)))
            return numpy.hstack(
                parts,
            )
