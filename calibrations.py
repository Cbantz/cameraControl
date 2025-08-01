import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from camera import CameraController
from motor_controller import Motor_Controller
from distance import Distance_Scanner
from stability import Stability_Check


class Calibration_Manager(QtWidgets.QGroupBox):
    def __init__(self, camera: CameraController = None, motor: Motor_Controller = None):
        super().__init__(parent=None)
        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)
        self.stability_checker = Stability_Check(camera=camera)
        self.distance_scanner = Distance_Scanner(camera=camera, motor=motor)
        self.gridlayout.addWidget(self.stability_checker.track_button)
        self.gridlayout.addWidget(self.distance_scanner.button)
        self.show()