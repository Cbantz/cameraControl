import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np

class EE_ROI(pg.CircleROI):
    def __init__(self, pos, size=None, radius=None, scaleSnap=True, translateSnap=True):
        super().__init__(pos, size, radius, scaleSnap, translateSnap)
        self.snapSize = 1
        self.removeHandle(0)
        self.ee_roi.addScaleHandle((0, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((0, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 1), (0.5, 0.5), lockAspect=True)
        self.half_roi = Half_ROI(pos, size, radius, ee_roi=self)
        self.sigRegionChanged.connect(self.half_roi.center_rel_ee)

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
    def __init__(self, pos, size=None, radius=None, movable=False, ee_roi: EE_ROI = None):
        super().__init__(pos, size, radius, movable)
        self.removeHandle(0)
        self.ee_roi = ee_roi
    
    def radius(self) -> float:
        return self.size().x()/2
    
    def center_rel_ee(self) -> None:
        ee_pos_x = self.ee_roi.pos()[0]
        ee_pos_y = self.ee_roi.pos()[1]
        ee_rad = self.ee_roi.size().x()/2
        self.setPos((ee_pos_x + ee_rad - self.radius(), ee_pos_y+ee_rad-self.radius()))

    def resize(self, radius: int):
        self.setSize(radius * 2, center=(0.5,0.5))
