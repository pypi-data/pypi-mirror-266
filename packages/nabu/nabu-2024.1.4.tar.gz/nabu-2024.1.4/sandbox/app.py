from time import sleep
import pycuda.autoinit
import pycuda.gpuarray as garray
from nabu.resources.processconfig import ProcessConfig
from nabu.resources.tasks import build_processing_steps

from nabu.app.logger import Logger

from nabu.app.chunkreader import ChunkReaderComponent
from nabu.app.flatfield import FlatFieldComponent
from nabu.app.phase import PhaseRetrievalComponent
from nabu.app.opmap import NegativeLogComponent
from nabu.app.ccdfilter import CCDFilterComponent
from nabu.app.unsharp import UnsharpMaskComponent
from nabu.app.reconstructor import ReconstructorComponent


if __name__ == "__main__":

    conf = ProcessConfig("/home/pierre/workspace/data/nabu.conf")
    steps, options = build_processing_steps(conf)
    dataset_infos = conf.dataset_infos
    SUB_REGION = (None, None, None, 50)

    logger = Logger("nabu_processing", console=True)

    # Read chunk
    options["read_chunk"]["sub_region"] = SUB_REGION
    options["read_chunk"]["convert_float"] = True
    Ch = ChunkReaderComponent(options["read_chunk"], dataset_infos, logger=logger)
    Ch.execute()
    radios = Ch.chunk_reader.files_data
    d_radios = garray.to_gpu(radios)

    # Flat-field
    options["flatfield"]["sub_region"] = SUB_REGION
    options["flatfield"]["use_opencl"] = False
    options["flatfield"]["use_cuda"] = True
    F = FlatFieldComponent(d_radios, options["flatfield"], dataset_infos, logger=logger)
    F.execute()

    # CCD filter
    options["ccd_correction"]["use_cuda"] = True
    options["ccd_correction"]["use_opencl"] = False
    CCD = CCDFilterComponent(d_radios, options["ccd_correction"], dataset_infos, logger=logger)
    CCD.execute()


    # Phase retrieval
    options["phase"]["use_cuda"] = True
    options["phase"]["use_opencl"] = False
    P = PhaseRetrievalComponent(radios[0].shape, options["phase"], dataset_infos, logger=logger)
    P.execute(d_radios)

    # Unsharp
    # ~ options["unsharp_mask"]["use_cuda"] = True
    # ~ options["unsharp_mask"]["use_opencl"] = False
    # ~ U = UnsharpMaskComponent(radios[0].shape, options["unsharp_mask"], dataset_infos, logger=logger)
    # ~ U.execute(d_radios)

    # -log()
    options["take_log"]["use_cuda"] = True
    options["take_log"]["use_opencl"] = False
    L = NegativeLogComponent(d_radios, options["take_log"], dataset_infos, logger=logger)
    L.execute()


    # Test
    # ~ from spire.utils import ims
    # ~ r = d_radios.get()
    # ~ ims(r[:, 10, :])


    # Reconstruction
    options["reconstruction"]["use_cuda"] = True

    # Test ...
    if 1:
        options["reconstruction"]["start_x"] = 100
        options["reconstruction"]["end_x"] = -100
        options["reconstruction"]["start_y"] = 100
        options["reconstruction"]["end_y"] = -100
        options["reconstruction"]["start_z"] = 0
        options["reconstruction"]["end_z"] = SUB_REGION[-1]-1
        d_rec = garray.zeros((50, 1849, 1849), "f") # y
    #
    else:
        d_rec = garray.zeros((SUB_REGION[-1], 2048, 2048), "f")
    R = ReconstructorComponent(d_radios.shape, options["reconstruction"], dataset_infos, logger=logger)
    R.execute(d_radios, output=d_rec)


    # Write to file
    rec = d_rec.get()
    import numpy as np
    np.save("/home/pierre/tmp/crayon/recs_nabu_vertical.npy", rec)

    """from nabu.reconstruction.reconstructor_cuda import CudaReconstructor
    R = CudaReconstructor(
        radios.shape,
        [0, 1],
        vol_type="projections",
        extra_options={"padding_mode": conf.nabu_config["reconstruction"]["padding_type"]}
    )
    d_recs = garray.zeros((1, 2048, 2048), "f")
    R.reconstruct(d_radios, output=d_recs)
    recs = d_recs.get()
    ims(recs[0], cmap="gray")
    # save
    import numpy as np
    np.save("/tmp/rec0.npy", recs[0])
    """


"""
Notes
  - If the cuda backend is used at step N, it should also be used at step N+1,


otherwise we have to get() the data

"""

