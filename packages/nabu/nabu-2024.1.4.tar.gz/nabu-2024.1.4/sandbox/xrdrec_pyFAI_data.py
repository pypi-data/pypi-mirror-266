

data = h5_read(filename)  # radially integrated data
q = hdf5read(filename,'/q')
y = hdf5read(filename,'/y')
omega = hdf5read(filename,'/omega') ;
# y = y(1:ny*nomega)
y = y[:ny*nomega]
# omega = omega(1:ny*nomega) ;
omega = omega[:ny*nomega]


#
# size(X) : height, width, nz
# size(X, 1): height
# flip(X, 2): X[:, i, :] = np.fliplr(X[:, i, :]) for i
#



def get_matlab_to_python_size(arr, dim):
    if arr.ndim == 2:
        # 2D: both Matlab and Python ordering is (Height, Width)
        return arr.shape[dim-1]
    elif arr.ndim == 3:
        # 3D:
        # Matlab: (Height, Width, Nz) ; indices start at 1
        # Python: (Nz, Height, Width) ; indices start at 0
        matlab_to_python = [None, 1, 2, 0]
        dim_py = matlab_to_python[dim]
        if dim_py is None:
            raise ValueError("Matlab index cannot be zero")
        return arr.shape[dim_py]
    else:
        return arr.size


def xrdrec_pyFAI_data(
    ny,
    nomega,
    omega_step,
    acq_method,
    zinger_removal,
    air_mask,
    diode_norm,
    int_norm_roi,
    sample_move_roi,
    sample_thrs,
    c_range,
    vis_rec,
    h5overwrite
):
    """
    FILENAME HDF5 filename containing radially integrated data
    NY number of y steps
    NOMEGA number of omega steps
    OMEGA_STEP angular step
    ACQ_METHOD acquisition methods: FAST_ROT_SLOW_TRANS, FAST_TRANS_STEP_ROT, ZIG_ZAG, FAST_ROT_SLOW_TRANS_OLD
    ZINGER_REMOVAL = 1 if removal performed, 0 otherwise
    AIR_MASK (matrix) mask for air scattering calculation and removal. Set to 1 the pixels used to calculate
             the air scattering contribution and set to 0 he others. SIZE(AIR_MATRIX) = SIZE(Y) = SIZE(OMEGA) = [NY/2 2*NOMEGA]

    DIODE_NORM = 1 if diode normalization is performed, 0 otherwise
    INT_NORM_ROI (string) region of interest for total integrated scattering normalization, empty if no normalization perform
    SAMPLE_MOVE_ROI roi for calculating the center of mass to correct for sample movement (this does also the center of rotation)
    SAMPLE_THRS threshold for calculating the center of mass. SAMPLE_THRS = 0.25 is a typical value
    C_RANGE
        If ACQ_METHOD = ZIG_ZAG
              C_RANGE is a vector containing the center of rotation searching range.
              C_RANGE is expressed in pixel units
        If ACQ_METHOD = FAST_ROT_SLOW_TRANS
              C_RANGE is a scalar defining the rotation axis.
              C_RANGE is expressed in millimiters
        If ACQ_METHOD = FAST_ROT_SLOW_TRANS_OLD
              C_RANGE is a vector containing the center of rotation searching range.
              C_RANGE is expressed in millimiters
    VIS_REC = 1 if visualization of reconstruction performed
    H5OVERWRITE if overwrite previously reconstructed data, 0 if not
    """

    if diode_norm:
        diode = hdf5read(filename,'/diode')
        # s = s ./ diode(:)' * mean(diode) ;
        s = s / diode * np.mean(diode)

    # Here "s" is likely to be 2D, at least for fast_rot_slow_trans**

    if acq_method == 'zig_zag':
        # s = reshape(s,size(s,1),ny,nomega)
        s = s.reshape((nomega, s.shape[-2], ny))
        # s(:,:,2:2:end) = flip(s(:,:,2:2:end),2) ;
        s[1::2, :, :] = np.flip(s[1::2, :, :], axis=0)
        # s = permute(s,[2,3,1]) ;
        s = np.moveaxis(s, [0, 1, 2], [1, 2, 0])
        # figure(1) ; imagesc(sum(s,3)) ; colormap(jet) ; title(sprintf('integrated sinogram %s',strrep(filename,'_','-'))) ;  drawnow ;
        if verbose:
            plt.figure()
            plt.imshow(np.sum(s, axis=0), cmap="jet")
            plt.title("Integrated sinogram")
        # ny = size(s,1) ;
        ny = s.shape[1]
        # nomega = 180 / omega_step
        nomega = 180 / omega_step

    elif acq_method == 'fast_rot_slow_trans':
        # Here s is 2D ?
        # s = s(:,1:ny*nomega);
        s = s[:, :ny*nomega]
        # s = permute(s,[2 1]) ;
        s = np.moveaxis(s, [0, 1], [1, 0])
        # s = reshape(s,2*nomega,ny/2,size(s,2)) ;
        s = s.reshape((s.shape[0], 2*nomega, ny//2))
        # s = permute(s,[2 1 3]) ;
        s = np.moveaxis(s, [0, 1, 2], [1, 0, 2])
        # y = reshape(y,2*nomega,ny/2) ;
        y = y.reshape((2*nomega, ny//2))
        # y = permute(y,[2 1]) ;
        y = np.moveaxis(y, 1, 0)

    elif acq_method == 'fast_rot_slow_trans_old':
        # Here s is 2D ?
        # s = s(:,1:ny*nomega) ;
        s = s[:, :ny*nomega]
        # s = permute(s,[2 1]) ;
        s = np.moveaxis(s, 1, 0)
        # s = reshape(s,2*nomega,ny/2,size(s,2)) ;
        s = s.reshape((s.shape[0], 2*nomega, ny//2))
        # s = permute(s,[2 1 3]) ;
        s = np.moveaxis(s, [0, 1, 2], [1, 0, 2])
        # y = reshape(y,2*nomega,ny/2) ;
        y = y.reshape((2*nomega, ny//2))
        # y = permute(y,[2 1]) ;
        y = np.moveaxis(y, 1, 0)
        # omega = reshape(omega,2*nomega,ny/2) ;
        omega = omega.reshape((2*nomega, ny//2)
        # omega = permute(omega,[2 1]) ;
        omega = np.moveaxis(omega, 1, 0)
    else:
        print("Unknown acquisition method")
        return


    # remove zingers
    if zinger_removal:
        # sn = sino_hot_spot_remove(s,[0:.005:5],[1 5], 1) ;
        sn = sino_hot_spot_remove(s, np.arange(0, 5+0.005, .005), [1, 5], 1)
     else:
         # sn = s ;
         sn = s

    # remove air scattering
    if air_mask is not None:
        ## air_mask seems to be 3D
        ## sum(air_mask) sums along the first dim (height)
        # if sum(sum(air_mask)==0)
        if np.any(air_mask.sum(axis=1) == 0):
            # use the same air scattering pattern for all orientations
            # n = sum(air_mask(:)) ;
            n = air_mask.sum()
            # a = sum( sum( sn .* air_mask(:,:,ones(1,size(sn,3))), 1), 2) / n ;
            o = np.ones(sn.shape[0])
            a = (sn * air_mask[o, :, :]).sum(axis=1, keepdims=True).sum(axis=2, keepdims=True) / n
            # sn = sn - a(ones(1,size(sn,1)),ones(1,size(sn,2)),:) ;
            sn -= a[:, np.ones(sn.shape[1]), np.ones(sn.shape[2])]
        else:
            # use the same specific air scattering pattern for each orientations
            # n = sum(air_mask) ;
            n = air_mask.sum(axis=1, keepdims=True)
            # a = sum( sn .* air_mask(:,:,ones(1,size(sn,3))), 1) ./ n(:,:,ones(1,size(sn,3)));
            o = np.ones(sn.shape[0])
            num = (sn * air_mask[o, :, :]).sum(axis=1, keepdims=True)
            denom = n[o, :, :]
            a = num / denom
            # sn = sn - a(ones(1,size(sn,1)),:,:) ;
            sn -= a[:, np.ones(sn.shape[1]), :]


    # normalize total intensity
    # should do better. For example this is wrong when using highly absorbing samples without radial
    # symmetry. Possible solutions: matlab interp or model the behaviour of sample absorption
    if int_norm_roi is not None:
        # m = eval(sprintf('mean(mean(sn(:,:,%s),3),1)',int_norm_roi)) ; plot(m(:),'o') ; drawnow ;
        # assuming int_norm_roi is a slice object
        m = sn[int_norm_roi, :, :].mean(axis=0, keepdims=True).mean(axis=1, keepdims=True)
        # sn = sn ./ m(ones(1,size(sn,1)),:,ones(1,size(sn,3))) * mean(m(:)) ;
        sn = sn / m[np.ones(sn.shape[0]), np.ones(sn.shape[1]), :] * m.mean()
        # figure(2) ; imagesc(sum(sn,3)) ; colormap(jet) ; title(sprintf('normalized integrated sinogram %s',filename)) ;  drawnow ;
        if verbose:
            plt.figure()
            plt.imshow(sn.sum(axis=0), cmap="jet")
            plt.title("Normalized integrated sinogram")
            plt.show()


    # correct for sample movement using edge detection (automatically center of rotation)
    if sample_move_roi is not None:
        sn = correct_sample_movement(sn, sample_move_roi, omega_step, sample_thrs)
        # rot_cen = (size(sn,1)+1)/2 ;
        rot_cen = (sn.shape[1] - 1)/2 # 0-based indices



    # center of rotation
    if c_range is not None:
       sni, rot_cen = sino_center_of_rotation(sn, acq_method, c_range, nomega, y, omega)
    else:
       sni = sn


    # FBP recosntruction
    v = fbp_reconstruction(sni, nomega, vis_rec)

