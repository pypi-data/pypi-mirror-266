import math
import numpy as np
from scipy.fftpack import rfft
from numbers import Real
from ..misc import fourier_filters
from .alignment import AlignmentBase, plt, progress_bar, local_fftn, local_ifftn
from ..resources.utils import extract_parameters

# three possible  values for the validity check, which can optionally be returned by the find_shifts methods
cor_result_validity = {
    "unknown": "unknown",
    "sound": "sound",
    "correct": "sound",
    "questionable": "questionable",
}


class CenterOfRotation(AlignmentBase):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        shift_axis: int = -1,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
        cor_options=None,
    ):
        """Find the Center of Rotation (CoR), given two images.

        This method finds the half-shift between two opposite images, by
        means of correlation computed in Fourier space.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

           - L1: distance from source to motor
           - L2: distance from source to detector
           - ps: physical pixel size
           - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        shift_axis: int
            Axis along which we want the shift to be computed. Default is -1 (horizontal).
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        peak_fit_radius: int, optional
            Radius size around the max correlation pixel, for sub-pixel fitting.
            Minimum and default value is 1.
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.


        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotation()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        cc = self._compute_correlation_fft(img_1, img_2, padding_mode, high_pass=high_pass, low_pass=low_pass)
        img_shape = img_2.shape
        cc_vs = np.fft.fftfreq(img_shape[-2], 1 / img_shape[-2])
        cc_hs = np.fft.fftfreq(img_shape[-1], 1 / img_shape[-1])

        (f_vals, fv, fh) = self.extract_peak_region_2d(cc, peak_radius=peak_fit_radius, cc_vs=cc_vs, cc_hs=cc_hs)
        fitted_shifts_vh = self.refine_max_position_2d(f_vals, fv, fh)

        estimated_cor = fitted_shifts_vh[shift_axis] / 2.0

        if isinstance(self.cor_options.get("near_pos", None), (int, float)):
            near_pos = self.cor_options["near_pos"]
            if (
                np.abs(near_pos - estimated_cor) / near_pos > 0.2
            ):  # For comparison, near_pos is RELATIVE (as estimated_cor is).
                validity_check_result = cor_result_validity["questionable"]
            else:
                validity_check_result = cor_result_validity["sound"]
        else:
            validity_check_result = cor_result_validity["unknown"]

        if return_validity:
            return estimated_cor, validity_check_result
        else:
            return estimated_cor


class CenterOfRotationSlidingWindow(CenterOfRotation):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        side,
        window_width=None,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
        cor_options=None,
    ):
        """Semi-automatically find the Center of Rotation (CoR), given two images
        or sinograms. Suitable for half-aquisition scan.

        This method finds the half-shift between two opposite images,  by
        minimizing difference over a moving window.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        side: string
            Expected region of the CoR. Allowed values: 'left', 'center' or 'right'.
        window_width: int, optional
            Width of window that will slide on the other image / part of the
            sinogram. Default is None.
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        peak_fit_radius: int, optional
            Radius size around the max correlation pixel, for sub-pixel fitting.
            Minimum and default value is 1.
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.

        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationSlidingWindow()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        validity_check_result = cor_result_validity["unknown"]

        if side is None:
            raise ValueError("Side should be one of 'left', 'right', or 'center'. 'None' was given instead")

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(
            img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_2 = self._prepare_image(
            img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_shape = img_2.shape

        near_pos = self.cor_options.get("near_pos", None)
        if near_pos is None:
            if window_width is None:
                if side.lower() == "center":
                    window_width = round(img_shape[-1] / 4.0 * 3.0)
                else:
                    window_width = round(img_shape[-1] / 10)
            window_shift = window_width // 2
            window_width = window_shift * 2 + 1

            win_1_start_seed = 0
            # number of pixels where the window will "slide".
            n = img_shape[-1] - window_width
        else:
            abs_pos = near_pos + img_shape[-1] // 2
            offset = min(img_shape[-1] - abs_pos, abs_pos)  # distance to closest edge.

            window_fraction = 0.4  # Hard-coded ?
            window_shift = int(np.floor(offset * window_fraction))
            window_width = 2 * window_shift + 1

            sliding_shift = int(np.floor(offset * (1 - window_fraction))) - 1
            n = 2 * sliding_shift + 1
            win_1_start_seed = 2 * near_pos - sliding_shift

        if side.lower() == "right":
            win_2_start = 0
        elif side.lower() == "left":
            win_2_start = img_shape[-1] - window_width
        elif side.lower() == "center":
            win_2_start = img_shape[-1] // 2 - window_shift
        else:
            raise ValueError(
                "Side should be one of 'left', 'right', or 'center'. '%s' was given instead" % side.lower()
            )

        win_2_end = win_2_start + window_width

        diffs_mean = np.zeros((n,), dtype=img_1.dtype)
        diffs_std = np.zeros((n,), dtype=img_1.dtype)

        for ii in progress_bar(range(n), verbose=self.verbose):
            win_1_start = win_1_start_seed + ii
            win_1_end = win_1_start + window_width
            img_diff = img_1[:, win_1_start:win_1_end] - img_2[:, win_2_start:win_2_end]
            diffs_abs = np.abs(img_diff)
            diffs_mean[ii] = diffs_abs.mean()
            diffs_std[ii] = diffs_abs.std()

        diffs_mean = diffs_mean.min() - diffs_mean
        win_ind_max = np.argmax(diffs_mean)

        diffs_std = diffs_std.min() - diffs_std
        if not win_ind_max == np.argmax(diffs_std):
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]
        else:
            validity_check_result = cor_result_validity["sound"]

        (f_vals, f_pos) = self.extract_peak_regions_1d(diffs_mean, peak_radius=peak_fit_radius)
        win_pos_max, win_val_max = self.refine_max_position_1d(f_vals, return_vertex_val=True)

        # Derive the COR
        if isinstance(near_pos, Real):
            cor_h = -(win_2_start - (win_1_start_seed + win_ind_max + win_pos_max)) / 2.0
            cor_pos = -(win_2_start - (win_1_start_seed + np.arange(n))) / 2.0
        else:
            cor_h = -(win_2_start - (win_ind_max + win_pos_max)) / 2.0
            cor_pos = -(win_2_start - np.arange(n)) / 2.0

        if (side.lower() == "right" and win_ind_max == 0) or (side.lower() == "left" and win_ind_max == n):
            self.logger.warning("Sliding window width %d might be too large!" % window_width)

        if self.verbose:
            print("Lowest difference window: index=%d, range=[0, %d]" % (win_ind_max, n))
            print("CoR tested for='%s', found at voxel=%g (from center)" % (side, cor_h))

            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.stem(cor_pos, diffs_mean, label="Mean difference")
            ax.stem(cor_h, win_val_max, linefmt="C1-", markerfmt="C1o", label="Best mean difference")
            ax.stem(cor_pos, -diffs_std, linefmt="C2-", markerfmt="C2o", label="Std-dev difference")
            ax.set_title("Window dispersions")
            plt.legend()
            plt.show(block=False)

        if return_validity:
            return cor_h, validity_check_result
        else:
            return cor_h


class CenterOfRotationGrowingWindow(CenterOfRotation):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        side="all",
        min_window_width=11,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
    ):
        """Automatically find the Center of Rotation (CoR), given two images or
        sinograms. Suitable for half-aquisition scan.

        This method finds the half-shift between two opposite images,  by
        minimizing difference over a moving window.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        side: string, optional
            Expected region of the CoR. Allowed values: 'left', 'center', 'right', or 'all'.
            Default is 'all'.
        min_window_width: int, optional
            Minimum window width that covers the common region of the two images /
            sinograms. Default is 11.
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        peak_fit_radius: int, optional
            Radius size around the max correlation pixel, for sub-pixel fitting.
            Minimum and default value is 1.
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.



        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationGrowingWindow()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        validity_check_result = cor_result_validity["unknown"]

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(
            img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_2 = self._prepare_image(
            img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_shape = img_2.shape

        def window_bounds(mid_point, window_max_width=img_shape[-1]):
            return (
                np.fmax(np.ceil(mid_point - window_max_width / 2), 0).astype(np.intp),
                np.fmin(np.ceil(mid_point + window_max_width / 2), img_shape[-1]).astype(np.intp),
            )

        img_lower_half_size = np.floor(img_shape[-1] / 2).astype(np.intp)
        img_upper_half_size = np.ceil(img_shape[-1] / 2).astype(np.intp)

        use_estimate_from_motor = "near_pos" in self.cor_options.keys() and isinstance(
            self.cor_options["near_pos"], (int, float)
        )
        use_estimate_from_motor = False  # Not yet implemented.
        if use_estimate_from_motor:
            near_pos = self.cor_options["near_pos"]

        else:
            if side.lower() == "right":
                win_1_mid_start = img_lower_half_size
                win_1_mid_end = np.floor(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
                win_2_mid_start = -img_upper_half_size + min_window_width
                win_2_mid_end = img_upper_half_size
            elif side.lower() == "left":
                win_1_mid_start = -img_lower_half_size + min_window_width
                win_1_mid_end = img_lower_half_size
                win_2_mid_start = img_upper_half_size
                win_2_mid_end = np.ceil(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
            elif side.lower() == "center":
                win_1_mid_start = 0
                win_1_mid_end = img_shape[-1]
                win_2_mid_start = 0
                win_2_mid_end = img_shape[-1]
            elif side.lower() == "all":
                win_1_mid_start = -img_lower_half_size + min_window_width
                win_1_mid_end = np.floor(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
                win_2_mid_start = -img_upper_half_size + min_window_width
                win_2_mid_end = np.ceil(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
            else:
                raise ValueError(
                    "Side should be one of 'left', 'right', or 'center'. '%s' was given instead" % side.lower()
                )

        n1 = win_1_mid_end - win_1_mid_start
        n2 = win_2_mid_end - win_2_mid_start

        if not n1 == n2:
            raise ValueError(
                "Internal error: the number of window steps for the two images should be the same."
                + "Found the following configuration instead => Side: %s, #1: %d, #2: %d" % (side, n1, n2)
            )

        diffs_mean = np.zeros((n1,), dtype=img_1.dtype)
        diffs_std = np.zeros((n1,), dtype=img_1.dtype)

        for ii in progress_bar(range(n1), verbose=self.verbose):
            win_1 = window_bounds(win_1_mid_start + ii)
            win_2 = window_bounds(win_2_mid_end - ii)
            img_diff = img_1[:, win_1[0] : win_1[1]] - img_2[:, win_2[0] : win_2[1]]
            diffs_abs = np.abs(img_diff)
            diffs_mean[ii] = diffs_abs.mean()
            diffs_std[ii] = diffs_abs.std()

        diffs_mean = diffs_mean.min() - diffs_mean
        win_ind_max = np.argmax(diffs_mean)

        diffs_std = diffs_std.min() - diffs_std
        if not win_ind_max == np.argmax(diffs_std):
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]
        else:
            validity_check_result = cor_result_validity["sound"]

        (f_vals, f_pos) = self.extract_peak_regions_1d(diffs_mean, peak_radius=peak_fit_radius)
        win_pos_max, win_val_max = self.refine_max_position_1d(f_vals, return_vertex_val=True)

        cor_h = (win_1_mid_start + (win_ind_max + win_pos_max) - img_upper_half_size) / 2.0

        if (side.lower() == "right" and win_ind_max == 0) or (side.lower() == "left" and win_ind_max == n1):
            self.logger.warning("Minimum growing window width %d might be too large!" % min_window_width)

        if self.verbose:
            cor_pos = (win_1_mid_start + np.arange(n1) - img_upper_half_size) / 2.0

            self.logger.info("Lowest difference window: index=%d, range=[0, %d]" % (win_ind_max, n1))
            self.logger.info("CoR tested for='%s', found at voxel=%g (from center)" % (side, cor_h))

            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.stem(cor_pos, diffs_mean, label="Mean difference")
            ax.stem(cor_h, win_val_max, linefmt="C1-", markerfmt="C1o", label="Best mean difference")
            ax.stem(cor_pos, -diffs_std, linefmt="C2-", markerfmt="C2o", label="Std-dev difference")
            ax.set_title("Window dispersions")
            plt.show(block=False)

        if return_validity:
            return cor_h, validity_check_result
        else:
            return cor_h


class CenterOfRotationAdaptiveSearch(CenterOfRotation):
    """This adaptive method works by applying a gaussian which highlights, by apodisation, a region
    which can possibly contain the good center of rotation.
    The whole image is spanned during several applications of the apodisation. At each application
    the apodisation function, which is a gaussian, is moved to a new guess position.
    The lenght of the step, by which the gaussian is moved, and its sigma are
    obtained by multiplying the shortest distance from the left or right border with
    a self.step_fraction and  self.sigma_fraction factors which ensure global overlapping.
    for each step a region around the CoR  of each image is selected, and the regions of the two images
    are compared to  calculate a cost function. The value of the cost function, at its minimum
    is used to select the best step at which the CoR is taken as final result.
    The option filtered_cost= True (default) triggers the filtering (according to low_pass and high_pass)
    of the two images which are used for he cost function. ( Note: the low_pass and high_pass options
    are used, if given, also without the filtered_cost option, by being passed to the base class
    CenterOfRotation )
    """

    sigma_fraction = 1.0 / 4.0
    step_fraction = 1.0 / 6.0

    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        high_pass=None,
        low_pass=None,
        margins=None,
        filtered_cost=True,
        return_validity=False,
    ):
        """Find the Center of Rotation (CoR), given two images.

        This method finds the half-shift between two opposite images, by
        means of correlation computed in Fourier space.
        A global search is done on on the detector span (minus a margin) without assuming centered scan conditions.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        low_pass: float or sequence of two floats.
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`.
        margins:  None or a couple of floats or ints
            if margins is None or in the form of  (margin1,margin2) the search is done between margin1 and  dim_x-1-margin2.
            If left to None then by default (margin1,margin2)  = ( 10, 10 ).
        filtered_cost: boolean.
            True by default. It triggers the use of filtered images in the calculation of the cost function.
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.

        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationAdaptiveSearch()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3), high_pass=20, low_pass=1   )
        """

        validity_check_result = cor_result_validity["unknown"]

        self._check_img_pair_sizes(img_1, img_2)

        used_type = img_1.dtype

        roi_yxhw = self._determine_roi(img_1.shape, roi_yxhw)

        if filtered_cost and (low_pass is not None or high_pass is not None):
            img_filter = fourier_filters.get_bandpass_filter(
                img_1.shape[-2:],
                cutoff_lowpass=low_pass,
                cutoff_highpass=high_pass,
                use_rfft=True,
                data_type=self.data_type,
            )
            # fft2 and iff2 use axes=(-2, -1) by default
            img_filtered_1 = local_ifftn(local_fftn(img_1, axes=(-2, -1)) * img_filter, axes=(-2, -1)).real
            img_filtered_2 = local_ifftn(local_fftn(img_2, axes=(-2, -1)) * img_filter, axes=(-2, -1)).real
        else:
            img_filtered_1 = img_1
            img_filtered_2 = img_2

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        img_filtered_1 = self._prepare_image(img_filtered_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_filtered_2 = self._prepare_image(img_filtered_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        dim_radio = img_1.shape[1]

        if margins is None:
            lim_1, lim_2 = 10, dim_radio - 1 - 10
        else:
            lim_1, lim_2 = margins
            lim_2 = dim_radio - 1 - lim_2

        if lim_1 < 1:
            lim_1 = 1
        if lim_2 > dim_radio - 2:
            lim_2 = dim_radio - 2

        if lim_2 <= lim_1:
            message = (
                "Image shape or cropped selection too small for global search."
                + " After removal of the margins the search limits collide."
                + " The cropped size is %d\n" % (dim_radio)
            )
            raise ValueError(message)

        found_centers = []
        x_cor = lim_1
        while x_cor < lim_2:
            tmp_sigma = (
                min(
                    (img_1.shape[1] - x_cor),
                    (x_cor),
                )
                * self.sigma_fraction
            )

            tmp_x = (np.arange(img_1.shape[1]) - x_cor) / tmp_sigma
            apodis = np.exp(-tmp_x * tmp_x / 2.0)

            x_cor_rel = x_cor - (img_1.shape[1] // 2)

            img_1_apodised = img_1 * apodis

            try:
                cor_position = CenterOfRotation.find_shift(
                    self,
                    img_1_apodised.astype(used_type),
                    img_2.astype(used_type),
                    low_pass=low_pass,
                    high_pass=high_pass,
                    roi_yxhw=roi_yxhw,
                )
            except ValueError as err:
                if "positions are outside the input margins" in str(err):
                    x_cor = min(x_cor + x_cor * self.step_fraction, x_cor + (dim_radio - x_cor) * self.step_fraction)
                    continue
            except:
                message = "Unexpected error from base class CenterOfRotation.find_shift in CenterOfRotationAdaptiveSearch.find_shift  : {err}".format(
                    err=err
                )
                self.logger.error(message)
                raise

            p_1 = cor_position * 2
            if cor_position < 0:
                p_2 = img_2.shape[1] + cor_position * 2
            else:
                p_2 = -img_2.shape[1] + cor_position * 2

            if abs(x_cor_rel - p_1 / 2) < abs(x_cor_rel - p_2 / 2):
                cor_position = p_1 / 2
            else:
                cor_position = p_2 / 2

            cor_in_img = img_1.shape[1] // 2 + cor_position
            tmp_sigma = (
                min(
                    (img_1.shape[1] - cor_in_img),
                    (cor_in_img),
                )
                * self.sigma_fraction
            )

            M1 = int(round(cor_position + img_1.shape[1] // 2)) - int(round(tmp_sigma))
            M2 = int(round(cor_position + img_1.shape[1] // 2)) + int(round(tmp_sigma))

            piece_1 = img_filtered_1[:, M1:M2]
            piece_2 = img_filtered_2[:, img_1.shape[1] - M2 : img_1.shape[1] - M1]

            if piece_1.size and piece_2.size:
                piece_1 = piece_1 - piece_1.mean()
                piece_2 = piece_2 - piece_2.mean()
                energy = np.array(piece_1 * piece_1 + piece_2 * piece_2, "d").sum()
                diff_energy = np.array((piece_1 - piece_2) * (piece_1 - piece_2), "d").sum()
                cost = diff_energy / energy

                if not np.isnan(cost):
                    if tmp_sigma * 2 > abs(x_cor_rel - cor_position):
                        found_centers.append([cost, abs(x_cor_rel - cor_position), cor_position, energy])

            x_cor = min(x_cor + x_cor * self.step_fraction, x_cor + (dim_radio - x_cor) * self.step_fraction)

        if len(found_centers) == 0:
            message = "Unable to find any valid CoR candidate in {my_class}.find_shift ".format(
                my_class=self.__class__.__name__
            )
            raise ValueError(message)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Now build the neigborhood of the minimum as a list of five elements:
        # the minimum in the middle of the two before, and the two after

        filtered_found_centers = []
        for i in range(len(found_centers)):
            if i > 0:
                if abs(found_centers[i][2] - found_centers[i - 1][2]) < 0.5:
                    filtered_found_centers.append(found_centers[i])
                    continue
            if i + 1 < len(found_centers):
                if abs(found_centers[i][2] - found_centers[i + 1][2]) < 0.5:
                    filtered_found_centers.append(found_centers[i])
                    continue

        if len(filtered_found_centers):
            found_centers = filtered_found_centers

        min_choice = min(found_centers)
        index_min_choice = found_centers.index(min_choice)
        min_neighborood = [
            found_centers[i][2] if (i >= 0 and i < len(found_centers)) else math.nan
            for i in range(index_min_choice - 2, index_min_choice + 2 + 1)
        ]

        score_right = 0
        for i_pos in [3, 4]:
            if abs(min_neighborood[i_pos] - min_neighborood[2]) < 0.5:
                score_right += 1
            else:
                break

        score_left = 0
        for i_pos in [1, 0]:
            if abs(min_neighborood[i_pos] - min_neighborood[2]) < 0.5:
                score_left += 1
            else:
                break

        if score_left + score_right >= 2:
            validity_check_result = cor_result_validity["sound"]
        else:
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # An informative message in case one wish to look at how it has gone
        informative_message = " ".join(
            ["CenterOfRotationAdaptiveSearch found this neighborood of the optimal position:"]
            + [str(t) if not math.isnan(t) else "N.A." for t in min_neighborood]
        )
        self.logger.debug(informative_message)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The return value is the optimum which had been placed in the middle of the neighborood
        cor_position = min_neighborood[2]

        if return_validity:
            return cor_position, validity_check_result
        else:
            return cor_position

    __call__ = find_shift


class CenterOfRotationFourierAngles(CenterOfRotation):
    """This CoR estimation algo is proposed by V. Valls (BCU). It is based on the Fourier
    transform of the columns on the sinogram.
    It requires an initial guesss of the CoR wich is retrieved from
    dataset_info.dataset_scanner.estimated_cor_from_motor. It is assumed in mm and pixel size in um.
    Options are (for the moment) hard-coded in the SinoCORFinder.cor_finder.extra_options dict.
    """

    _default_cor_options = {
        "crop_around_cor": False,
        "side": "center",
        "near_pos": None,
        "near_std": 100,
        "near_width": 20,
        "near_shape": "tukey",
        "near_weight": 0.1,
        "near_alpha": 0.5,
        "shift_sino": True,
        "near_step": 0.5,
        "refine": False,
    }

    def _freq_radio(self, sinos, ifrom, ito):
        size = (sinos.shape[0] + sinos.shape[0] % 2) // 2
        fs = np.empty((size, sinos.shape[1]))
        for i in range(ifrom, ito):
            line = sinos[:, i]
            f_signal = rfft(line)
            f = np.abs(f_signal[: (f_signal.size - 1) // 2 + 1])
            f2 = np.abs(f_signal[(f_signal.size - 1) // 2 + 1 :][::-1])
            if len(f) > len(f2):
                f[1:] += f2
            else:
                f[0:] += f2
            fs[:, i] = f
        with np.errstate(divide="ignore", invalid="ignore", under="ignore"):
            fs = np.log(fs)
        return fs

    def gaussian(self, p, x):
        return p[3] + p[2] * np.exp(-((x - p[0]) ** 2) / (2 * p[1] ** 2))

    def tukey(self, p, x):
        pos, std, alpha, height, background = p
        alpha = np.clip(alpha, 0, 1)
        pi = np.pi
        inv_alpha = 1 - alpha
        width = std / (1 - alpha * 0.5)
        xx = (np.abs(x - pos) - (width * 0.5 * inv_alpha)) / (width * 0.5 * alpha)
        xx = np.clip(xx, 0, 1)
        return (0.5 + np.cos(pi * xx) * 0.5) * height + background

    def sinlet(self, p, x):
        std = p[1] * 2.5
        lin = np.maximum(0, std - np.abs(p[0] - x)) * 0.5 * np.pi / std
        return p[3] + p[2] * np.sin(lin)

    def _px(self, detector_width, abs_pos, near_std):
        sym_range = None
        if abs_pos is not None:
            if self.cor_options["crop_around_cor"]:
                sym_range = int(abs_pos - near_std * 2), int(abs_pos + near_std * 2)

        window = self.cor_options["near_width"]
        if sym_range is not None:
            xx_from = max(window, sym_range[0])
            xx_to = max(xx_from, min(detector_width - window, sym_range[1]))
            if xx_from == xx_to:
                sym_range = None
        if sym_range is None:
            xx_from = window
            xx_to = detector_width - window

        xx = np.arange(xx_from, xx_to, self.cor_options["near_step"])

        return xx

    def _symmetry_correlation(self, px, array, angles):
        window = self.cor_options["near_width"]
        if self.cor_options["shift_sino"]:
            shift_index = np.argmin(np.abs(angles - np.pi)) - np.argmin(np.abs(angles - 0))
        else:
            shift_index = None
        px_from = int(px[0])
        px_to = int(np.ceil(px[-1]))
        f_coef = np.empty(len(px))
        f_array = self._freq_radio(array, px_from - window, px_to + window)
        if shift_index is not None:
            shift_array = np.empty(array.shape, dtype=array.dtype)
            shift_array[0 : len(shift_array) - shift_index, :] = array[shift_index:, :]
            shift_array[len(shift_array) - shift_index :, :] = array[:shift_index, :]
            f_shift_array = self._freq_radio(shift_array, px_from - window, px_to + window)
        else:
            f_shift_array = f_array

        for j, x in enumerate(px):
            i = int(np.floor(x))
            if x - i > 0.4:  # TO DO : Specific to near_step = 0.5?
                f_left = f_array[:, i - window : i]
                f_right = f_shift_array[:, i + 1 : i + window + 1][:, ::-1]
            else:
                f_left = f_array[:, i - window : i]
                f_right = f_shift_array[:, i : i + window][:, ::-1]
            with np.errstate(divide="ignore", invalid="ignore"):
                f_coef[j] = np.sum(np.abs(f_left - f_right))
        return f_coef

    def _cor_correlation(self, px, abs_pos, near_std):
        if abs_pos is not None:
            signal = self.cor_options["near_shape"]
            weight = self.cor_options["near_weight"]
            alpha = self.cor_options["near_alpha"]
            if signal == "sinlet":
                coef = self.sinlet((abs_pos, near_std, -weight, 1), px)
            elif signal == "gaussian":
                coef = self.gaussian((abs_pos, near_std, -weight, 1), px)
            elif signal == "tukey":
                coef = self.tukey((abs_pos, near_std * 2, alpha, -weight, 1), px)
            else:
                raise ValueError("Shape unsupported")
        else:
            coef = np.ones_like(px)
        return coef

    def find_shift(
        self,
        img_1,
        img_2,
        angles,
        side,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
    ):
        sinos = np.vstack([img_1, np.fliplr(img_2).copy()])
        detector_width = sinos.shape[1]

        increment = np.abs(angles[0] - angles[1])
        if np.abs(angles[0] - angles[-1]) < (360 - 0.5) * np.pi / 180 - increment:
            self.logger.warning("Not enough angles, estimator skipped")
            return None

        near_pos = self.cor_options.get("near_pos", None)  # A RELATIVE estimation of the COR

        # Default coarse estimate to center of detector
        # if no one is given either in NX or by user.
        if near_pos is None:
            self.logger.warning("No initial guess was found (from metadata or user) for CoR")
            self.logger.warning("Setting initial guess to center of detector.")
            if side == "center":
                abs_pos = detector_width // 2
            elif side == "left":
                abs_pos = detector_width // 4
            elif side == "right":
                abs_pos = detector_width * 3 // 4
            elif side == "near":
                abs_pos = detector_width // 2
            else:
                raise ValueError(f"side '{side}' is not handled")
        elif isinstance(near_pos, (int, float)):  # Convert RELATIVE to ABSOLUTE position
            abs_pos = near_pos + detector_width / 2

        near_std = None
        if abs_pos is not None:
            near_std = self.cor_options["near_std"]

        px = self._px(detector_width, abs_pos, near_std)

        coef_f = self._symmetry_correlation(
            px,
            sinos,
            angles,
        )
        coef_p = self._cor_correlation(px, abs_pos, near_std)
        coef = coef_f * coef_p

        if len(px) > 0:
            if self.cor_options["refine"]:
                f_vals, f_pos = self.extract_peak_regions_1d(-coef, peak_radius=20, cc_coords=px)
                cor, _ = self.refine_max_position_1d(f_vals, fx=f_pos, return_vertex_val=True)
            else:
                cor = px[np.argmin(coef)]
            cor = cor - detector_width / 2
        else:
            cor = None

        return cor

    __call__ = find_shift


class CenterOfRotationOctaveAccurate(AlignmentBase):
    """This is a Python implementation of Octave/fastomo3/accurate COR estimator.
    The Octave 'accurate' function is renamed `local_correlation`.
    The Nabu standard `find_shift` has the same API as the other COR estimators (sliding, growing...)

    The class inherits directly from AlignmentBase.
    """

    _default_cor_options = {
        "maxsize": [5, 5],
        "refine": None,
        "pmcc": False,
        "normalize": True,
        "low_pass": 0.01,
        "limz": 0.5,
    }

    def _cut(self, im, nrows, ncols, new_center_row=None, new_center_col=None):
        """Cuts a sub-matrix out of a larger matrix.
        Cuts in the center of the original matrix, except if new center is specified
        NO CHECKING of validity indices sub-matrix!

        Parameters
        ----------
        im : array.
            Original matrix
        nrows : int
            Number of rows in the output matrix.
        ncols : int
            Number of columns in the output matrix.
        new_center_row : int
            Index of center row around which to cut (default: None, i.e. center)
        new_center_col : int
            Index of center column around which to cut (default: None, i.e. center)

        Returns
        -------
        nrows x ncols array.

        Examples
        --------
        im_roi = cut(im, 1024, 1024)                -> cut center 1024x1024 pixels
        im_roi = cut(im, 1024, 1024, 600.5, 700.5)  -> cut 1024x1024 pixels around pixels (600-601, 700-701)

        Author: P. Cloetens <cloetens@esrf.eu>
        2023-11-06 J. Lesaint <jerome.lesaint@esrf.fr>

        * See octave-archive for the original Octave code.
        * 2023-11-06: Python implementation. Comparison seems OK.
        """
        [n, m] = im.shape
        if new_center_row is None:
            new_center_row = (n + 1) / 2
        if new_center_col is None:
            new_center_col = (m + 1) / 2

        rb = int(np.round(0.5 + new_center_row - nrows / 2))
        rb = int(np.round(new_center_row - nrows / 2))
        re = int(nrows + rb)
        cb = int(np.round(0.5 + new_center_col - ncols / 2))
        cb = int(np.round(new_center_col - ncols / 2))
        ce = int(ncols + cb)

        return im[rb:re, cb:ce]

    def _checkifpart(self, rapp, rapp_hist):
        res = 0
        for k in range(rapp_hist.shape[0]):
            if np.allclose(rapp, rapp_hist[k, :]):
                res = 1
                return res
        return res

    def _interpolate(self, input, shift, mode="mean", interpolation_method="linear"):
        """Applies to the input a translation by a vector `shift`. Based on
        `scipy.ndimage.affine_transform` function.
        JL: This Octave function was initially used in the refine clause of the local_correlation (Octave find_shift).
        Since find_shift is always called with refine=False in Octave, refine is not implemented (see local_interpolation())
        and this function becomes useless.

        Parameters
        ----------
        input : array
            Array to which the translation is applied.
        shift : tuple, list or array of length 2.
        mode : str
            Type of padding applied to the unapplicable areas of the output image.
            Default `mean` is a constant padding with the mean of the input array.
            `mode` must belong to 'reflect', 'grid-mirror', 'constant', 'grid-constant', 'nearest', 'mirror', 'grid-wrap', 'wrap'
            See `scipy.ndimage.affine_transform` for details.
        interpolation_method : str or int.
            The interpolation is based on spline interpolation.
            Either 0, 1, 2, 3, 4 or 5: order of the spline interpolation functions.
            Or one among 'linear','cubic','pchip','nearest','spline' (Octave legacy).
                'nearest' is equivalent to 0
                'linear' is equivalent to 1
                'cubic','pchip','spline' are equivalent to 3.
        """
        admissible_modes = (
            "reflect",
            "grid-mirror",
            "constant",
            "grid-constant",
            "nearest",
            "mirror",
            "grid-wrap",
            "wrap",
        )
        admissible_interpolation_methods = ("linear", "cubic", "pchip", "nearest", "spline")

        from scipy.ndimage import affine_transform

        [s0, s1] = shift
        matrix = np.zeros([2, 3], dtype=float)
        matrix[0, 0] = 1.0
        matrix[1, 1] = 1.0
        matrix[:, 2] = [-s0, -s1]  # JL: due to transf. convention diff in Octave and scipy (push fwd vs pull back)

        if interpolation_method == "nearest":
            order = 0
        elif interpolation_method == "linear":
            order = 1
        elif interpolation_method in ("pchip", "cubic", "spline"):
            order = 3
        elif interpolation_method in (0, 1, 2, 3, 4, 5):
            order = interpolation_method
        else:
            raise ValueError(
                f"Interpolation method is {interpolation_method} and should either an integer between 0 (inc.) and 5 (inc.) or in {admissible_interpolation_methods}."
            )

        if mode == "mean":
            mode = "constant"
            cval = input.mean()
            return affine_transform(input, matrix, mode=mode, order=order, cval=cval)
        elif mode not in admissible_modes:
            raise ValueError(f"Pad method is {mode} and should be in {admissible_modes}.")

        return affine_transform(input, matrix, mode=mode, order=order)

    def _local_correlation(
        self,
        z1,
        z2,
        maxsize=[5, 5],
        cor_estimate=[0, 0],
        refine=None,
        pmcc=False,
        normalize=True,
    ):
        """Returns the 2D shift in pixels between two images.
        It looks for a local optimum around the initial shift cor_estimate
        and within a window 'maxsize'.
        It uses variance of the difference of the normalized images or PMCC
        It adapts the shift estimate in case optimum is at the edge of the window
        If 'maxsize' is set to 0, it will only use approximate shift (+ refine possibly)
        Set 'cor_estimate' to allow for the use of any initial shift estimation.

        When not successful (stuck in loop or edge reached), returns [nan nan]
        Positive values corresponds to moving z2 to higher values of the index
        to compensate drift: interpolate(f)(z2, row, column)

        Parameters
        ----------
        z1,z2 : 2D arrays.
            The two (sub)images to be compared.

        maxsize : 2-list. Default [5,5]
            Size of the search window.

        cor_estimate:
            Initial guess of the center of rotation.

        refine: Boolean or None (default is None)
            Wether the initial guess should be refined of not.

        pmcc: Boolean (default is False)
            Use Pearson correlation coefficient  i.o. variance.

        normalize: Boolean (default is True)
            Set mean of each image to 1 if True.

        Returns
        -------
        c = [row,column] (or [NaN,NaN] if unsuccessful.)

        2007-01-05 P. Cloetens cloetens@esrf.eu
        * Initial revision
        2023-11-10 J. Lesaint jerome.lesaint@esrf.fr
        * Python conversion.
        """

        if type(maxsize) in (float, int):
            maxsize = [int(maxsize), int(maxsize)]
        elif type(maxsize) in (tuple, list):
            maxsize = [int(maxsize[0]), int(maxsize[1])]
        elif maxsize in ([], None, ""):
            maxsize = [5, 5]

        if refine is None:
            refine = np.allclose(maxsize, 0.0)

        if normalize:
            z1 /= np.mean(z1)
            z2 /= np.mean(z2)

        #####################################
        # JL : seems useless since func is always called with a first approximate.
        ## determination of approximative shift (manually or Fourier correlation)
        # if isinstance(cor_estimate,str):
        #    if cor_estimate in ('fft','auto','fourier'):
        #        padding_mode = None
        #        cor_estimate = self._compute_correlation_fft(
        #            z1,
        #            z2,
        #            padding_mode,
        #            high_pass=self.high_pass,
        #            low_pass=self.low_pass
        #        )
        #    elif cor_estimate in ('manual','man','m'):
        #        cor_estimate = None
        #        # No ImageJ plugin here :
        #        # rapp = ij_align(z1,z2)

        ####################################
        # check if refinement with realspace correlation is required
        # otherwise keep result as it is
        if np.allclose(maxsize, 0):
            shiftfound = 1
            if refine:
                c = np.round(np.array(cor_estimate, dtype=int))
            else:
                c = np.array(cor_estimate, dtype=int)
        else:
            shiftfound = 0
            cor_estimate = np.round(np.array(cor_estimate, dtype=int))

        rapp_hist = []
        if np.sum(np.abs(cor_estimate) + 1 >= z1.shape):
            self.logger.info(f"Approximate shift of [{cor_estimate[0]},{cor_estimate[1]}] is too large, setting [0 0]")
            cor_estimate = np.array([0, 0])
        maxsize = np.minimum(maxsize, np.floor((np.array(z1.shape) - 1) / 2)).astype(int)
        maxsize = np.minimum(maxsize, np.array(z1.shape) - np.abs(cor_estimate) - 1).astype(int)

        while not shiftfound:
            # Set z1 region
            # Rationale: the (shift[0]+maxsize[0]:,shift[1]+maxsize[1]:) block of z1 should match
            # the (maxsize[0]:,maxisze[1]:)-upper-left corner of z2.
            # We first extract this z1 block.
            # Then, take moving z2-block according to maxsize.
            # Of course, care must be taken with borders, hence the various max,min calls.

            # Extract the reference block
            shape_ar = np.array(z1.shape)
            cor_ar = np.array(cor_estimate)
            maxsize_ar = np.array(maxsize)

            z1beg = np.maximum(cor_ar + maxsize_ar, np.zeros(2, dtype=int))
            z1end = shape_ar + np.minimum(cor_ar - maxsize_ar, np.zeros(2, dtype=int))

            z1p = z1[z1beg[0] : z1end[0], z1beg[1] : z1end[1]].flatten()

            # Build local correlations array.
            window_shape = (2 * int(maxsize[0]) + 1, 2 * int(maxsize[1]) + 1)
            cc = np.zeros(window_shape)

            # Prepare second block indices
            z2beg = (cor_ar + maxsize_ar > 0) * cc.shape + (cor_ar + maxsize_ar <= 0) * (shape_ar - z1end + z1beg) - 1
            z2end = z2beg + z1end - z1beg

            if pmcc:
                std_z1p = z1p.std()
            if normalize == 2:
                z1p /= z1p.mean()

            for k in range(cc.shape[0]):
                for l in range(cc.shape[1]):
                    if pmcc:
                        z2p = z2[z2beg[0] - k : z2end[0] - k, z2beg[1] - l : z2end[1] - l].flatten()
                        std_z2p = z2p.std()
                        cc[k, l] = -np.cov(z1p, z2p, rowvar=True)[1, 0] / (std_z1p * std_z2p)
                    else:
                        if normalize == 2:
                            z2p = z2[z2beg[0] - k : z2end[0] - k, z2beg[1] - l : z2end[1] - l].flatten()
                            z2p /= z2p.mean()
                            z2p -= z1p
                        else:
                            z2p = z2[z2beg[0] - k : z2end[0] - k, z2beg[1] - l : z2end[1] - l].flatten()
                            z2p -= z1p
                        cc[k, l] = ((z2p - z2p.mean()) ** 2).sum()
                        # cc(k,l) = std(z1p./z2(z2beg(1)-k:z2end(1)-k,z2beg(2)-l:z2end(2)-l)(:));

            c = np.unravel_index(np.argmin(cc, axis=None), shape=cc.shape)

            if not np.sum((c == 0) + (c == np.array(cc.shape) - 1)):
                # check that we are not at the edge of the region that was sampled
                x = np.array([-1, 0, 1])
                tmp = self.refine_max_position_2d(cc[c[0] - 1 : c[0] + 2, c[1] - 1 : c[1] + 2], x, x)
                c += tmp
            shiftfound = True

            c += z1beg - z2beg

            rapp_hist = []
            if not shiftfound:
                cor_estimate = c
                # Check that new shift estimate was not already done (avoid eternal loop)
                if self._checkifpart(cor_estimate, rapp_hist):
                    if self.verbose:
                        self.logger.info(f"Stuck in loop?")
                    refine = True
                    shiftfound = True
                    c = np.array([np.nan, np.nan])
                else:
                    rapp_hist.append(cor_estimate)
                    if self.verbose:
                        self.logger.info(f"Changing shift estimate: {cor_estimate}")
                    maxsize = np.minimum(maxsize, np.array(z1.shape) - np.abs(cor_estimate) - 1).astype(int)
                    if (maxsize == 0).sum():
                        if self.verbose:
                            self.logger.info(f"Edge of image reached")
                        refine = False
                        shiftfound = True
                        c = np.array([np.nan, np.nan])
            elif len(rapp_hist) > 0:
                if self.verbose:
                    self.logger.info("\n")

        ####################################
        # refine result; useful when shifts are not integer values
        # JL: I don't understand why this refine step should be useful.
        # In Octave, from fastomo.m, refine is always set to False.
        # So this could be ignored.
        # I keep it for future use if it proves useful.
        # if refine:
        #    if debug:
        #        print('Refining solution ...')
        #    z2n = self.interpolate(z2,c)
        #    indices = np.ceil(np.abs(c)).astype(int)
        #    z1p = np.roll(z1,((c>0) * (-1) * indices),[0,1])
        #    z1p = z1p[1:-indices[0]-1,1:-indices[1]-1].flatten()
        #    z2n = np.roll(z2n,((c>0) * (-1) * indices),[0,1])
        #    z2n = z2n[:-indices[0],:-indices[1]]
        #    ccrefine = np.zeros([3,3])
        #    [n2,m2] = z2n.shape
        #    for k in range(3):
        #        for l in range(3):
        #            z2p = z1p - z2n[2-k:n2-k,2-l:m2-l].flatten()
        #            ccrefine[k,l] = ((z2p - z2p.mean())**2).sum()
        #    x = np.array([-1,0,1])
        #    crefine = self.refine_max_position_2d(ccrefine, x, x)
        #    #crefine = min2par(ccrefine)

        #    # Check if the refinement is effectively confined to subpixel
        #    if (np.abs(crefine) >= 1).sum():
        #        self.logger.info("Problems refining result\n")
        #    else:
        #        c += crefine

        return c

    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        side: str,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        low_pass=0.01,
        high_pass=None,
    ):
        """Automatically finds the Center of Rotation (CoR), given two images
        (projections/radiographs). Suitable for half-aquisition scan.

        This method finds the half-shift between two opposite images,  by
        minimizing the variance of small ROI around a global COR estimate
        (obtained by maximizing Fourier-space computed global correlations).


        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        side: string
            Expected region of the CoR. Must be 'center' in that case.
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
            The ROI will be used for the global estimate.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`

                    Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationOctaveAccurate()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        self.logger.info(
            f"Estimation of the COR with following options: high_pass={high_pass}, low_pass={low_pass}, limz={self.cor_options['limz']}."
        )

        self._check_img_pair_sizes(img_1, img_2)

        if side != "center":
            self.logger.fatal(
                "The accurate algorithm cannot handle half acq. Use 'near', 'fourier-angles', 'sliding-window' or 'growing-window' instead."
            )
            raise ValueError(
                "The accurate algorithm cannot handle half acq. Use 'near', 'fourier-angles', 'sliding-window' or 'growing-window' instead."
            )

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        cc = self._compute_correlation_fft(
            img_1,
            img_2,
            padding_mode,
            high_pass=high_pass,
            low_pass=low_pass,
        )

        # We use fftshift to deal more easily with negative shifts.
        # This has a cost of subtracting half the image shape afterward.
        shift = np.unravel_index(np.argmax(np.fft.fftshift(cc)), img_shape)
        shift -= np.array(img_shape) // 2

        # The real "accurate" starts here (i.e. the octave findshift() func).
        if np.abs(shift[0]) > 10 * self.cor_options["limz"]:
            # This is suspiscious. We don't trust results of correlate.
            self.logger.info(f"Pre-correlation yields {shift[0]} pixels vertical motion")
            self.logger.info(f"We do not consider it.")
            shift = (0, 0)

        # Limit the size of region for comparison to cutsize in both directions.
        # Hard-coded?
        cutsize = img_shape[1] // 2
        oldshift = np.round(shift).astype(int)
        if (img_shape[0] > cutsize) or (img_shape[1] > cutsize):
            im0 = self._cut(img_1, min(img_shape[0], cutsize), min(img_shape[1], cutsize))
            im1 = self._cut(
                np.roll(img_2, oldshift, axis=(0, 1)), min(img_shape[0], cutsize), min(img_shape[1], cutsize)
            )
            shift = oldshift + self._local_correlation(
                im0,
                im1,
                maxsize=self.cor_options["maxsize"],
                refine=self.cor_options["refine"],
                pmcc=self.cor_options["pmcc"],
                normalize=self.cor_options["normalize"],
            )
        else:
            shift = self._local_correlation(
                img_1,
                img_2,
                maxsize=self.cor_options["maxsize"],
                cor_estimate=oldshift,
                refine=self.cor_options["refine"],
                pmcc=self.cor_options["pmcc"],
                normalize=self.cor_options["normalize"],
            )
        if ((shift - oldshift) ** 2).sum() > 4:
            self.logger.info(f"Pre-correlation ({oldshift}) and accurate correlation ({shift}) are not consistent.")
            self.logger.info("Please check!!!")

        offset = shift[1] / 2

        if np.abs(shift[0]) > self.cor_options["limz"]:
            self.logger.info("Verify alignment or sample motion.")
            self.logger.info(f"Verical motion: {shift[0]} pixels.")
            self.logger.info(f"Offset?: {offset} pixels.")
        else:
            self.logger.info(f"Offset?: {offset} pixels.")

        return offset
