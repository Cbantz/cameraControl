import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from roi_manager import EE_ROI
from displayimageitem import Display_Imi
from scipy.ndimage import center_of_mass
import numpy as np

class Spot_Tracker(QtCore.QObject):
    focused_com_update = QtCore.Signal(tuple)
    current_com : tuple = None
    def __init__(self, imi : Display_Imi, ee_roi: EE_ROI):
        super().__init__(parent=None)
        self.imi = imi
        self.ee_roi = ee_roi
        self.centroid_button = QtWidgets.QPushButton("Centroid")
        self.centroid_button.setCheckable(True)
        self.inner_com_check = QtWidgets.QCheckBox("Center Inside ROI Only")

    def get_com(self, frame: np.ndarray):
        com_full = center_of_mass(frame)
        com = (com_full[1], com_full[0])
        if self.centroid_button.isChecked():
            self.ee_roi.set_center_pos(com)
        if self.inner_com_check.isChecked():
            inner_com = center_of_mass(self.ee_roi.getArrayRegion(frame, self.imi))
            ee_pos = self.ee_roi.pos()
            com = (ee_pos[0] + inner_com[1], ee_pos[1] + inner_com[0])
            

        self.focused_com_update.emit(com)
        self.current_com = com
        self.ee_roi.center_roi.set_center_pos(com)


