import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np
import matplotlib.pyplot as plt
from camera import CameraController


class Stability_Check(QtCore.QObject):
    tracking : bool = False
    def __init__(self, camera: CameraController = None):
        super().__init__(parent= None)
        self.track_button = QtWidgets.QPushButton("Track COM")
        self.track_button.show()
        self.track_button.clicked.connect(lambda : self.track_stability())
        if camera:
            self.spot_tracker = camera.worker.spot_tracker
            self.spot_tracker.focused_com_update.connect(self.new_com)
        else:
            print("No camera connected to Stability Check")
        

    def track_stability(self, frames: int = 100):
        print(f"DEBUG: track_stability called. 'frames' argument received: {frames} (type: {type(frames)})")
        self.num_frames = frames
        print(f"DEBUG: self.num_frames after assignment: {self.num_frames} (type: {type(self.num_frames)})")
        print(f"Tracking {self.num_frames} positions")
        self.frames_counted : int = 0
        self.coms = []
        self.plotwidget = pg.PlotWidget()
        self.scatter = self.plotwidget.plot([], [], symbol='o')
        self.plotwidget.show()
        self.tracking = True


    def new_com(self, com: tuple):
        if not self.tracking:
            return

        self.coms.append(com)
        xs = [com[0] for com in self.coms]
        ys = [com[1] for com in self.coms]
        self.scatter.setData(xs, ys)
        self.frames_counted += 1
        print(f"Counted {self.frames_counted} of {self.num_frames} positions")
        if self.frames_counted == self.num_frames:
            self.tracking = False

        
            


