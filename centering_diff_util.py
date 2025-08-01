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


    def __init__(self, camera: CameraController, tolerance: int = 5):
        super().__init__(parent=None)
        self.centering_tolerance = tolerance
        if camera:
            self.camera = camera
            self.imi = camera.imi
            self.roi = self.camera.camera.get_roi()
            self.camera.worker.spot_tracker.focused_com_update.connect(self.com_received)
        else:
            print("No Camera connected to Centering utility")
        

            


    def com_received(self, com):
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


