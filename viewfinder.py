import pyqtgraph as pg
from Viewbox import Viewbox
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_tools import Diffractometer_Tools
from viewfinder_buttons import ViewfinderButtons

class Viewfinder(pg.GraphicsLayoutWidget):
    """
    Displays a feed from a camera with a histogram.
    """
    def __init__(self, roi_manager: ROI_Manager = None, camera: CameraController = None, diff_tools: Diffractometer_Tools = None, vf_buttons : ViewfinderButtons = None):
        super().__init__(parent=None)

        # Instantiate Children
        if camera:
            imi = camera.imi
        else:
            print("No Camera connected to Viewfinder")
            imi = None
        self.viewbox = Viewbox(roi_manager=roi_manager, diff_tools=diff_tools, camera=camera)
        self.hist = pg.HistogramLUTItem(imi)
        self.hist.setHistogramRange(0, 65535) # Max pixel value in RAW16

        # Arrange in layout
        self.addItem(self.viewbox)
        self.addItem(self.hist)

        


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Viewfinder()
    widget.show()
    app.exec()
        