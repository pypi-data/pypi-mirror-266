import numpy as np
from nabu.estimation.translation import DetectorTranslationAlongBeam
from tomoscan.io import HDF5File


def get_data(fname, h5_paths):
    with HDF5File(fname, "r") as f:
        align_data = f[h5_paths["align_data"]][()]
        dark = f[h5_paths["dark"]][0]
        pixel_size_um = f[h5_paths["pixel_size"]][()]
        positions_mm = f[h5_paths["positions"]][()]

    # Dark subtraction
    align_data = align_data - dark.astype("f")

    return align_data, pixel_size_um, positions_mm



def get_alignment(align_data, pixel_size_um, positions_mm, plot=True):

    tr_calc = DetectorTranslationAlongBeam()
    if plot == True:
        tr_calc.verbose=True

    shifts_v, shifts_h = tr_calc.find_shift(align_data, positions_mm)

    # pixel_size is in microns, motor position is in mm
    tilt_v_deg = np.rad2deg(np.arctan(shifts_v * pixel_size_um / 1e3))
    tilt_h_deg = np.rad2deg(np.arctan(shifts_h * pixel_size_um / 1e3))
    print (f"\nVertical tilt  to be applied in deg (thy): {tilt_v_deg}")
    print (f"Horizontal tilt to be applied in deg (thz): {tilt_h_deg}\n")

    return align_data, shifts_v, shifts_h, positions_mm






if __name__ == "__main__":
    fname = "/data/id19/inhouse/id192201/id19/sample/sample_0001/sample_0001.h5"
    h5_paths = {
        "align_data": "11.1/measurement/pcolinux",
        "dark": "12.1/measurement/pcolinux",
        "pixel_size": "11.1/instrument/pcolinux/x_pixel_size",
        "positions": "11.1/measurement/hrxc"
    }
    align_data, pixel_size_um, positions_mm = get_data(fname, h5_paths)
    # align_data, shifts_v, shifts_h, positions_mm = get_alignment(align_data, pixel_size_um, positions_mm)

    D = DetectorTranslationAlongBeam()
    D. verbose = True
    sv, sh = D.find_shift(align_data, positions_mm)
    D.verbose = False
    sv, sh = D.find_shift(align_data, positions_mm)
    D.verbose = True
    sv, sh = D.find_shift(align_data, positions_mm)



