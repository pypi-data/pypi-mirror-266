from math import floor, ceil
import numpy as np
from scipy.ndimage import convolve1d

def shift_bilinear2(img, shift, axis=1):
    """
    Shift an image with bilinear interpolation,
    For a translation, the difference between non-interpolated and interpolated coordinates is constant.
    Thus, the bilinear weighting it can be implemented as a convolution operator.
    """
    if img.ndim != 2:
        raise ValueError("Expected 2D image")
    axis = axis % 2
    res = np.zeros_like(img)
    # Extract the integer and fractional parts of the shift
    shift0 = shift
    shift = abs(shift)
    shift_i, shift_f = int(shift), shift - int(shift)
    shift1, shift2 = shift - floor(shift), ceil(shift) - shift

    # Integer shift is simply a slicing operation
    # Fractional shift is a convolution operation
    res_area = slice(shift_i, None)
    img_area = slice(0, -shift_i)
    if shift < 0: # negative shift
        res_area, img_area = img_area, res_area

    slice_all = slice(None, None)
    if axis == 1:
        res_area = (slice_all, res_area)
        img_subset = img[slice_all, img_area]
    else:
        res_area = (res_area, slice_all)
        img_subset = img[img_area, slice_all]

    if shift_f < 1e-4:
        res[res_area] = img_subset
    else:
        res[res_area] = convolve1d(img_subset, [shift1, shift2], axis=axis, mode="reflect")
    return res


