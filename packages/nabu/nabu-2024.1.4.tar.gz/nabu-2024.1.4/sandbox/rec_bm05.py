import numpy as np
from nabu.resources.dataset_analyzer import analyze_dataset
from nabu.io.reader import ChunkReader
from nabu.preproc.ccd import FlatField
from nabu.preproc.double_flat_field import DoubleFlatField
from nabu.preproc.ccd import CCDCorrection
from nabu.preproc.phase import PaganinPhaseRetrieval
from nabu.preproc.sinogram import SinoProcessing

from nabu.reconstruction.fbp import Backprojector
from spire.utils import ims


di = analyze_dataset("/data/visitor/md1252/bm05/HR/tube02/HA-800_2.25um_FO-20.122ULZ-OLZ-OLP_008_")

C = ChunkReader(di.projections, sub_region=(None, None, 1024-50, 1024+50), convert_float=True)
C.load_files()
radios = C.files_data

F2 =FlatField(radios.shape, di.flats, di.darks, radios_indices=sorted(di.projections.keys()), sub_region=C.sub_region)
F2.normalize_radios(radios)

DFF = DoubleFlatField(radios.shape, input_is_mlog=False)
DFF.apply_double_flatfield(radios)

ccd_corr = CCDCorrection(radios.shape)
ccd_corr.median_clip_correction(radios, inplace=True)

P2 = PaganinPhaseRetrieval(radios.shape[1:], distance=di.distance*1e1, energy=di.energy, pixel_size=2.25, delta_beta=100)
for i in range(radios.shape[0]):
    radios[i] = P2.apply_filter(radios[i])

np.log(radios, out=radios)
radios *= -1
S = SinoProcessing(radios_shape=radios.shape, rot_center=1831.5, halftomo=True)
o = S.radios_to_sinos(radios)

B = Backprojector(o.shape[1:], extra_options={"padding_mode": "edges"})
ims(B.fbp(o[50]), cmap="gray")







# Taken from PyHST/Cspace/CCspace.c (line 6066 @ f826cfc0de7be7ee185bb6ba38f7fdb0d0ec2a8a)
def straighten_sino(Sino, output=None):
    if output is None:
        output = Sino
    Nr, Nc = Sino.shape
    J = np.arange(Nc)
    x = 2.* (J + 0.5 - Nc/2)/Nc
    sum0 = Nc
    f2 = (3.0*x*x-1.0)
    sum1 = (x**2).sum()
    sum2 = (f2**2).sum()

    for i in range(Nr):
        ff0 = Sino[i, :].sum()
        ff1 = (x * Sino[i, :]).sum()
        ff2 = (f2*Sino[i, :]).sum()

        output[i, :] = Sino[i, :] - ff0/sum0 + ff1*x/sum1 + ff2*f2/sum2

    return output





