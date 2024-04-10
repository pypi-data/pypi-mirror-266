from posixpath import join
import numpy as np
from nabu.io.utils import get_h5_value
from nabu.app.utils import parse_params_values
from nxtomomill.nexus.nxtomo import NXtomo
from nxtomomill.utils import ImageKey
from integrator.hdf5 import ID15Dataset, list_datasets

def convert_id15_dataset(
    fname, output_fname,
    detector_name="pcoedgehs", ignore_last_n_projections=100,
    energy=None, distance=None
):

    entries = list_datasets(fname)
    if len(entries) < 3:
        print("Error: Expected at least three datasets, got only %d" % (len(entries)))
        return
    do_360 = False
    if len(entries) == 6:
        do_360 = True

    projs = ID15Dataset(fname, detector_name=detector_name, entry="1.1")
    flats = ID15Dataset(fname, detector_name=detector_name, entry="2.1")
    darks = ID15Dataset(fname, detector_name=detector_name, entry="3.1")
    if do_360:
        projs2 = ID15Dataset(fname, detector_name=detector_name, entry="4.1")
        flats2 = ID15Dataset(fname, detector_name=detector_name, entry="5.1")
        darks2 = ID15Dataset(fname, detector_name=detector_name, entry="6.1")

    my_nxtomo = NXtomo("entry")

    data_urls = [
        darks.dataset_hdf5_url,
        flats.dataset_hdf5_url,
        projs.dataset_hdf5_url
    ]
    if do_360:
        data_urls.extend([
            # darks2.dataset_hdf5_url,
            flats2.dataset_hdf5_url,
            projs2.dataset_hdf5_url
        ])
    my_nxtomo.instrument.detector.data = data_urls

    img_keys = [
        [ImageKey.DARK_FIELD] * darks.data_shape[0],
        [ImageKey.FLAT_FIELD] * flats.data_shape[0],
        [ImageKey.PROJECTION] * (projs.data_shape[0] - ignore_last_n_projections),
        [ImageKey.ALIGNMENT]  * ignore_last_n_projections,
    ]
    if do_360:
        img_keys.extend([
            # [ImageKey.DARK_FIELD] * darks2.data_shape[0],
            [ImageKey.FLAT_FIELD] * flats2.data_shape[0],
            [ImageKey.PROJECTION] * (projs2.data_shape[0] - ignore_last_n_projections),
            [ImageKey.ALIGNMENT]  * ignore_last_n_projections,
        ])

    my_nxtomo.instrument.detector.image_key_control = np.concatenate(img_keys)

    rotation_angles = get_h5_value(projs.fname, join(projs.entry, "instrument/hrrz/data"))
    if rotation_angles is not None:
        last_idx = None
        if ignore_last_n_projections > 0:
            last_idx = -ignore_last_n_projections
        rotation_angles = [
            [0] * darks.data_shape[0],
            [0] * flats.data_shape[0],
            rotation_angles[:last_idx],
            [0] * ignore_last_n_projections
        ]
        if do_360:
            rotation_angles2 = get_h5_value(projs2.fname, join(projs2.entry, "instrument/hrrz/data"))
            rotation_angles.extend([
                # [0] * darks2.data_shape[0],
                [0] * flats2.data_shape[0],
                rotation_angles2[:last_idx],
                [0] * ignore_last_n_projections
            ])
        print(np.concatenate(rotation_angles).shape)
        my_nxtomo.sample.rotation_angle = np.concatenate(rotation_angles)

    # my_nxtomo.instrument.detector.field_of_view = "Full" if not(do_360) else "Half"
    my_nxtomo.instrument.detector.field_of_view = "Full"
    my_nxtomo.instrument.detector.x_pixel_size = my_nxtomo.instrument.detector.y_pixel_size = 6.5 * 1e-6

    if energy is not None:
        my_nxtomo.energy = energy  # in keV by default
    if distance is not None:
        my_nxtomo.instrument.detector.distance = distance  # in meter


    my_nxtomo.save(file_path=output_fname, overwrite=True, nexus_path_version=1.1)





CLIConfig = {
    "input_file": {
        "help": "Bliss HDF5 file",
        "default": "",
        "mandatory": True,
    },
    "output_file": {
        "help": "Output NX file",
        "default": "",
        "mandatory": True,
    },
    "ignore_last_n_projections": {
        "help": "Number of projections to ignore in the end of each series of projections.",
        "default": 0,
        "type": int,
    },
    "detector_name": {
        "help": "Detector name. Default is pcoedgehs",
        "default": "pcoedgehs",
    },
    "energy": {
        "help": "Incident beam energy in keV",
        "default": 0.,
        "type": float,
    },
    "distance": {
        "help": "Sample-detector distance in meters",
        "default": 0.,
        "type": float,
    },
}


if __name__ == "__main__":

    args = parse_params_values(
        CLIConfig,
        parser_description="Convert a ID15A absorption tomography acquisition file to NX format",
    )

    convert_id15_dataset(
        args["input_file"],
        args["output_file"],
        detector_name=args["detector_name"],
        ignore_last_n_projections=args["ignore_last_n_projections"],
        energy=args["energy"] or None,
        distance=args["distance"] or None
    )

