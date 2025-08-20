import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from roi_manager import ROI_Manager
from camera import CameraController
import time

class spot_size_live(pg.PlotWidget):
    def __init__(self, roi_manager: ROI_Manager = None):
        super().__init__(parent = None)

        if roi_manager:
            self.half_roi = roi_manager.ee_roi.half_roi
            self.half_roi.resized.connect(self.new_size)
        else:
            print("No ROI Manager connected to Spot size live")
        
        self.times = []
        self.sizes = []
        self.start_time = time.time()
        self.plot : pg.PlotDataItem = self.plotItem.plot([], [], symbol='o')
        self.show()

    def new_size(self, radius):
        new_time = time.time()
        time_since_start = new_time - self.start_time
        self.times.append(time_since_start)
        self.sizes.append(radius)
        self.plot.setData(self.times, self.sizes)
        current_time = self.times[-1]
        self.setXRange(current_time - 5, current_time)
        
        
        