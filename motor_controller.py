import instruments as ik
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from signals import signals as sig
import numpy as np

class Motor_Controller(QtCore.QObject):
    esp = ik.newport.NewportESP301



    def __init__(self, port):
        self.controller = self.esp.open_serial(port, baud=921600)
        print("Controller Connected")
        self.connect()
        self.units = 7
        self.setup_axis(self.camera_axis, self.units)
        self.setup_axis(self.grating_axis, self.units)
    
    def connect(self):
        self.camera_axis = self.controller.axis[0]
        self.grating_axis = self.controller.axis[1]
        print("Axes Connected.")
        self.camera_axis.enable()
        self.grating_axis.enable()
        print(f"Max velocity cam: {self.camera_axis.read_setup()['max_velocity']}")
        print(f"grating: {self.grating_axis.read_setup()}")

    def setup_axis(self, axis: ik.newport.NewportESP301.Axis, units: ik.newport.NewportESP301.Axis.units):
        axis._set_units(units)


    def start_move_cam_indef(self, velocity):
        print(F"Starting camera move at velocity={velocity}.")
        sign = "+" if velocity > 0 else '-'
        self.camera_axis.velocity = abs(velocity)
        self.camera_axis.move_indefinitely(direction = sign)
        
    

    def end_move_cam(self):
        self.camera_axis.stop_motion()
        print("Stopping Camera.")

    def start_move_grating(self, velocity):
        print(f"Starting Grating move at velocity={velocity}")
        sign = "+" if velocity > 0 else "-"
        self.grating_axis.velocity = abs(velocity)
        self.grating_axis.move_indefinitely(direction=sign)
        

    def end_move_grating(self):
        self.grating_axis.stop_motion()
        print("Stopping Grating")

    def rel_move_cam(self, distance):
        print(f"Camera relative move of {distance}")
        self.camera_axis.move(distance, absolute=False)
        print(self.camera_axis.velocity)

    def rel_move_grating(self, distance):
        print(f"Grating relative move of {distance}")
        self.grating_axis.move(distance, absolute=False)
    
    def abort_movement(self):
        self.camera_axis.abort_motion()
        self.grating_axis.abort_motion()
        print("Movement Aborted.")

    

if __name__ == '__main__':
    mc = Motor_Controller("COM6")