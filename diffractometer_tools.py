import numpy as np
from pyqtgraph.Qt import QtCore
from camera import CameraController
from motor_controller import Motor_Controller
from centering_diff_util import Centering_Monitor
from centering_crosshairs import Crosshairs
from diff_motor_controls import motor_control_widget
from roi_manager import ROI_Manager
from camera_capture import Capture_Manager

class Diffractometer_Tools(QtCore.QObject):
    '''
    Collection of utilities to make use of the diffractometer.
    '''
    def __init__(self, camera: CameraController = None, roi_manager : ROI_Manager = None):
        super().__init__(parent=None)
        self.centered_tolerance = 20
        self.frame_dims = None


        # Instantiate Children
        self.worker_thread = QtCore.QThread()
        self.centering_monitor = Centering_Monitor(camera=camera, roi_manager=roi_manager)
        self.centering_monitor.moveToThread(self.worker_thread)
        self.worker_thread.start()
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
            self.capture_manager = Capture_Manager(camera=camera)
        else:
            print("No camera connected to Diffractometer tools")
        

    def com_received(self, com):
        '''
        Runs whenever the camera gets a new center of mass processed.
        '''
        self.set_spot_pos(com)
        

    def set_spot_pos(self, pos):
        '''
        Saves the last center of mass as the spot position.
        '''
        self.spot_pos = pos



    

