import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from Viewbox import Viewbox
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_tools import Diffractometer_Tools
from data_display_widget import Data_Display_Widget
from viewfinder_buttons import ViewfinderButtons

class Viewfinder(pg.GraphicsLayoutWidget):
    """
    Displays a feed from a camera as well as stats from the image and ROIs inside.
    """
    def __init__(self, roi_manager: ROI_Manager = None, camera: CameraController = None, diff_tools: Diffractometer_Tools = None):
        super().__init__(parent=None)
        # Set Layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)

        # Instantiate Children
        self.vf_buttons = ViewfinderButtons()
        self.viewbox = Viewbox(ee_roi=roi_manager.ee_roi, bg_roi=roi_manager.bg_roi, diff_tools=diff_tools, centroid_button=self.vf_buttons.centroid_button)
        self.hist = pg.HistogramLUTItem(self.viewbox.main_imi)
        self.stats_display = Data_Display_Widget(roi_manager = roi_manager, camera = camera)

        # Connect Signals
        # From VF Buttons
        self.vf_buttons.reset_roi_button.clicked(self.viewbox.center_rois)

        # Arrange in layout
        self.addItem


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Viewfinder()
    widget.show()
    app.exec()
        