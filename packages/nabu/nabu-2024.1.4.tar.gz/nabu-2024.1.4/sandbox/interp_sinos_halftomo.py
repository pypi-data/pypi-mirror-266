def interp_sinos_mp(sinos, angles, nproc=1):
    n_a = angles.size
    angles_1 = angles[:n_a//2]
    angles_2 = angles[n_a//2:]
    sinos_interpolated = np.zeros(
        (sinos.shape[0], angles_2.size, sinos.shape[-1]), dtype=sinos.dtype
    )
    def _interp_sino(args):
        sino, sino_interpolated = args
        interpolator = interp1d(angles_2, sino[angles.size//2:, :], axis=0, fill_value="extrapolate")
        sino_interpolated[:] = interpolator(angles_1 + 180)
        return None
    with ThreadPool(nproc) as tp:
        tp.map(_interp_sino, zip(sinos, sinos_interpolated))
    return sinos_interpolated




def interp_sinos(sinos, angles):
    n_a = angles.size
    angles_1 = angles[:n_a//2]
    angles_2 = angles[n_a//2:]
    sinos_interpolated = np.zeros(
        (sinos.shape[0], angles_2.size, sinos.shape[-1]), dtype=sinos.dtype
    )
    for i in range(sinos.shape[0]):
        sino = sinos[i, n_a//2:, :]
        interpolator = interp1d(angles_2, sino, axis=0, fill_value="extrapolate")
        sinos_interpolated[i] = interpolator(angles_1 + 180)
    return sinos_interpolated
