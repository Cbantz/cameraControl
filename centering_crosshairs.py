import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from centering_diff_util import Centering_Monitor
from camera import CameraController

class Crosshairs(QtCore.QObject):
    """
    Two crosshairs which will light up to signify a centered spot.
    """
    def __init__(self, centering: Centering_Monitor = None, camera : CameraController = None, parent = None):
        super().__init__(parent)

        self.centering = centering
        self.camera = camera
        if(camera):
            roi = camera.camera.get_roi()
            width, height = roi[2], roi[3]
        else:
            print("No Camera Connected to Crosshairs, crosshairs will not function")
            return
        
        if(centering):
            self.tolerance = self.centering.centering_tolerance
            self.h_crosshair = pg.ROI((0,(height/2)-self.tolerance), (width, 2*self.tolerance), movable=False) # Centered on axis with width = tolerance
            self.v_crosshair = pg.ROI(((width/2)-self.tolerance,0), (2*self.tolerance, height), movable = False) 
            # Signal Connections
            self.centering.h_enter_center.connect(self.show_centered_h)
            self.centering.v_enter_center.connect(self.show_centered_v)
            self.centering.h_exit_center.connect(self.reset_pen_h)
            self.centering.v_exit_center.connect(self.reset_pen_v)
        else:
            print("No Centering Monitor connected to crosshairs")


    def show_centered_h(self):
        self.h_crosshair.setPen(pg.mkPen('g'))
    def show_centered_v(self):
        self.v_crosshair.setPen(pg.mkPen('g'))
    def reset_pen_h(self):
        self.h_crosshair.setPen(pg.mkPen('w'))
    def reset_pen_v(self):
        self.v_crosshair.setPen(pg.mkPen('w'))

if __name__ == "__main__":
    app = pg.mkQApp()
    crosshairs = Crosshairs((200, 100), 20)
    print(crosshairs.h_crosshair.pos(), crosshairs.h_crosshair.size())
    print(crosshairs.v_crosshair.pos(), crosshairs.v_crosshair.size())
    app.exec()
