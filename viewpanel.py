import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from Viewbox import Viewbox
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_tools import Diffractometer_Tools
from data_display_widget import Data_Display_Widget
from viewfinder_buttons import ViewfinderButtons
from viewfinder import Viewfinder
from ee_processor import EE_Processor
from displayimageitem import Display_Imi

class ViewPanel(QtWidgets.QWidget):
    '''
    Widget which shows viewfinder, rois, and stats from viewfinder
    '''
    def __init__(self, roi_manager: ROI_Manager = None, camera: CameraController = None, diff_tools: Diffractometer_Tools = None):
        super().__init__(parent=None)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)

        # Instantiate Children


        self.vf_buttons = ViewfinderButtons()
        self.ee_processor = EE_Processor(camera=camera, roi_manager=roi_manager)
        self.viewfinder = Viewfinder(roi_manager=roi_manager, camera=camera, vf_buttons=self.vf_buttons, diff_tools=diff_tools)
        self.data_panel = Data_Display_Widget(roi_manager=roi_manager, ee_processor=self.ee_processor, camera=camera)

        #Connect Signals

            #From Button
        self.vf_buttons.reset_roi_button.clicked.connect(self.viewfinder.viewbox.center_rois)


        # Set Layout
        self.grid_layout.addWidget(self.vf_buttons)
        self.grid_layout.addWidget(self.viewfinder)
        self.grid_layout.addWidget(self.data_panel)

        self.viewfinder.setMinimumHeight(300)
        

if __name__ == "__main__":
    app = pg.mkQApp()
    widget = ViewPanel()
    widget.show()
    app.exec()

