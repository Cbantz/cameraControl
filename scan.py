import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from instruments.newport import NewportESP301
from motor_controller import Motor_Controller
from camera_capture import Capture_Manager

class Scan_Manager(QtCore.QObject):
    def __init__(self, capture_manager : Capture_Manager = None, motor : Motor_Controller = None):
        super().__init__(parent = None)
        self.button = QtWidgets.QPushButton("Start Scan")
        self.sample_name_box = QtWidgets.QTextEdit()
        
