import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

class Background_ROI(pg.RectROI):
    '''
    Region used to define the background of the camera image.
    '''
    def __init__(self, pos : tuple, size = (100, 100)):
        """
        

        Args:
            pos (tuple): Position to instantiate region at. 
            size (tuple, optional): Size of the region. Defaults to (100, 100).
        """
        super().__init__(pos, size)

    def set_in_corner(self, dims: tuple, corner: str = "BR") -> None:
        """Moves region to a corner.

        Args:
            dims (tuple): dimensions of the frame to sit in.
            corner (str, optional): Which corner to set in (TR, TL, BR, BL). Defaults to "BR".
        """     
        size_x = self.size().x()
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