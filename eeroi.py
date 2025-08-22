import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np

class EE_ROI(pg.CircleROI):
    def __init__(self, pos, size=None, radius=100, scaleSnap=True, translateSnap=True):
        super().__init__(pos, size, radius=radius, scaleSnap=scaleSnap, translateSnap=translateSnap)
        self.snapSize = 1
        self.removeHandle(0)
        self.addScaleHandle((0, 0), (0.5, 0.5), lockAspect=True)
        self.addScaleHandle((1, 0), (0.5, 0.5), lockAspect=True)
        self.addScaleHandle((0, 1), (0.5, 0.5), lockAspect=True)
        self.addScaleHandle((1, 1), (0.5, 0.5), lockAspect=True)
        self.half_roi = Half_ROI(pos, size, radius, ee_roi=self)
        self.sigRegionChanged.connect(self.half_roi.center_rel_ee)
        self.center_roi = Center_Spot((0,0))
        self.setVisible(True)
        self.half_roi.setVisible(True)
        self.center_roi.setVisible(True)

    def set_center_pos(self, pos:tuple):
        x,y = pos[0],pos[1]
        radius = self.size().x()/2
        centered_pos = (x-radius, y-radius)
        self.setPos(centered_pos)
   
    def get_center_pos(self) -> tuple:
        radius = self.size().x()/2
        (x, y) = self.pos()
        centered_pos = (x - radius, y-radius)
        return centered_pos

class Half_ROI(pg.CircleROI):
    resized = QtCore.Signal(float)
    is_locked_to_ee : bool = True
    def __init__(self, pos, size=None, radius=None, movable=False, ee_roi: EE_ROI = None):
        super().__init__(pos, size, radius=radius, movable=movable)
        self.removeHandle(0)
        self.ee_roi = ee_roi
        self.setPen(pg.mkPen('y'))
    
    def radius(self) -> float:
        return self.size().x()/2
    
    def center_rel_ee(self) -> None:
        if(self.is_locked_to_ee):
            ee_pos_x = self.ee_roi.pos()[0]
            ee_pos_y = self.ee_roi.pos()[1]
            ee_rad = self.ee_roi.size().x()/2
            self.setPos((ee_pos_x + ee_rad - self.radius(), ee_pos_y+ee_rad-self.radius()))
    
    def set_center_pos(self, pos:tuple):
        x,y = pos[0],pos[1]
        radius = self.size().x()/2
        centered_pos = (x-radius, y-radius)
        self.setPos(centered_pos)

    def resize(self, radius: float):
        self.setSize(radius * 2, center=(0.5,0.5))
        self.resized.emit(radius)

class Center_Spot(pg.CircleROI):
    def __init__(self, pos, radius=2, movable = False):
        super().__init__(pos, radius, movable)
        self.setPen(pg.mkPen('r', width=2))
        self.removeHandle(0)
        self.setVisible(False)
    
    def set_center_pos(self, pos:tuple):
        x,y = pos[0],pos[1]
        radius = self.size().x()/2
        centered_pos = (x-radius, y-radius)
        self.setPos(centered_pos)

        
if __name__ == "__main__":
    app = pg.mkQApp()
    widget = pg.GraphicsLayoutWidget()
    viewbox = pg.ViewBox()
    viewbox.addItem(Center_Spot((0,0)))
    viewbox.setAspectLocked(True)
    widget.addItem(viewbox)
    widget.show()
    app.exec()
    
