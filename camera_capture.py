from pyqtgraph import QtCore, QtWidgets
from camera import CameraController
from astropy.io import fits
from astropy.io.fits import Card
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from capture_widget import Capture_Widget
import zwoasi as asi

class Capture_Manager(QtCore.QObject):
    filepath : str = None
    capture : bool = False
    def __init__(self, camera: CameraController):
        super().__init__(parent= None)
        #Instantiate Children
        self.header_manager = HeaderManager()

        #   Camera
        self.camera = camera
        self.camera.worker.raw_frame_ready.connect(self.frame_received)

        #   Widget
        self.widget = Capture_Widget()
        self.widget.button.clicked.connect(self.capture_button_pressed)

    def capture_button_pressed(self):
        self.filepath = self.widget.folder_select.folder_selected
        self.capture = True
    


    def frame_received(self, frame):
        if self.capture:
            self.capture_fits_image(frame)
            self.capture = False
                
                
                

    def capture_fits_image(self, frame : np.ndarray):
        print(self.filepath)
        time = datetime.now(tz=ZoneInfo("UTC"))
        filename = str(time.strftime("%Y%m%d_%H%M%S"))
        filepath = f"{self.filepath}/{filename}.fits"
        header = self.header_manager.get_header(time=time, camera=self.camera)
        fits.writeto(filepath, frame, header)
        print(F"Captured image {filename}")

class HeaderManager:
    def __init__(self):
        pass

    def get_header(self, time: datetime, camera: CameraController):
        header : fits.Header = fits.Header()
        header.append(Card("date-obs", time.strftime("%Y-%m-%dT%H:%M:%S"), "Observation Datetime."))
        header.append(Card("SFTWARE", "GUI OAT", "Software used to capture this image."))
        header.append(Card("Camera", camera.camera.get_camera_property()["Name"], "Camera used to capture this image."))
        return header

if __name__ == "__main__":
    HeaderManager()

        






    

