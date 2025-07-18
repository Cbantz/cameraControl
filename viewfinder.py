import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from Viewbox import Viewbox
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_tools import Diffractometer_Tools
from data_display_widget import Data_Display_Widget
from viewfinder_buttons import ViewfinderButtons
from displayimageitem import Display_Imi

class Viewfinder(pg.GraphicsLayoutWidget):
    """
    Displays a feed from a camera with a histogram
    """
    def __init__(self, roi_manager: ROI_Manager = None, camera: CameraController = None, diff_tools: Diffractometer_Tools = None, vf_buttons : ViewfinderButtons = None, imi: Display_Imi = None):
        super().__init__(parent=None)

        # Instantiate Children
        
        self.viewbox = Viewbox(roi_manager=roi_manager, diff_tools=diff_tools, vf_buttons = vf_buttons, imi=imi)
        self.hist = pg.HistogramLUTItem(imi)
        self.hist.setHistogramRange(0, 65545) # Max pixel value in RAW16

        # Arrange in layout
        self.addItem(self.viewbox)
        self.addItem(self.hist)

        


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Viewfinder()
    widget.show()
    app.exec()
        