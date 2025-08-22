from pyqtgraph.Qt import QtCore
from camera import CameraController
import numpy as np

class Spot_Averager(QtCore.QObject):
    done = QtCore.Signal(tuple)

    def __init__(self, num_frames: int = 1, camera: CameraController = None):
        super().__init__(parent=None)
        self.coms = []
        self.num_frames = num_frames
        self.frames_tracked: int = 0

        self.buffered = False


        if camera:
            self.camera = camera
            self.camera.worker.spot_tracker.focused_com_update.connect(lambda: self.start_tracking())
        else:
            print("No Camera connected to Spot Averager. Deleting Spot Averager Object.")
            self.deleteLater()


    def start_tracking(self):
        if not self.buffered:
            print("Averaging Started")
            self.buffered = True
            self.camera.worker.spot_tracker.focused_com_update.connect(self.track) # This allows a buffer frame, which could be blurry as motors move.

        

    def track(self, com):
        self.coms.append(com)
        self.frames_tracked += 1
        if self.frames_tracked == self.num_frames:
            self.send_result()


    def send_result(self):
        x_avg = np.average([i[0] for i in self.coms])
        y_avg = np.average([i[1] for i in self.coms])
        print(f"Results of Averaging: coms: {self.coms}")
        self.done.emit((x_avg, y_avg))
        self.deleteLater()
