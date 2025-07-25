import pyqtgraph as pg
from instruments.newport.newportesp301 import NewportESP301
from pyqtgraph.Qt import QtCore, QtWidgets
from angle_manager_widget import Widget
from motor_controller import Motor_Controller

class Angle_Manager(QtCore.QObject):
    grating_pos_offset : float
    camera_pos_offset : float
    
    def __init__(self, motor_controller : Motor_Controller = None):
        super().__init__(parent = None)
        if motor_controller:
            self.cam_stage : NewportESP301.Axis = motor_controller.camera_axis
            self.grating_stage : NewportESP301.Axis = motor_controller.grating_axis
        else:
            print("Stage motors not connected to angle manager.")
        
        self.widget = Widget()
        self.widget.back_ref_button.clicked.connect(self.set_back_angle)
        self.widget.zeroth_order_button.clicked.connect(self.set_zeroth_order)

    def set_back_angle(self):
        self.grating_pos_offset = self.grating_stage.position
        print(f"Set Grating offset: {self.grating_pos_offset}")

    def grating_stage_angle(self) -> float:
        return self.grating_pos_offset - self.grating_stage.position

    def set_zeroth_order(self):
        self.camera_pos_offset = self.cam_stage.position + (2*self.grating_stage_angle())
        print(f"Set Camera offset: {self.camera_pos_offset}")

    def camera_stage_angle(self):
        return self.camera_pos_offset - self.cam_stage.position

    def alpha(self):
        if self.grating_pos_offset:
            return - self.grating_stage_angle()
        
    def beta(self):
        if self.camera_pos_offset:
            print(f"Calculating beta, grating pos: {self.grating_stage_angle()}, camera pos: {self.camera_stage_angle()}")
            return self.camera_stage_angle() - self.grating_stage_angle()

        
    
    