import numpy
import pytest

from nabu.stitching.overlap import compute_image_minimum_divergence, compute_image_higher_signal, check_overlaps
from nabu.testutils import get_data


def test_compute_image_minimum_divergence():
    """make sure the compute_image_minimum_divergence function is processing"""
    raw_data_1 = get_data("brain_phantom.npz")["data"]
    raw_data_2 = numpy.random.rand(*raw_data_1.shape) * 255.0

    stitching = compute_image_minimum_divergence(raw_data_1, raw_data_2, high_frequency_threshold=2)
    assert stitching.shape == raw_data_1.shape


def test_compute_image_higher_signal():
    """
    make sure compute_image_higher_signal is processing
    """
    raw_data = get_data("brain_phantom.npz")["data"]
    raw_data_1 = raw_data.copy()
    raw_data_1[40:75] = 0.0
    raw_data_1[:, 210:245] = 0.0

    raw_data_2 = raw_data.copy()
    raw_data_2[:, 100:120] = 0.0

    stitching = compute_image_higher_signal(raw_data_1, raw_data_2)

    numpy.testing.assert_array_equal(
        stitching,
        raw_data,
    )


def test_check_overlaps():
    """test 'check_overlaps' function"""

    # two frames, ordered and with an overlap
    check_overlaps(
        frames=(
            numpy.ones(10),
            numpy.ones(20),
        ),
        positions=((10,), (0,)),
        axis=0,
        raise_error=True,
    )

    # two frames, ordered and without an overlap
    with pytest.raises(ValueError):
        check_overlaps(
            frames=(
                numpy.ones(10),
                numpy.ones(20),
            ),
            positions=((0,), (100,)),
            axis=0,
            raise_error=True,
        )

    # two frames, frame 0 fully overlap frame 1
    with pytest.raises(ValueError):
        check_overlaps(
            frames=(
                numpy.ones(20),
                numpy.ones(10),
            ),
            positions=((8,), (5,)),
            axis=0,
            raise_error=True,
        )

    # three frames 'overlaping' as expected
    check_overlaps(
        frames=(
            numpy.ones(10),
            numpy.ones(20),
            numpy.ones(10),
        ),
        positions=((20,), (10,), (0,)),
        axis=0,
        raise_error=True,
    )

    # three frames: frame 0 overlap frame 1 but also frame 2
    with pytest.raises(ValueError):
        check_overlaps(
            frames=(
                numpy.ones(20),
                numpy.ones(10),
                numpy.ones(10),
            ),
            positions=((20,), (15,), (11,)),
            axis=0,
            raise_error=True,
        )
