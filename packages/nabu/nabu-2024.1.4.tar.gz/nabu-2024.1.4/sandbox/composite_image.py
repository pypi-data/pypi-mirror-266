import numpy as np
from silx.io import get_data
from nabu.preproc.ccd import Log
from nabu.preproc.flatfield import FlatFieldDataUrls
from nabu.estimation.cor_sino import SinoCor

class SinoRed:
    """
    Class and method to prepare sinogram and calculate COR in HA
    The pseudo sinogram is built with shrinked radios taken every theta degres

        ovs: oversampling horizontaly the radios. Paul use 4. Here 1 is used because float subpixel shift is used instead
        theta: Take a radio every theta degres and its correspondant at 180 degrees.
        yred: resize vertically the radio to yred lines
    """
    def __init__(self, dataset_info, side="right", oversampling=4, theta=10, subsampling_y=10, take_log=True):
                
        self.take_log = take_log
        self.side = side
        self.ovs = oversampling
        self.theta = theta
        self.yred_fact = subsampling_y
        self.dataset_info = dataset_info

        self.nproj = self.dataset_info.n_angles

        self.dproj = round(self.nproj/360*self.theta)
        self.proj_stop = round(self.nproj/(2*self.dproj))+1
        self.sx, self.sy = self.dataset_info.radio_dims
        self.rcor_abs = round(self.sx/2.)
        self.cor_acc = round(self.sx/2.)

        # in this mode, the sinogram will be composed by a succession of 360/dtheta radios
        # 180/dtheta should be integer. sy/syred_fact should be integer
        # The radios themseleves are compressed verticaly by a factor of yred_fact.
        # in the original Paul's algorithm, the radio are horizontally oversampled by 4 to obtain
        # the subpixel precision. Here we prefor to do a float schift on 1/10 pixels to obtain this
        # subprecision.
        
        self.nprojred = 2*self.proj_stop
        self.yred = round(self.sy/self.yred_fact)

        # initialize sinograms and radios arrays
        self.sino = np.zeros((int(self.nprojred * self.yred), self.sx))

        self.projs_indices = np.arange(self.proj_stop)*self.dproj
        self.projs_absolute_indices = sorted(self.dataset_info.projections.keys())

        self.flatfield = FlatFieldDataUrls(
            (len(self.projs_indices), self.sy, self.sx),
            proc.dataset_info.flats,
            proc.dataset_info.darks,
            radios_indices=[self.projs_absolute_indices[i] for i in self.projs_indices],
            dtype=np.float64
        )
        self.mlog = Log(
            (1, ) + self.flatfield.shape,
            clip_min=1e-6,
            clip_max=10.
        )

    def get_radio(self, image_num):
        radio_dataset_idx = self.projs_absolute_indices[image_num]
        data_url = self.dataset_info.projections[radio_dataset_idx]
        radio = get_data(data_url).astype(np.float64)
        self.flatfield.normalize_single_radio(radio, radio_dataset_idx, dtype=radio.dtype)
        if self.take_log:
            self.mlog.take_logarithm(radio)
        return radio
    
    def get_sino(self):
        """
        Build sinogram (composite image) from the radio files
        """
        nradios = np.arange(self.proj_stop)*self.dproj
        np2 = round(self.nproj/2)
        ns2 = round(self.sino.shape[0]/2)
        # loop on all the projections
        irad = 0
        for npi in self.projs_indices:
            radio1 = np.resize(self.get_radio(npi), (self.yred, self.sx))
            radio2 = np.resize(self.get_radio(npi+np2), (self.yred, self.sx))
            
            self.sino[irad:irad+self.yred,:] = radio1
            self.sino[irad+ns2:irad+ns2+self.yred,:] = radio2
            
            irad = irad + self.yred
                
        self.sino[np.isnan(self.sino)] = 0.0001 # ?
        return self.sino
