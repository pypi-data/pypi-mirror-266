import numpy as np
from glob import glob
import h5py
from silx.io.dictdump import h5todict

# ~ data = h5todict("/scratch/paleo/bamboo/bamboo_nxtomomill_rec_0100_0.hdf5", path="/entry0000/reconstruction/results")["data"]

def merge_recs(pattern, h5_path):
    fl = glob(pattern)
    fl.sort()
    if fl == []:
        raise ValueError("Nothing found as pattern %s" % pattern)
    recs = []
    n_imgs = 0
    for fname in fl:
        data = h5todict(fname, path=h5_path)["data"]
        n_imgs += data.shape[0]
        recs.append(data)
    recs_np = np.zeros((n_imgs,) + recs[0].shape[1:], dtype=recs[0].dtype)
    pos = 0
    for i in range(len(recs)):
        data = recs[i]
        recs_np[pos:pos+data.shape[0], :, :] = data[:, :, :]
        pos += data.shape[0]
    return recs_np


# TODO checks on shape[1:]
def merge_hdf5_files(pattern, h5_path, output_file):
    files_list = glob(pattern)
    files_list.sort()
    if files_list == []:
        raise ValueError("Nothing found as pattern %s" % pattern)
    virtual_sources = []
    shapes = []
    for fname in files_list:
        with h5py.File(fname, "r") as fid:
            shape = fid[h5_path].shape
        vsource = h5py.VirtualSource(fname, name=h5_path, shape=shape)
        virtual_sources.append(vsource)
        shapes.append(shape)

    n_images = sum([shape[0] for shape in shapes])
    virtual_layout = h5py.VirtualLayout(
        shape=(n_images, ) + shapes[0][1:],
        dtype='f'
    )
    start_idx = 0
    for vsource, shape in zip(virtual_sources, shapes):
        n_imgs = shape[0]
        virtual_layout[start_idx:start_idx + n_imgs] = vsource
        start_idx += n_imgs
    with h5py.File(output_file, 'w') as f:
        f.create_virtual_dataset('data', virtual_layout)


