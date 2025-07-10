import instruments as ik
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from signals import signals as sig

class Motor_Controller(QtCore.QObject):
    esp = ik.newport.NewportESP301
    def __init__(self, port):
        self.controller = self.esp.open_serial(port, baud=921600)
        print("Controller Connected")
        self.connect()
        print(ik.newport.NewportESP301Axis._unit_dict)
        self.units = 7
        self.setup_axis(self.camera_axis, self.units)
        self.setup_axis(self.grating_axis, self.units)
        sig.motor_abort_req.connect(self.abort_movement)
        sig.motor_move_camera_indef_req.connect(self.start_move_cam_indef)
        sig.motor_stop_camera_req.connect(self.end_move_cam)
    
    def connect(self):
        self.camera_axis = self.controller.axis[0]
        self.grating_axis = self.controller.axis[1]
        print("Axes Connected.")
        self.camera_axis.enable()
        self.grating_axis.enable()

    def setup_axis(self, axis: ik.newport.NewportESP301Axis, units: ik.newport.NewportESP301Axis.units):
        axis._set_units(units)


    def start_move_cam_indef(self, velocity):
        self.camera_axis.velocity = velocity
        self.camera_axis.move_indefinitely()
        print(F"Starting camera move at velocity={velocity}.")
    

    def end_move_cam(self):
        self.camera_axis.stop_motion()
        print("Stopping Camera.")
    
    def abort_movement(self):
        self.camera_axis.abort_motion()
        self.grating_axis.abort_motion()
        print("Movement Aborted.")

    

if __name__ == '__main__':
    mc = Motor_Controller("COM6")