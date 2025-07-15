import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from scipy.ndimage import center_of_mass
import numpy as np
from viewcrosshairs import Crosshairs

class EE_Gui_Main_View(pg.ViewBox):
    '''
    The main view widget of the EEGUI. Can show a live feed of the camera or a static image. Contains statistics about the frame displayed.
    '''
    def __init__(self, parent=None, border=None, lockAspect=True, enableMouse=True, invertY=True, enableMenu=True, name=None, invertX=False, defaultPadding=0.02):
        super().__init__(parent, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX, defaultPadding)

        # Components
        self.main_imi = pg.ImageItem(axisOrder='row-major')
        self.addItem(self.main_imi)
        self.centroid_button = None
        self.crosshairs = None

        self.create_rois()
        


    
    
    def create_rois(self):
        '''
        Runs on startup. Creates the ee, half, and bkg ROIs.
        '''
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

        self.addItem(self.ee_roi)
        self.addItem(self.half_roi)
        self.addItem(self.bg_roi)

        self.display_crosshairs(1, 1, 1)

    def display_new_image(self, image: np.ndarray):
        '''
        Displays frame argument in the main view.
        '''
        self.main_imi.setImage(image)

    def centroid(self, com = None):
        '''
        Moves the EE ROI to the scipy center of mass of the current displayed image. Can take provided center of mass. If none provided, will calculate it here.
        '''

        if not com:
            com = center_of_mass(self.main_imi.image)
            offset = self.ee_roi.size().x() / 2 #Adjust for 'pos' controlling the top left corner of the ROI
            centered_pos = (com[1]-offset, com[0] - offset)
            self.ee_roi.setPos(centered_pos) # Centers ROI because position is based on top right

        elif self.centroid_button is not None:
            if self.centroid_button.isChecked():
                offset = self.ee_roi.size().x() / 2 #Adjust for 'pos' controlling the top left corner of the ROI
                centered_pos = (com[1]-offset, com[0] - offset)
                self.ee_roi.setPos(centered_pos) # Centers ROI because position is based on top right

    def center_rois(self):
        '''
        Will organize and show ROIs according to content being shown. Useful when changing main image focus or type.
        '''

        print("Arranging ROIs")
        x,y = np.shape(self.main_imi.image) 

        # ROI parameters
        roi_size = self.ee_roi.size()[0]
        roi_pos = ((y - roi_size) / 2, (x - roi_size) / 2)  # Centered position
        self.display_crosshairs(x, y, 20)

        roi_bounds = pg.QtCore.QRectF(pg.QtCore.QPoint(0, 0), pg.QtCore.QPoint(y, x)) #ROI bounded to the image size.
        
        # ROI centered in image
        self.ee_roi.setPos(roi_pos)
        self.bg_roi.setPos((y - self.bg_roi.size().y(), x-self.bg_roi.size().y()))

        # Set ROI Bounds
        self.ee_roi.maxBounds = roi_bounds
        self.bg_roi.maxBounds = roi_bounds

        #Show ROIs
        self.ee_roi.setVisible(True)
        self.bg_roi.setVisible(True)

    def set_half_roi_pos(self):
        '''
        Repositions the half ROI to be in the center of the ee ROI
        '''
        ee_x, ee_y = self.ee_roi.pos()
        ee_size = self.ee_roi.size()[0]
        half_size = self.half_roi.size()[0]
        self.half_roi.setPos(ee_x + (ee_size-half_size)/2, ee_y + (ee_size-half_size)/2)

    def set_half_roi_size(self, radius):
        '''
        Resizes the half ROI. Should only be accessed by a signal from the EE Worker.
        '''
        self.half_roi.setSize(radius * 2, center=(0.5,0.5))

    def _set_centroid_button(self, button: QtWidgets.QPushButton):
        '''
        Sets centroid button to be used by centroid function.
        '''
        self.centroid_button = button

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
    view = EE_Gui_Main_View()
    view.show
    app.exec()