import numpy as np
from nabu.preproc.phase import PaganinPhaseRetrieval


def get_decay(curve, cutoff=1e3, vmax=None):
    if vmax is None:
        vmax = curve.max()
    return np.argmax(curve < vmax / cutoff)



def compute_paganin_margin(shape, **pag_kwargs):
    """

    Parameters
    -----------
    shape: tuple
        Detector shape in the form (n_z, n_x)
    """
    P = PaganinPhaseRetrieval(shape, **pag_kwargs)

    ifft_func = np.fft.irfft2 if P.use_R2C else np.fft.ifft2
    conv_kernel = ifft_func(P.paganin_filter)

    vmax = conv_kernel[0,0]

    v_margin = get_decay(conv_kernel[:, 0], cutoff=1e3, vmax=vmax)
    h_margin = get_decay(conv_kernel[0, :], cutoff=1e3, vmax=vmax)
    # If the Paganin filter is very narrow, then the corresponding convolution
    # kernel is constant, and np.argmax() gives 0 (when it should give the max value)
    if v_margin == 0:
        v_margin = shape[0]
    if h_margin == 0:
        h_margin = shape[1]

    return v_margin, h_margin


