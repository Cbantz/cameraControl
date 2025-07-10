import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np

class EE_GUI_Central_Widget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=True, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.view = pg.ViewBox()
        self.main_imi = pg.ImageItem()
        self.hist = pg.HistogramLUTItem(self.main_imi)

        self.frame_source: QtCore.QObject = None

        self._startup()
        self.create_rois()
        self.setup_data_display

    def _startup(self):
        self.view.addItem(self.main_imi)
        self.addItem(self.view)
        self.addItem(self.hist)

    def _setup_data_display():



    def create_rois(self):
        # Create EE ROI
        self.ee_roi = pg.CircleROI((0,0), size=100, scaleSnap = True, snapSize = 1, translateSnap=True)
        self.ee_roi.removeHandle(0)
        self.ee_roi.addScaleHandle((0, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((0, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.setVisible(False)

        # Create Half ROI
        self.half_roi = pg.CircleROI((0,0), size=1, movable = False)
        self.half_roi.removeHandle(0)

        # Create Background ROI
        self.bg_roi = pg.RectROI((0,0), size=300)
        self.bg_roi.setVisible(False)

        self.view.addItem(self.ee_roi)
        self.view.addItem(self.half_roi)
        self.view.addItem(self.bg_roi)


    def display_new_image(self, image: np.ndarray):
        self.main_imi.setImage(image)


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = EE_GUI_Main_View()
    app.exec()


    