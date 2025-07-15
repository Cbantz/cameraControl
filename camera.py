import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
import zwoasi as asi
import numpy as np
from signals import signals as sig
from scipy.ndimage import center_of_mass
import time

class Camera(QtCore.QObject):

    frame_ready = QtCore.Signal(np.ndarray) # Emitted when a new frame has been processed, contains frame.
    com_ready = QtCore.Signal(tuple) # Emitted when a new frame has been processed. Contains center of mass of frame.
    start_req = QtCore.Signal() # Use to start camera
    first_frame = QtCore.Signal() # Emitted with the first frame processed to help GUI set up for live view.

    def __init__(self, parent = None):
        super().__init__(parent)
        print("camera time")
        # Initializations
        asi.init(r"C:\Program Files\ASIStudio\ASICamera2.dll")
        self.camera = asi.Camera(asi.list_cameras()[0])
        self.settings = Camera_Settings(self.camera)
        self.start_req.connect(self.start_live)
        print("Camera Initialized")
        

    def update_camera_settings(self):
        '''
        Sets camera settings.
        '''
        print("Setting Camera Settings")
        try:

            self.camera.set_roi(bins=self.settings.bins)
            self.camera.set_image_type(self.settings.image_type)
            self.camera.set_control_value(asi.ASI_EXPOSURE, self.settings.exposure)
            self.camera.set_control_value(asi.ASI_GAIN, self.settings.gain)
            self.timeout = self.settings.get_timeout()
        except Exception as e:
            print("No Camera is Connected")

    def start_live(self):
        '''
        Starts the camera live feed.
        '''
        print("Starting Live")
        self.update_camera_settings() # Set camera settings before running
        
        self.camera.start_video_capture()

        self.send_first_frame()
        

        while self.settings.is_active:
            if(self.settings.is_active): # Break if setting.isactive has been switched to off
                frame = self.camera.capture_video_frame(timeout=self.settings.get_timeout())
                self.process_frame(frame)
            else:
                break

    
    def send_first_frame(self):
        '''
        Processes and send the first frame of a live view.
        '''
        self.update_camera_settings()
        frame = self.camera.capture_video_frame(timeout=self.settings.get_timeout())
        self.process_frame(frame)
        self.first_frame.emit()
        

        
        
    def process_frame(self, frame):
        '''
        Takes and processes a frame before sending it to be displayed in the main window.
        '''

        start_time = time.time()

        if(self.settings.settings_changed):
            self.update_camera_settings()
        settings_end_time = time.time()

        frame = self.camera.capture_video_frame(timeout=self.timeout)
        frame_cap_end_time = time.time()

        if self.bg_roi_slice is not None: # Only gets a new slive when array moved. For optimization.
            self.bg_roi_slice = self.bg_roi.getArraySlice(frame, self.imi)
        background = np.average(frame[self.bg_roi_slice])
        background_end_time = time.time()

        bg_subbed_frame = frame - background
        bg_subbed_frame[bg_subbed_frame < 0] = 0
        background_sub_end_time = time.time()

        com = center_of_mass(bg_subbed_frame)
        end_time = time.time()
        total_time = end_time - start_time
        frame_cap_time = frame_cap_end_time - settings_end_time
        background_time = background_end_time - frame_cap_end_time
        background_sub_time = background_sub_end_time -background_end_time
        com_time = end_time - background_sub_end_time
        settings_time = settings_end_time-start_time

        timing_data = {
    "settings_time": settings_time,  # Assuming 'com' is defined elsewhere in your code
    "total_time": total_time, # Assuming 'start_time' and 'end_time' are defined
    "frame_capture_time": frame_cap_time, # Assuming 'frame_cap_end_time' is defined
    "background_time": background_time, # Assuming 'background_end_time' is defined
    "background_subtraction_time": background_sub_time, # Assuming 'background_sub_end_time' is defined
    "com_calculation_time": com_time
}

        # print(f"Frame Ready: took {total_time}.")
        # for i in timing_data:
        #     print(f'{i}: {timing_data[i]}')

        if self.settings.is_active: # Only send processed frame if still active
            self.frame_ready.emit(bg_subbed_frame)
            self.com_ready.emit(com)


        

        
        

    def end_live(self):
        '''
        Shuts down live feed
        '''
        print("Ending Live Feed")
        self.settings.set_active(False)
        self.camera.stop_video_capture()


    def bg_array_moved(self):
        '''
        Tells the processor that the slice needs to be updated when bg roi is moved
        '''
        self.bg_roi_slice = None


    def set_imi(self, imi: pg.ImageItem):
        '''
        Sets the Image Item to be used for processing.
        '''
        self.imi = imi
    
    def set_bg_roi(self, roi: pg.ROI):
        '''
        Sets background ROI to be used for processing.
        '''
        self.bg_roi = roi
        self.bg_roi_slice = None
        self.bg_roi.sigRegionChanged.connect(self.bg_array_moved)




class Camera_Settings(QtCore.QObject):
    '''
    Settings class that every camera object will have.
    '''
    is_active: bool = False
    settings_changed = False
    bins: int = 4
    image_type = asi.ASI_IMG_RAW16
    exposure = 250
    gain = 200
    
    def __init__(self, camera: 'Camera', parent = None):
        super().__init__(parent)
        self.camera = camera

    def set_active(self, should_be_active: bool):
        '''
        Sets the camera to an active or inactive state.
        '''
        self.is_active = should_be_active

    def get_timeout(self):
        '''
        Returns the timeout setting of the camera.
        '''
        self.timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] * 2000) + 500 # Recommended in docs.
        return (self.timeout)
    

if __name__ == "__main__":
    camera = Camera()
    camera.start_req.emit()

        
