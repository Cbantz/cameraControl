import numpy as np
from pyqtgraph.Qt import QtCore
from camera import CameraController
from motor_controller import Motor_Controller
from centering_diff_util import Centering_Monitor
from centering_crosshairs import Crosshairs
from diff_motor_controls import motor_control_widget
from roi_manager import ROI_Manager
from camera_capture import Capture_Manager
from angle_manager import Angle_Manager
from calibrations import Calibration_Manager

class Diffractometer_Tools(QtCore.QObject):
    '''
    Collection of utilities to make use of the diffractometer.
    '''
    def __init__(self, camera: CameraController = None, roi_manager : ROI_Manager = None):
        super().__init__(parent=None)
        self.frame_dims = None


        # Instantiate Children
        #   Centering
        self.worker_thread = QtCore.QThread()
        self.centering_monitor = Centering_Monitor(camera=camera)
        self.centering_monitor.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.crosshairs = Crosshairs(centering=self.centering_monitor, camera=camera)



        # Set up Motor
        self.motor = None
        try:
            self.motor = Motor_Controller("COM6")
            
        except Exception as e:
            print(e)

        self.motor_control_widget = motor_control_widget(motor=self.motor)


        #   Angle Manager
        self.angle_manager = Angle_Manager(motor_controller=self.motor)

        #   Calibrations
        self.calibration_manager = Calibration_Manager(camera=camera, motor=self.motor)

        # Set up Camera
        if camera:
            self.camera = camera
            self.capture_manager = Capture_Manager(camera=camera, angle_manager=self.angle_manager)
        else:
            print("No camera connected to Diffractometer tools")


        



    

