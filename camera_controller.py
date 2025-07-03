from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
import zwoasi as asi
import numpy as np
from signals import signals as sig

class Camera_Controller(QtCore.QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        print("camera time")
        asi.init(r"C:\Program Files\ASIStudio\ASICamera2.dll")
        self.camera = asi.Camera(asi.list_cameras()[0])
        sig.main_win_req_frame.connect(self.send_frame)
        sig.main_win_start_live_view.connect(self.start_live)
        sig.main_win_end_live_view.connect(self.end_live)

    def update_camera_settings(self):
        '''
        Sets camera settings.
        '''
        print("Setting Camera Settings")
        try:
            
            self.camera.set_roi(bins=4)
            self.camera.set_image_type(asi.ASI_IMG_RAW16)
        except Exception as e:
            print("No Camera is Connected")

    def start_live(self):
        '''
        Starts the camera live feed.
        '''
        print("Starting Live")
        self.update_camera_settings()
        self.timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 100000 + 500
        
        self.camera.start_video_capture()
        frame = self.camera.capture_video_frame(timeout=self.timeout)
        sig.cam_frame_ready.emit(frame)

        QtCore.QThread.msleep(250)
        sig.cam_first_frame.emit()


        
        
    def send_frame(self, bg_roi, main_imi):
        '''
        Takes and processes a frame before sending it to be displayed in the main window.
        '''
        frame = self.camera.capture_video_frame(timeout=self.timeout)
        background = np.average(bg_roi.getArrayRegion(frame, main_imi))
        bg_subbed_frame = frame - background
        bg_subbed_frame[bg_subbed_frame < 0] = 0
        sig.cam_frame_ready.emit(bg_subbed_frame)

    def end_live(self):
        print("Ending Live Feed")

        self.camera.stop_video_capture()