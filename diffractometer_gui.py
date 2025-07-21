import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from camera import CameraController
from roi_manager import ROI_Manager
from diffractometer_tools import Diffractometer_Tools
from viewpanel import ViewPanel
class Diffractometer_GUI(QtWidgets.QWidget):
    """
    Central widget for diffractometer control GUI.
    """
    def __init__(self, camera: CameraController = None, roi_manager: ROI_Manager = None):
        super().__init__(parent=None)
        self.parent_layout = QtWidgets.QGridLayout()
        self.setLayout(self.parent_layout)


        #Instantiate Children
        self.diff_tools = Diffractometer_Tools(camera=camera)
        self.viewpanel = ViewPanel(roi_manager=roi_manager, camera=camera, diff_tools=self.diff_tools)

        # Arrange Layout
        self.parent_layout.addWidget(self.viewpanel)
        self.parent_layout.addWidget(self.diff_tools.motor_control_widget)


if __name__ == "__main__":
    app = pg.mkQApp()
    ROIs = ROI_Manager()
    camera = CameraController(roi_manager=ROIs)
    widget = Diffractometer_GUI(camera=camera, roi_manager=ROIs)
    widget.show()
    app.exec()

    