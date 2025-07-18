import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
from centering_crosshairs import Crosshairs
from displayimageitem import Display_Imi
from diffractometer_tools import Diffractometer_Tools
from viewfinder_buttons import ViewfinderButtons
from roi_manager import ROI_Manager
from viewfinder_buttons import ViewfinderButtons
from camera import CameraController
from displayimageitem import Display_Imi

class Viewbox(pg.ViewBox):
    '''
    Viewbox containing rois and crosshairs
    '''
    def __init__(self, roi_manager: ROI_Manager = None, diff_tools : Diffractometer_Tools = None, vf_buttons : ViewfinderButtons = None, imi: Display_Imi = None):
        super().__init__(parent=None, invertY=True)

        # Components
        if imi:
            self.imi=imi
        
        #Set up ROIs
        if roi_manager:
            self.ee_roi = roi_manager.ee_roi
            self.half_roi = self.ee_roi.half_roi
            self.bg_roi = roi_manager.bg_roi
            self.addItem(self.ee_roi)
            self.addItem(self.half_roi)
        else:
            print("No ROI Manager connected to Viewbox")
        
        # Set up Centroid Button
        if vf_buttons:
            self.centroid_button = vf_buttons.centroid_button

        else:
            print("No Viewfinder Buttons connected to Viewbox")

        # Set up Crosshairs
        if diff_tools:
            self.addItem(diff_tools.crosshairs.h_crosshair)
            self.addItem(diff_tools.crosshairs.v_crosshair)
        else:
            print("No Diffractometer Tools connected to Viewbox")

        self.addItem(self.imi)
        

    def centroid(self, com = None):
        '''
        Moves the EE ROI to the scipy center of mass of the current displayed image. Can take provided center of mass. If none provided, will calculate it here.
        '''

        if not com:
            self.ee_roi.set_center_pos(self.imi.com()) # Set center of ee_roi to com of image item

        
        if self.centroid_button.isChecked():
            self.ee_roi.set_center_pos(com)

    def center_rois(self):
        '''
        Will organize and show ROIs according to content being shown. Useful when changing main image focus or type.
        '''

        print("Arranging ROIs")
        x,y = np.shape(self.imi.dims) 

        # ROI parameters
        self.display_crosshairs(x, y, 20)

        roi_bounds = pg.QtCore.QRectF(pg.QtCore.QPoint(0, 0), pg.QtCore.QPoint(x, y)) #ROI bounded to the image size.
        
        # ROI centered in image
        self.ee_roi.set_center_pos(x/2, y/2)
        self.bg_roi.set_in_corner("BR", self.imi.dims())

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