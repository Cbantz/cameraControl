import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np
from photutils.aperture import CircularAperture

class EE_Worker(QtCore.QObject):
    is_busy: bool = False # Can take a new frame
    ee_ready = QtCore.Signal(float, float, float) # Results of calculations
    half_ready = QtCore.Signal(int) # Results
    completed = QtCore.Signal() # Used to check for a new frame

    def __init__(self, parent = None):
        super().__init__(parent)

    def set_ee_roi(self, roi: pg.ROI):
        self.ee_roi = roi
    
    def set_image_item(self, imi: pg.ImageItem):
        self.imi = imi

    def calculate_ee(self):

        frame = self.imi.image
        self.is_busy = True
        total_sum = np.sum(frame)

        roi_region = self.ee_roi.getArrayRegion(frame, self.imi)
        ee = np.sum(roi_region)

        ee_pc_enc = ee/total_sum
        '''
        Returns the radius from center of ee_roi necessary to encircle 50% energy of the ee_roi
        '''
        r_min = 1
        r_max = np.shape(roi_region)[0]/2 # Max radius to be searched (half of size(diameter))

        # Calculate half by splitting radius search in half until possible is only one pixel
        while r_max-r_min > 1:
            r_mid = (r_max+r_min)/2
            aperture = CircularAperture((np.shape(roi_region)[0]/2,np.shape(roi_region)[1]/2), r = r_mid)
            aperture_counts = aperture.do_photometry(roi_region, method='center')[0]
            try:
                pc_enc = aperture_counts / ee
                if(pc_enc > 0.5):
                    r_max = r_mid
                else:
                    r_min = r_mid
            except RuntimeWarning as e:
                print("There are no counts enclosed")
        
        self.is_busy = False
        
        self.half_ready.emit(r_mid)
        self.ee_ready.emit(ee, ee_pc_enc, total_sum)
        self.completed.emit()
        
  




