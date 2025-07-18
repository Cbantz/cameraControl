import numpy as np
from pyqtgraph.Qt import QtCore
from camera import CameraController

class Centering_Monitor(QtCore.QObject):
    '''
    Checks state of centered and manages crosshairs
    '''
    h_enter_center = QtCore.Signal()
    h_exit_center = QtCore.Signal()
    v_enter_center = QtCore.Signal()
    v_exit_center = QtCore.Signal()
    is_y_centered = False
    is_x_centered = False
    def __init__(self, camera: CameraController, tolerance: int = 20):
        super().__init__(parent=None)
        self.centering_tolerance = tolerance
        if camera:
            self.camera = camera
            self.roi = self.camera.camera.get_roi()
        else:
            print("No Camera connected to Centering utility")
        


    def check_centered(self, com: tuple):
        
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

