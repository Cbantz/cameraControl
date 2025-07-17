import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

class Background_ROI(pg.RectROI):
    def __init__(self, pos, size, centered=False, sideScalers=False, **args):
        super().__init__(pos, size, centered, sideScalers, **args)

    def set_in_corner(self, corner: str, dims: tuple) -> None:
        size_x = self.size.x()
        size_y = self.size().y()
        match corner:
            case "TR":
                self.setPos(dims[0]-size_x, 0)
            case "TL":
                self.setPos(0, 0)
            case "BR":
                self.setPos(dims[0]-size_x, dims[1]-size_y)
            case "BL":
                self.setPos(0, dims[1]-size_y)
            case _:
                print("Corner position was not valid. Please use 'TR', 'TL', 'BR', or 'BL'")