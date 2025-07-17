import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
from viewcrosshairs import Crosshairs
from eeroi import EE_ROI, Half_ROI
from bg_roi import Background_ROI
from displayimageitem import Display_Imi
from diffractometer_tools import Diffractometer_Tools
from viewfinder_buttons import ViewfinderButtons
from roi_manager import ROI_Manager

class Viewbox(pg.ViewBox):
    '''
    Viewbox containing rois and crosshairs
    '''
    def __init__(self, roi_manager: ROI_Manager = None, crosshairs : Crosshairs = None, diff_tools : Diffractometer_Tools = None, centroid_button: QtWidgets.QPushButton = None):
        super().__init__(parent=None, invertY=True)

        # Components
        self.main_imi = Display_Imi()
        
        #Set up ROIs
        if roi_manager:
            self.ee_roi = roi_manager.ee_roi
            self.half_roi = self.ee_roi.half_roi
            self.bg_roi = roi_manager.bg_roi
            self.addItem(self.ee_roi)
            self.addItem(self.half_roi)
        else:
            print("No ROI Manager Passed to Viewbox")
        
        # Set up Centroid Button
        if centroid_button:
            self.centroid_button = centroid_button

        else:
            print("No Centroid Button connected to Viewbox")

        self.crosshairs = crosshairs

        self.addItem(self.main_imi)
        

    def centroid(self, com = None):
        '''
        Moves the EE ROI to the scipy center of mass of the current displayed image. Can take provided center of mass. If none provided, will calculate it here.
        '''

        if not com:
            self.ee_roi.set_center_pos(self.main_imi.com()) # Set center of ee_roi to com of image item

        
        if self.centroid_button.isChecked():
            self.ee_roi.set_center_pos(com)

    def center_rois(self):
        '''
        Will organize and show ROIs according to content being shown. Useful when changing main image focus or type.
        '''

        print("Arranging ROIs")
        x,y = np.shape(self.main_imi.dims) 

        # ROI parameters
        self.display_crosshairs(x, y, 20)

        roi_bounds = pg.QtCore.QRectF(pg.QtCore.QPoint(0, 0), pg.QtCore.QPoint(x, y)) #ROI bounded to the image size.
        
        # ROI centered in image
        self.ee_roi.set_center_pos(x/2, y/2)
        self.bg_roi.set_in_corner("BR", self.main_imi.dims())

        # Set ROI Bounds
        self.ee_roi.maxBounds = roi_bounds
        self.bg_roi.maxBounds = roi_bounds

        #Show ROIs
        self.ee_roi.setVisible(True)
        self.bg_roi.setVisible(True)

    def display_crosshairs(self, x, y, width):
        if(not self.crosshairs):
            self.crosshairs = Crosshairs((x, y), width)
            self.addItem(self.crosshairs.h_crosshair)
            self.addItem(self.crosshairs.v_crosshair)
        else:
            self.removeItem(self.crosshairs.h_crosshair)
            self.removeItem(self.crosshairs.v_crosshair)
            self.crosshairs.set_size((x, y), width)
            self.addItem(self.crosshairs.h_crosshair)
            self.addItem(self.crosshairs.v_crosshair)




if __name__ == "__main__":
    app=pg.mkQApp()
    view = Viewbox()
    view.show()
    app.exec()