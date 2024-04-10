import numpy as np
import astra
from spire.utils import ims
vol = np.load("/scisoft/users/paleo/data/maquette/MRI512cube.npy")

n_x, n_y, n_z = vol.shape
n_a = 1500


def _create_projector_parallel(vol_geom, angles, dx=1., dy=1.):
    n_x, n_z = vol_geom['GridColCount'], vol_geom['GridSliceCount']
    # det_spacing_x, det_spacing_y, det_row_count, det_col_count, angles
    proj_geom = astra.create_proj_geom('parallel3d', dx, dy, n_z, n_x, angles)
    projector, proj_geom = astra.create_projector('cuda3d', proj_geom, vol_geom)
    return projector, proj_geom


def _create_projector_helical(vol_geom, dz, n_angles):
    n_x, n_z = vol_geom['GridColCount'], vol_geom['GridSliceCount']
    vectors = np.zeros((n_angles, 12))
    angles = np.linspace(0, np.pi, n_angles)
    for i in range(n_angles):
        # ray direction
        vectors[i,0] = np.sin(angles[i])
        vectors[i,1] = -np.cos(angles[i])
        vectors[i,2] = 0

        # center of detector
        # ~ vectors[i,3] = 0
        # ~ vectors[i,4] = 0
        vectors[i,5] = i*dz

        # vector from detector pixel (0,0) to (0,1)
        vectors[i,6] = np.cos(angles[i])
        vectors[i,7] = np.sin(angles[i])
        vectors[i,8] = 0;

        # vector from detector pixel (0,0) to (1,0)
        vectors[i,9] = 0
        vectors[i,10] = 0
        vectors[i,11] = 1

    proj_geom = astra.create_proj_geom('parallel3d_vec', n_z, n_x, vectors)
    projector = astra.create_projector('cuda3d', proj_geom, vol_geom)
    return projector, proj_geom


def proj3D(volume, n_a):
    n_x, n_y, n_z = volume.shape
    vol_geom = astra.create_vol_geom(n_y, n_x, n_z) # rows, colums, slices (y, x, z)
    vol_astra = astra.data3d.create('-vol', vol_geom, volume)

    angles = np.linspace(0, np.pi, n_a)
    projector, proj_geom = _create_projector_parallel(vol_geom, angles)

    projs_id, projs = astra.create_sino3d_gpu(vol_astra, proj_geom, vol_geom)
    astra.data3d.clear() #

    return projs


def proj3D_helical(volume, n_a, dz):
    n_x, n_y, n_z = volume.shape
    vol_geom = astra.create_vol_geom(n_y, n_x, n_z) # rows, colums, slices (y, x, z)
    vol_astra = astra.data3d.create('-vol', vol_geom, volume)

    projector, proj_geom = _create_projector_helical(vol_geom, dz, n_a)

    projs_id, projs = astra.create_sino3d_gpu(vol_astra, proj_geom, vol_geom)
    astra.data3d.clear() #

    return projs


# ~ projs = proj3D_helical(vol, 150, 2)
