import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np
from diffractometer_tools import Diffractometer_Tools as dt

class Crosshairs(QtCore.QObject):
    def __init__(self, dimensions: tuple, width: int, parent = None):
        super().__init__(parent)
        x = dimensions[1]
        y = dimensions[0]
        self.h_crosshair = pg.LineROI((0, y/2), (x, y/2), width=width, movable = False)
        self.v_crosshair = pg.LineROI((x/2, 0), (x/2, y), width=width, movable = False) 
        for handle in self.h_crosshair.getHandles():
            self.h_crosshair.removeHandle(handle)
        for handle in self.v_crosshair.getHandles():
            self.v_crosshair.removeHandle(handle)

    def set_size(self, dimensions: tuple, width: int):
        x = dimensions[1]
        y = dimensions[0]
        self.h_crosshair = pg.LineROI((0, y/2), (x, y/2), width=width, movable = False)
        self.v_crosshair = pg.LineROI((x/2, 0), (x/2, y), width=width, movable = False) 
        for handle in self.h_crosshair.getHandles():
            self.h_crosshair.removeHandle(handle)
        for handle in self.v_crosshair.getHandles():
            self.v_crosshair.removeHandle(handle)
        try:
            if(self.dt.is_x_centered):
                self.show_centered_v()
            if(self.dt.is_y_centered):
                self.show_centered_h()
        except AttributeError as e:
            print("Crosshair Size Set with no diffractometer tool attached")


    def set_diff_tools(self, dt: dt):
        self.dt = dt
        self.dt.h_enter_center.connect(self.show_centered_h)
        self.dt.v_enter_center.connect(self.show_centered_v)
        self.dt.h_exit_center.connect(self.reset_pen_h)
        self.dt.v_exit_center.connect(self.reset_pen_v)

    
    def show_centered_h(self):
        print("centered y")
        self.h_crosshair.setPen(pg.mkPen('g'))
    def show_centered_v(self):
        print("centered x")
        self.v_crosshair.setPen(pg.mkPen('g'))
    def reset_pen_h(self):
        print("un-centered y")
        self.h_crosshair.setPen(pg.mkPen('w'))
    def reset_pen_v(self):
        print("uncentered x")
        self.v_crosshair.setPen(pg.mkPen('w'))