import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from astropy.io import fits
import numpy as np

class Static_Image_Handler(QtCore.QObject):

    static_frame_ready = QtCore.Signal(np.ndarray)
    is_active = True

    def __init__(self, parent = None):
        super().__init__(parent)

    def set_bg_roi(self, roi: pg.ROI):
        self.bg_roi = roi
        self.bg_roi.sigRegionChanged.connect(self._bg_region_changed)
    
    def set_imi(self, imi: pg.ImageItem):
        self.imi = imi

    def set_active(self, should_be_active: bool = True):
        self.is_active = should_be_active

    def load_image(self, filepath: str):
        
        hdul = fits.open(filepath)
        header, data = hdul[0].header, hdul[0].data
        self.raw_im = data
        print(f"Loading Image {filepath}, {np.shape(self.raw_im)}")
        self.send_frame()

    def _bg_region_changed(self):
        self.send_frame()
    
    def send_frame(self):
        if(self.is_active):
            bg_region = self.bg_roi.getArrayRegion(self.raw_im, self.imi)
            bg_sub_frame = self.raw_im - np.average(bg_region)
            bg_sub_frame[bg_sub_frame < 0] = 0
            self.static_frame_ready.emit(bg_sub_frame)

    def end_process(self):
        self.is_active = False



if __name__ == "__main__":
    object = Static_Image_Handler()