import instruments as ik
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
import numpy as np

class Motor_Controller(QtCore.QObject):
    """
    Basic Newport ESP301 motor controls for diffractometer setup.

    Provides simple movement for a two axis (camera and grating) motor setup. Includes:
        - Indefinite movement.
        - Relative movement.



    """
    esp = ik.newport.NewportESP301
    camera_move_finished = QtCore.Signal()
    grating_move_finished = QtCore.Signal()
    camera_moving : bool = False
    grating_moving : bool = False


    def __init__(self, port):
        super().__init__(parent=None)
        self.controller = self.esp.open_serial(port, baud=921600)
        print("Controller Connected")
        self.connect_controller()
        self.units = 7
        self.setup_axis(self.camera_axis, self.units)
        self.setup_axis(self.grating_axis, self.units)
        self.polling_rate : float = 50
        self.motion_monitor_timer = QtCore.QTimer()
        self.motion_monitor_timer.setSingleShot(False)
        self.motion_monitor_timer.setInterval(self.polling_rate)
        self.motion_monitor_timer.timeout.connect(self.monitor_movement)
        self.motion_monitor_timer.start()
        
    
    def connect_controller(self):
        self.camera_axis : ik.newport.NewportESP301.Axis = self.controller.axis[0]
        self.grating_axis :  ik.newport.NewportESP301.Axis = self.controller.axis[1]
        print("Axes Connected.")
        self.camera_axis.enable()
        self.grating_axis.enable()

    def monitor_movement(self):
        if self.camera_axis.is_motion_done == False:
            self.camera_moving = True
        elif self.camera_moving:
            self.camera_moving = False
            self.camera_move_finished.emit()
            print("Camera Move Finished")

        if self.grating_axis.is_motion_done == False:
            self.grating_moving = True
        elif self.grating_moving:
            self.grating_moving = False
            self.grating_move_finished.emit()
            print("Grating Move Finished")


    def setup_axis(self, axis: ik.newport.NewportESP301.Axis, units: ik.newport.NewportESP301.Axis.units):
        '''
        Configure any axis-specific settings.
        '''
        axis._set_units(units)


    def start_move_cam_indef(self, velocity: float):
        '''
        Starts indefinite movement of the camera axis.

        WARNING:
        Always plan for stopping movement if using this function.
        '''
        print(F"Starting camera move at velocity={velocity}.")
        sign = "+" if velocity > 0 else '-'
        self.camera_axis.velocity = abs(velocity)
        self.camera_axis.move_indefinitely(direction = sign)
        
    

    def end_move_cam(self):
        '''
        Stops movement of the camera axis.
        '''
        self.camera_axis.stop_motion()
        print("Stopping Camera.")

    def start_move_grating(self, velocity):
        '''
        Starts indefinite movement of the grating axis.

        WARNING:
        Always plan for stopping movement if using this function.
        '''
        print(f"Starting Grating move at velocity={velocity}")
        sign = "+" if velocity > 0 else "-"
        self.grating_axis.velocity = abs(velocity)
        self.grating_axis.move_indefinitely(direction=sign)
        

    def end_move_grating(self):
        '''
        Ends any movement of the grating axis.
        '''
        self.grating_axis.stop_motion()
        print("Stopping Grating")

    def rel_move_cam(self, distance: float, blocking: bool = False):
        '''
        Rotates the camera axis a given amount.
        '''
        print(f"Camera relative move of {distance}")
        self.camera_axis.move(distance, absolute=False, block=blocking)
        print(self.camera_axis.velocity)

    def rel_move_grating(self, distance, blocking: bool = False):
        '''
        Rotates the grating axis a given amount.
        '''
        print(f"Grating relative move of {distance}")
        self.grating_axis.move(distance, absolute=False, block=blocking)

    def abs_move_cam(self, distance: float, blocking: bool = False):
        '''
        Rotates the camera axis to a given angle.
        '''
        print(f"Camera absolute move of {distance}")
        self.camera_axis.move(distance, absolute=True, block=blocking)
        print(self.camera_axis.velocity)

    def abs_move_grating(self, position, blocking: bool = False):
        '''
        Rotates the grating axis to a given angle.
        '''
        print(f"Grating absolute move of {position}")
        self.grating_axis.velocity = 0.5
        self.grating_axis.move(position, absolute=True, block=blocking)
    
    def abort_movement(self):
        '''
        Sends the abort command to the controller for both axes.

        WARNING:
        This will raise an error from the controller. Try not to use it unless regular stopping fails or was not implemented.
        '''
        self.camera_axis.abort_motion()
        self.grating_axis.abort_motion()
        print("Movement Aborted.")

    

if __name__ == '__main__':
    mc = Motor_Controller("COM6")