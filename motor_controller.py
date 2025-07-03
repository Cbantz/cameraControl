import instruments as ik
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui

class Motor_Controller(QtCore.QObject):
    esp = ik.newport.NewportESP301
    def __init__(self, port):
        self.controller = self.esp.open_serial(port)
    
    def connect(self):
        self.camera_axis = self.controller.axis[0]
        self.grating_axis = self.controller.axis[1]
        self.camera_axis.enable()
        self.grating_axis.enable()

    

    

