import numpy as np
import astra
from utils import ims


def _create_projector_parallel(vol_geom, angles, dx=1., dy=1.):
    n_x, n_z = vol_geom['GridColCount'], vol_geom['GridSliceCount']
    # det_spacing_x, det_spacing_y, det_row_count, det_col_count, angles
    proj_geom = astra.create_proj_geom('parallel3d', dx, dy, n_z, n_x, angles)
    projector = astra.create_projector('cuda3d', proj_geom, vol_geom)
    return projector, proj_geom


def _create_projector_tilted(vol_geom, n_angles, alpha):
    n_x, n_z = vol_geom['GridColCount'], vol_geom['GridSliceCount']
    vectors = np.zeros((n_angles, 12))
    angles = np.linspace(0, np.pi, n_angles)
    c_a = np.cos(alpha)
    s_a = np.sin(alpha)
    for i in range(n_angles):
        # ray direction
        vectors[i,0] = np.sin(angles[i]) * c_a
        vectors[i,1] = -np.cos(angles[i]) * c_a
        vectors[i,2] = s_a

        # center of detector
        # ~ vectors[i,3] = 0
        # ~ vectors[i,4] = 0
        # ~ vectors[i,5] = 0

        # vector from detector pixel (0,0) to (0,1)
        vectors[i,6] = np.cos(angles[i])
        vectors[i,7] = np.sin(angles[i])
        vectors[i,8] = 0

        # vector from detector pixel (0,0) to (1,0)
        vectors[i,9] = -np.sin(angles[i]) * s_a
        vectors[i,10] = np.cos(angles[i]) * s_a
        vectors[i,11] = c_a

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


def proj3D_tilt(volume, n_a, alpha):
    n_x, n_y, n_z = volume.shape
    vol_geom = astra.create_vol_geom(n_y, n_x, n_z) # rows, colums, slices (y, x, z)
    vol_astra = astra.data3d.create('-vol', vol_geom, volume)

    projector, proj_geom = _create_projector_tilted(vol_geom, n_a, alpha)

    projs_id, projs = astra.create_sino3d_gpu(vol_astra, proj_geom, vol_geom)
    astra.data3d.clear() #

    return projs





def create_projectors(vol, n_angles, alpha):
    n_x, n_y, n_z = vol.shape
    vol_geom = astra.create_vol_geom(n_y, n_x, n_z) # rows, colums, slices (y, x, z)

    vectors = np.zeros((n_angles, 12))
    angles = np.linspace(0, np.pi, n_angles)
    c_a = np.cos(alpha)
    s_a = np.sin(alpha)
    for i in range(n_angles):
        # ray direction
        vectors[i,0] = np.sin(angles[i]) * c_a
        vectors[i,1] = -np.cos(angles[i]) * c_a
        vectors[i,2] = s_a

        # center of detector
        # ~ vectors[i,3] = 0
        # ~ vectors[i,4] = 0
        # ~ vectors[i,5] = 0

        # vector from detector pixel (0,0) to (0,1)
        vectors[i,6] = np.cos(angles[i])
        vectors[i,7] = np.sin(angles[i])
        vectors[i,8] = 0

        # vector from detector pixel (0,0) to (1,0)
        vectors[i,9] = -np.sin(angles[i]) * s_a
        vectors[i,10] = np.cos(angles[i]) * s_a
        vectors[i,11] = c_a

    proj_geom = astra.create_proj_geom('parallel3d_vec', n_z, n_x, vectors)

    vol_id = astra.data3d.create('-vol', vol_geom, data=vol)
    # ~ proj_id = astra.data3d.create('-sino', proj_geom)

    # ~ proj_id = astra.create_projector('cuda3d', proj_geom, vol_geom)
    # ~ sinogram_id, sinogram = astra.create_sino3d_gpu(vol, proj_id)
    sino_id, sino = astra.create_sino3d_gpu(vol, proj_geom, vol_geom, returnData=True)

    # ~ rec_id, rec = astra.create_backprojection3d_gpu(sino, proj_geom, vol_geom, returnData=True)

    rec_id = astra.data3d.create('-vol', vol_geom)

    # Set up the parameters for a reconstruction algorithm using the GPU
    # ~ cfg = astra.astra_dict('SIRT3D_CUDA')
    cfg = astra.astra_dict('BP3D_CUDA')
    cfg['ReconstructionDataId'] = rec_id
    cfg['ProjectionDataId'] = sino_id
    alg_id = astra.algorithm.create(cfg)

    astra.algorithm.run(alg_id, 10)

    rec = astra.data3d.get(rec_id)






def fbp3D_tilted(projector, sino):
    cfg_backproj = astra.creators.astra_dict('FBP3D_CUDA')
    cfg_backproj['FilterType'] = 'Ram-Lak'
    cfg_backproj['ProjectorId'] = projector
    pg = astra.projector.projection_geometry(projector)
    # In
    sid = astra.data3d.link('-sino', pg, sino)
    cfg_backproj['ProjectionDataId'] = sid
    # Out
    vg = astra.projector.volume_geometry(projector)
    vshape = astra.functions.geom_size(vg)
    v = np.zeros(vshape, dtype=np.float32)
    vid = astra.data2d.link('-vol', vg, v)
    cfg_backproj['ReconstructionDataId'] = vid

    bp_id = astra.algorithm.create(cfg_backproj)
    astra.algorithm.run(bp_id)
    astra.algorithm.delete(bp_id)
    astra.data3d.delete([sid, vid])
    return v







def example():
    vol = np.load("/scisoft/users/paleo/data/maquette/MRI512cube.npy")

    tilt = np.deg2rad(20)
    n_angles = 180
    projs = proj3D_tilt(vol, n_angles, tilt)
    projs0 = proj3D(vol, n_angles)


    legend=["Proj 0", "Proj 45", "Proj 90", "Proj 135"]
    print("Standard parallel geometry")
    ims(
        [projs0[:, 0, :], projs0[:, 45, :], projs0[:, 90, :], projs0[:, 135, :]],
        legend=legend
    )
    print("Parallel geometry with tilted rotation axis")
    ims(
        [projs[:, 0, :], projs[:, 45, :], projs[:, 90, :], projs[:, 135, :]],
        legend=legend
    )









def mc_tilt_vals(shape, n_a, alpha, n_sim=5):
    n_z, n_y, n_x = shape
    x0 = (n_x - 1)/2.
    y0 = (n_y - 1)/2.
    angles = np.linspace(0, np.pi, n_a, False)
    s_a = np.sin(alpha)
    c_a = np.cos(alpha)
    s_t = np.sin(angles)
    c_t = np.cos(angles)
    vals = {}
    for i in range(n_a):
        for j in range(n_sim):
            x = np.random.randint(0, high=n_x)
            y = np.random.randint(0, high=n_y)
            z = np.random.randint(0, high=n_z)
            vals[(x, y, z)] = s_a * (s_t[i] * (x-x0) + x0) \
            + s_a * (c_t[i] * (y-y0) + y0) \
            + c_a * z
    return vals

"""
#
# For 512**3 with angular range [0, 2pi] and alpha = 50 mrad,
# we have delta_z_max = 40
#
V = mc_tilt_vals((512, 512, 512), 180, 50e-3, n_sim=100)
Z = np.array(list(map(lambda x: x[-1], V.keys())))
hist(np.array(list(V.values())) - Z, bins=64)

# For 14 mrad, delta_z_max = 13
# For 14 mrad and volume 2048**3, we have delta_z_max = 50

"""



"""
def get_sino_tilt(sinos, alpha, rot_center=None):
    n_z, n_a, n_x = sinos.shape
    if rot_center is None:
        rot_center = (n_x - 1)/2.
    c_a = np.cos(alpha)
    s_a = np.sin(alpha)

    X = np.arange(n_x)
    Y = np.arange(n_y)
    X *
"""














