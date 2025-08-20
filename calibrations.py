import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from camera import CameraController
from motor_controller import Motor_Controller
from distance import Distance_Scanner
from stability import Stability_Check
from backlash import Backlash_Calibration
from spot_size_live import spot_size_live
from roi_manager import ROI_Manager


class Calibration_Manager(QtWidgets.QGroupBox):
    def __init__(self, camera: CameraController = None, motor: Motor_Controller = None, roi_manager : ROI_Manager = None):
        super().__init__(parent=None)
        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)
        self.stability_checker = Stability_Check(camera=camera)
        self.distance_scanner = Distance_Scanner(camera=camera, motor=motor)
        self.backlash_check = Backlash_Calibration(camera=camera, motor=motor)
        # Spot Size
        self.half_size_tracker_button = QtWidgets.QPushButton("Spot Size Graph")
        self.half_size_tracker_button.clicked.connect(lambda: setattr(self, "spot_size_tracker", spot_size_live(roi_manager=roi_manager)))
        self.gridlayout.addWidget(self.stability_checker.track_button)
        self.gridlayout.addWidget(self.distance_scanner.button)
        self.gridlayout.addWidget(self.backlash_check.button)
        self.gridlayout.addWidget(self.half_size_tracker_button)
        self.show()