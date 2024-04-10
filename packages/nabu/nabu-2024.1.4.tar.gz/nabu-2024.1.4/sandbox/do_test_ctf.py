from nabu.preproc.ctf_id16 import ID16CTFPhaseRetrieval
from nabu.preproc.ctf_id16 import ID16CTFPhaseRetrieval
from nabu.preproc.ccd import FlatFieldArrays
from nabu.preproc.ctf import GeoPars
from nabu.testutils import get_data
test_data = get_data("ctf_tests_data_all_pars.npz")
rand_disp_vh = test_data["rh"]
rand_disp_vh.shape = [rand_disp_vh.shape[0], rand_disp_vh.shape[2]]
geo_pars = GeoPars(
	z1_vh=test_data["z1_vh"],
	z2=test_data["z2"],
	pix_size_det=test_data["pix_size_det"],
	length_scale=test_data["length_scale"],
	wavelength=test_data["wave_length"],
)
flats = [test_data["ref0"], test_data["ref1"]]
dark = test_data["dark"]

flatfield = FlatFieldArrays(
    [1200] + list(test_data["img_shape_vh"]), {0: flats[0], 1200: flats[1]}, {0: dark}
)
ctf_filter = ID16CTFPhaseRetrieval(
	geo_pars, 27.0,
	lim1=1.0e-5, lim2=0.2,
	flatfielder=flatfield,
	flat_distorsion_params={
		"tile_size": 100,
		"interpolation_kind": "cubic",
		"padding_mode": "edge",
		"correction_spike_threshold": 3.0
	},
	spikes_removal_threshold=0.04
)
img = test_data["im"].astype("f")
phase = ctf_filter.retrieve_phase(
	img, int(test_data["ipro"]),
	padded_shape=test_data["padded_img_shape_vh"],
	translation_vh=rand_disp_vh[:, int(test_data["ipro"])],
	normalize_by_mean=True
)
