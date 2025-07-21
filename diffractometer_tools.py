import numpy as np
from pyqtgraph.Qt import QtCore
from camera import CameraController
from motor_controller import Motor_Controller
from centering_diff_util import Centering_Monitor
from centering_crosshairs import Crosshairs
from diff_motor_controls import motor_control_widget

class Diffractometer_Tools(QtCore.QObject):
    '''
    Collection of utilities to make use of the diffractometer.
    '''
    def __init__(self, camera: CameraController = None):
        super().__init__(parent=None)
        self.centered_tolerance = 20
        self.frame_dims = None


        # Instantiate Children
        self.centering_monitor = Centering_Monitor(camera)
        self.crosshairs = Crosshairs(centering=self.centering_monitor, camera=camera)

        # Set up Motor
        self.motor = None
        try:
            self.motor = Motor_Controller()
        except Exception as e:
            print(e)

        self.motor_control_widget = motor_control_widget(motor=self.motor)

        # Set up Camera
        if camera:
            self.camera = camera
            self.camera.worker.com_ready.connect(self.com_received)
            self.camera.worker.frame_ready.connect(self.frame_received)
        else:
            print("No camera connected to Diffractometer tools")
        

    def com_received(self, com):
        '''
        Runs whenever the camera gets a new center of mass processed.
        '''
        self.set_spot_pos(com)
        self.centering_monitor.check_centered(com=com)
        

    def set_spot_pos(self, pos):
        '''
        Saves the last center of mass as the spot position.
        '''
        self.spot_pos = pos



    

