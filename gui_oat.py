import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from main_win_gui_oat import MainWindow
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_gui import Diffractometer_GUI

class GUI_OAT(QtCore.QObject):
    def __init__(self, roi_manager: ROI_Manager, camera: CameraController):
        super().__init__(parent = None)
        
        self.diff_gui = Diffractometer_GUI(camera, roi_manager)
        self.main_win = MainWindow()


