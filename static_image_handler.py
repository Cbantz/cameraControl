import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from astropy.io import fits
import numpy as np

class Static_Image_Handler(QtCore.QObject):

    static_frame_ready = QtCore.Signal(np.ndarray) # Emits whenever a new static frame is processed
    is_active = True # Starts up active

    def __init__(self, parent = None):
        super().__init__(parent)

    def set_bg_roi(self, roi: pg.ROI):
        '''
        Sets Background ROI to be used in processing frame.
        '''
        self.bg_roi = roi
        self.bg_roi.sigRegionChanged.connect(self._bg_region_changed)
    
    def set_imi(self, imi: pg.ImageItem):
        '''
        Sets Image Item to be used in processing frame.
        '''
        self.imi = imi

    def set_active(self, should_be_active: bool = True):
        '''
        Sets the Image Handler to be active or not.
        '''
        self.is_active = should_be_active

    def load_image(self, filepath: str):
        '''
        Loads a new fits image from the given filepath.
        '''
        hdul = fits.open(filepath)
        header, data = hdul[0].header, hdul[0].data
        self.raw_im = data
        print(f"Loading Image {filepath}, {np.shape(self.raw_im)}")
        self.send_frame()

    def _bg_region_changed(self):
        '''
        Runs whenever the set background region changes. Re-processes the frame.
        '''
        self.send_frame()
    
    def send_frame(self):
        '''
        Subtracts frame and sends processed frame through a signal.
        '''
        if(self.is_active):
            bg_region = self.bg_roi.getArrayRegion(self.raw_im, self.imi)
            bg_sub_frame = self.raw_im - np.average(bg_region)
            bg_sub_frame[bg_sub_frame < 0] = 0
            self.static_frame_ready.emit(bg_sub_frame)



if __name__ == "__main__":
    object = Static_Image_Handler()