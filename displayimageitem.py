import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
from scipy.ndimage import center_of_mass
from camera import CameraController

class Display_Imi(pg.ImageItem):
    def __init__(self, image=None, axisOrder = "row-major", camera: CameraController = None):
        super().__init__(image, axisOrder=axisOrder)
        if camera:
            camera.worker.frame_ready.connect(self.setNewImage)
        else:
            print("No Camera connected to Display IMI")

    def dims(self) -> tuple:
        if self.image:
            shape = np.shape(self.image)
            return (shape[1], shape[0])
        else:
            print("There is no image assigned to the Display Image Item.")

    def setNewImage(self, frame: np.ndarray) -> None:
        self.setImage(frame)

    def com(self) -> tuple:
        if self.image:
            com = center_of_mass(self.image)
            return (com[1], com[0])
        else:
            print("There is no image assigned to the Display Image Item")