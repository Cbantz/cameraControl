import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np
from photutils.aperture import CircularAperture
from camera import CameraController
from roi_manager import ROI_Manager
from displayimageitem import Display_Imi

class EE_Processor(QtCore.QObject):
    calc_req = QtCore.Signal()
    is_requested: bool = False
    def __init__(self, camera : CameraController = None, roi_manager: ROI_Manager = None):
        super().__init__(parent = None)
        if camera:
            imi=camera.imi
            imi.sigImageChanged.connect(self.request)
        else:
            print("No camera connected to EE Processor")
            imi=None
        if roi_manager:
            ee_roi = roi_manager.ee_roi
            ee_roi.sigRegionChanged.connect(self.request)
        else:
            print("No ROI Manager connected to EE Processor")
        self.worker = Worker(roi_manager=roi_manager, imi=imi, processor=self)
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.completed.connect(self.check_up_to_date)
        self.worker_thread.start()

    def request(self):
        if  self.worker.is_busy:
            self.is_requested = True
        else:
            self.calc_req.emit()
            

    def check_up_to_date(self):
        if self.is_requested:
            self.calc_req.emit()
            self.is_requested = False
    

    
    


class Worker(QtCore.QObject):
    is_busy: bool = False # Can take a new frame
    ee_ready = QtCore.Signal(float, float, float) # Results of calculations
    half_ready = QtCore.Signal(int) # Results
    completed = QtCore.Signal() # Used to check for a new frame

    def __init__(self, roi_manager: ROI_Manager = None, imi: Display_Imi = None, processor: EE_Processor = None):
        super().__init__(parent = None)

        if roi_manager:
            self.ee_roi = roi_manager.ee_roi
        else:
            print("No ROI Manager connected to EE Worker")

        if imi:
            self.imi = imi
        else:
            print("No imi connected to EE Worker")
        if processor:
            processor.calc_req.connect(self.calculate_ee)
        else:
            print("No Processor connected to EE Worker")

            

    def calculate_ee(self):


        frame = self.imi.image
        self.is_busy = True
        total_sum = np.sum(frame)

        roi_region = self.ee_roi.getArrayRegion(frame, self.imi)
        ee = np.sum(roi_region)

        ee_pc_enc = ee/total_sum

        #Returns the radius from center of ee_roi necessary to encircle 50% energy of the ee_roi

        r_min = 1
        r_max = np.shape(roi_region)[0]/2 # Max radius to be searched (half of size(diameter))

        # Calculate half by splitting radius search in half until possible is only one pixel
        while r_max-r_min > 1:
            r_mid = (r_max+r_min)/2
            aperture = CircularAperture((np.shape(roi_region)[0]/2,np.shape(roi_region)[1]/2), r = r_mid)
            aperture_counts = aperture.do_photometry(roi_region, method='center')[0]
            if ee != 0:
                pc_enc = aperture_counts / ee
                if(pc_enc > 0.5):
                    r_max = r_mid
                else:
                    r_min = r_mid

            else:
                r_mid = r_max
        
        self.is_busy = False

        self.half_ready.emit(r_mid)
        self.ee_roi.half_roi.resize(r_mid)
        self.ee_ready.emit(ee, ee_pc_enc, total_sum)
        self.completed.emit()
        
  




