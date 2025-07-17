import numpy as np
from pyqtgraph.Qt import QtCore
from camera import CameraController
from motor_controller import Motor_Controller

class Diffractometer_Tools(QtCore.QObject):
    '''
    Collection of utilities to make use of the diffractometer motors and, a camera.
    '''
    h_enter_center = QtCore.Signal()
    h_exit_center = QtCore.Signal()
    v_enter_center = QtCore.Signal()
    v_exit_center = QtCore.Signal()
    def __init__(self, camera: CameraController):
        super().__init__(parent=None)
        self.centered_tolerance = 20
        self.frame_dims = None
        self.is_y_centered = False
        self.is_x_centered = False

        # Set up Motor
        try:
            self.motor = Motor_Controller()
        except Exception as e:
            print(e)

        # Set up Camera
        if camera:
            self.camera = camera
            self.camera.worker.com_ready.connect(self.com_received)
            self.camera.worker.frame_ready.connect(self.frame_received)
            self.cam.frame_ready.connect(self.frame_received)
        else:
            print("No camera connected to Diffractometer tools")
        

    def com_received(self, com):
        '''
        Runs whenever the camera gets a new center of mass processed.
        '''
        self.set_spot_pos(com)
        self.check_for_centered(self.frame_dims, self.spot_pos)
        
    
    def frame_received(self, frame):
        dims = np.shape(frame)
        if dims == self.frame_dims:
            return
        else:
            self.frame_dims = dims

    def set_spot_pos(self, pos):
        '''
        Saves the last center of mass as the spot position.
        '''
        self.spot_pos = pos

    def check_for_centered(self, frame_dims : tuple, com: tuple):
        dim_y = frame_dims[0]
        dim_x = frame_dims[1]
        com_x = com[1]
        com_y = com[0]
        center_y = dim_y/2
        center_x = dim_x/2
        x_centered = np.abs(center_x - com_x) < self.centered_tolerance
        y_centered = np.abs(center_y - com_y) < self.centered_tolerance
        if y_centered and not self.is_y_centered:
            self.h_enter_center.emit()
            self.is_y_centered = True
        if x_centered and not self.is_x_centered:
            self.v_enter_center.emit()
            self.is_x_centered = True
        if not y_centered and self.is_y_centered:
            self.h_exit_center.emit()
            self.is_y_centered = False
        if not x_centered and self.is_x_centered:
            self.is_x_centered = False
            self.v_exit_center.emit()




    

