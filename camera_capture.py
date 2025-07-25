from pyqtgraph import QtCore, QtWidgets
from camera import CameraController
from astropy.io import fits
from astropy.io.fits import Card
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from capture_widget import Capture_Widget
import zwoasi as asi
from angle_manager import Angle_Manager

class Capture_Manager(QtCore.QObject):
    filepath : str = None
    capture : bool = False
    def __init__(self, camera: CameraController = None, angle_manager : Angle_Manager = None):
        super().__init__(parent= None)
        #Instantiate Children
        self.header_manager = HeaderManager(camera = camera, angle_manager = angle_manager)

        #   Camera
        if camera:
            self.camera = camera
            self.camera.worker.raw_frame_ready.connect(self.frame_received)
        else:
            print("No Camera connected to Camera Capture")


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
        header = self.header_manager.get_header(time=time)
        fits.writeto(filepath, frame, header)
        print(F"Captured image {filename}")

class HeaderManager:
    def __init__(self, camera: CameraController = None, angle_manager : Angle_Manager = None):
        if camera:
            self.camera = camera
        else:
            print("No Camera connected to Header Manager")
        

        self.angle_manager = angle_manager

    def get_header(self, time: datetime):
        header : fits.Header = fits.Header()
        header.append(Card("date-obs", time.strftime("%Y-%m-%dT%H:%M:%S"), "Observation Datetime."))
        header.append(Card("SFTWARE", "GUI OAT", "Software used to capture this image."))
        header.append(Card("Camera", self.camera.camera.get_camera_property()["Name"], "Camera used to capture this image."))
        header.append(Card("EXPOSURE", str(self.camera.camera.get_control_value(asi.ASI_EXPOSURE)), f"Exposure Time (microseconds)"))
        if self.angle_manager and self.angle_manager.grating_pos_offset and self.angle_manager.camera_pos_offset:
            header.append(Card("Alpha", str(self.angle_manager.alpha()), "Angle from the grating normal to the incident light."))
            header.append(Card("Beta", str(self.angle_manager.beta()), "Angle from the grating normal to the diffraction order"))
        return header

if __name__ == "__main__":
    HeaderManager()

        






    

