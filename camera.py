import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import zwoasi as asi
import numpy as np
from scipy.ndimage import center_of_mass
from roi_manager import ROI_Manager
from displayimageitem import Display_Imi
from bg_roi import Background_ROI
from camera_settings_widget import Camera_Settings_Widget

class CameraController(QtCore.QObject):
    start_req = QtCore.Signal() # Use to start camera
    def __init__(self, parent = None, roi_manager: ROI_Manager = None):
        super().__init__(parent)
        self.is_active: bool = False
        print("camera time")
        # Initializations
        asi.init(r"C:\Program Files\ASIStudio\ASICamera2.dll")
        try:
            self.camera = asi.Camera(asi.list_cameras()[0])
        except IndexError as ie:
            print("No camera is connected. Camera controller will not function.", ie)
            return
        if roi_manager:
            self.bg_roi = roi_manager.bg_roi
            self.bg_roi.sigRegionChangeFinished.connect(self.bg_array_moved)
        self.settings = Camera_Settings(self.camera)
        

        # Set Up Worker
        self.worker = Camera_Worker(self.camera, self, self.settings, self.bg_roi)
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.worker.first_frame.connect(self.bg_array_moved)
        print("Camera Initialized")

        # Set up display
        self.imi = Display_Imi()
        self.worker.frame_ready.connect(self.imi.setImage)

    def start_live_view(self):
        self.set_active()
        self.start_req.emit()

    def set_active(self, enabled: bool = True):
        '''
        Sets the camera to an active or inactive state.
        '''
        self.is_active = enabled


    def bg_array_moved(self):
        '''
        Tells the processor that the slice needs to be updated when bg roi is moved
        '''
        if self.is_active:
            self.bg_roi_slice = self.bg_roi.getArraySlice(self.imi.image, self.imi)[0]


            
    


class Camera_Settings(QtCore.QObject):
    '''
    Settings class that every camera object will have.
    '''
    bins: int = 1
    image_type = asi.ASI_IMG_RAW16
    exposure = 250
    gain = 200
    
    def __init__(self, camera: asi.Camera, parent = None):
        super().__init__(parent)
        self.camera = camera
        self.camera.set_roi(bins=self.bins)
        self.camera.set_image_type(self.image_type)
        self.camera.set_control_value(asi.ASI_EXPOSURE, self.exposure)
        self.camera.set_control_value(asi.ASI_GAIN, self.gain)
        self.timeout = self.get_timeout()
        self.widget = Camera_Settings_Widget()
        self.set_up_widget()

    def set_up_widget(self):
        self.widget.exposure_widget.slider.valueChanged.connect(self.set_exposure)
        self.widget.gain_widget.slider.valueChanged.connect(self.set_gain)

    def get_timeout(self):
        '''
        Returns the timeout setting of the camera.
        '''
        self.timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] * 2000) + 500 # Recommended in docs.
        return (self.timeout)
    
    def set_exposure(self, exposure: int):
        """
        Sets camera exposure (microseconds)
        """
        self.exposure = exposure
        self.camera.set_control_value(asi.ASI_EXPOSURE, self.exposure)
        print(f"Exposure set to {self.exposure}")

    def set_gain(self, gain: int):
        
        self.gain = gain
        self.camera.set_control_value(asi.ASI_GAIN, self.gain)
        print(f"Gain set to {self.gain}")


class Camera_Worker(QtCore.QObject):
    frame_ready = QtCore.Signal(np.ndarray) # Emitted when a new frame has been processed, contains frame.
    com_ready = QtCore.Signal(tuple) # Emitted when a new frame has been processed. Contains center of mass of frame.
    first_frame = QtCore.Signal() # Emitted with the first frame processed to help GUI set up for live view.
    frame_raw_stats = QtCore.Signal(dict)

    def __init__(self, camera: asi.Camera, camera_controller : CameraController, settings: Camera_Settings = None, bg_roi: Background_ROI = None, parent = None):
        super().__init__(parent)
        self.settings = settings
        self.camera = camera
        self.controller = camera_controller
        self.controller.start_req.connect(self.start_live)


    def start_live(self):
        print("Starting live view")
        self.camera.start_video_capture()
        results = self.capture_and_process_frame(bg_sub=False)
        if self.controller.is_active:
            self.emit_results(results[0], results[1], results[2])
            self.first_frame.emit()
            while self.controller.is_active:
                self.run_live()

        else:
            self.end_live()

    def run_live(self):
        results = self.capture_and_process_frame()
        if self.controller.is_active:
            self.emit_results(results[0], results[1], results[2])

        else:
            self.end_live()

    def capture_and_process_frame(self, bg_sub: bool = True) -> tuple[tuple, np.ndarray, dict]:

        frame = self.camera.capture_video_frame(timeout=self.settings.get_timeout())
        raw_frame_stats = {"Min": np.min(frame), "Max": np.max(frame)}
        if bg_sub:
            background_counts = np.average(frame[self.controller.bg_roi_slice])
            bg_subbed_frame = frame - background_counts
            bg_subbed_frame[bg_subbed_frame < 0] = 0
            com = center_of_mass(bg_subbed_frame)
            com_adjusted = (com[1], com[0])
            return(com_adjusted, bg_subbed_frame, raw_frame_stats)
        
        else:
            com = center_of_mass(frame)
            com_adjusted = (com[1], com[0])
            return(com_adjusted, frame, raw_frame_stats)
    
    def emit_results(self, com: tuple, frame: np.ndarray, rfs: dict):
        self.frame_ready.emit(frame)
        self.com_ready.emit(com)
        self.frame_raw_stats.emit(rfs)
    
    def end_live(self):
        print("Ending live view")
        self.camera.stop_video_capture()



if __name__ == "__main__":
    app = pg.mkQApp()
    object = CameraController()
    object.start_live_view()
    app.exec()

        
