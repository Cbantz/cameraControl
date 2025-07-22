import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from camera import CameraController
from roi_manager import ROI_Manager
from scipy.ndimage import center_of_mass



class Centering_Monitor(QtCore.QObject):
    '''
    Monitors whether a spot of light is centered or not.

    Checks each processed frame from camera and determines if the spot enters or exits the bounds of centering tolerance.
    '''
    h_enter_center = QtCore.Signal()
    h_exit_center = QtCore.Signal()
    v_enter_center = QtCore.Signal()
    v_exit_center = QtCore.Signal()
    is_y_centered = False
    is_x_centered = False


    def __init__(self, camera: CameraController, tolerance: int = 20, roi_manager: ROI_Manager = None):
        super().__init__(parent=None)
        self.centering_tolerance = tolerance
        if camera:
            self.camera = camera
            self.imi = camera.imi
            self.roi = self.camera.camera.get_roi()
        else:
            print("No Camera connected to Centering utility")
        
        if roi_manager:
            self.ee_roi = roi_manager.ee_roi
            self.center_roi = self.ee_roi.center_roi

            self.centroid_button = QtWidgets.QPushButton("Centroid")
            self.centroid_button.setCheckable(True)

            self.inner_com_check = QtWidgets.QCheckBox("Use Whole Frame for Centering")
            self.inner_com_check.checkStateChanged.connect(self.use_inner_changed)

            self.camera.worker.com_ready.connect(self.com_received)
        else:
            print("No ROI Manager connected to Centering utility")

    def com_received(self, com):
        if self.centroid_button.isChecked():
            self.ee_roi.set_center_pos(com)
        if self.inner_com_check.isChecked():
            inner_com = center_of_mass(self.ee_roi.getArrayRegion(self.imi.image, self.imi))
            ee_pos = self.ee_roi.pos()
            com = (ee_pos[0] + inner_com[1], ee_pos[1] + inner_com[0])
            
            self.ee_roi.center_roi.set_center_pos(com)
                
 
        self.check_centered(com)

    def check_centered(self, com: tuple):
        '''
        Checks position of spot in relation to center of both axes. Emits appropriate signal if spot has entered or exited a center.
        '''
        width, height = self.roi[2], self.roi[3]
        center_x, center_y = width/2, height/2
        com_x, com_y = com[0], com[1]
        self.x_centered = np.abs(center_x - com_x) < self.centering_tolerance
        self.y_centered = np.abs(center_y - com_y) < self.centering_tolerance
        if self.y_centered and not self.is_y_centered:
            self.h_enter_center.emit()
            self.is_y_centered = True
        if self.x_centered and not self.is_x_centered:
            self.v_enter_center.emit()
            self.is_x_centered = True
        if not self.y_centered and self.is_y_centered:
            self.h_exit_center.emit()
            self.is_y_centered = False
        if not self.x_centered and self.is_x_centered:
            self.is_x_centered = False
            self.v_exit_center.emit()

    def use_inner_changed(self):
        if self.inner_com_check.isChecked():
            self.ee_roi.center_roi.setVisible(True)
        else:
            self.ee_roi.center_roi.setVisible(False)

