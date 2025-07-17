import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from camera import CameraController
from data_display_widget import Data_Display_Widget
from diffractometer_controller_gui import dt_window
from roi_manager import ROI_Manager
from diffractometer_tools import Diffractometer_Tools
from viewfinder import Viewfinder

class Diffractometer_GUI(QtWidgets.QWidget):
    def __init__(self, camera: CameraController, roi_manager: ROI_Manager):
        super().__init__(parent=None)
        self.dt = Diffractometer_Tools(camera)
        self.viewfinder = Viewfinder()

    