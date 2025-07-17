import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import numpy as np
from scipy.ndimage import center_of_mass
from data_display_widget import Data_Display_Widget
from ee_worker import EE_Worker
from static_image_handler import Static_Image_Handler
from camera import CameraController
from Viewbox import EE_Gui_Main_View
from diffractometer_controller_gui import dt_window

class EE_GUI_Central_Widget(QtWidgets.QWidget):

    calculate_ee_req = QtCore.Signal() # Signal calls to ee_worker to calculate ee on a new frame.

    def __init__(self, camera: CameraController = None, parent=None):
        super().__init__(parent)
                                                                                                                                  


        # Set Layout
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)


        # Set up main viewing widget
        self.view = EE_Gui_Main_View()
        self._setup_view()
        self.camera = camera

        # Other variables and children
        self.ee_worker = EE_Worker()
        
        self.static_ih = Static_Image_Handler()
        self.frame_queued = False
        self._setup_data_display()
        self._setup_ee_worker()
        self._setup_static_ih()
        self._setup_diff_gui(dt_window())



    def start_static_im_show(self, filepath: str = "oat_lab_logo.fits"):
        '''
        Switches main view to static image mode. Defaults to logo if no filepath is provided.
        '''
        print("Starting Static Image Mode")
        if self.camera is not None:
            self.camera.end_live() # Ends camera video stream
            self.thread().msleep(1000)
        self.static_ih.set_active()
        self.static_ih.load_image(filepath)
        self.view.center_rois()
        self.hist.autoHistogramRange()

        # Adjust UI Elements for Static Mode
        try:
            self.view.centroid_button.setCheckable(False)
            self.view.centroid_button.setChecked(False)
        except:
            print("Main Application Widget has not been linked")
            return

    def start_camera(self):
        '''
        Switches main view to live camera mode.
        '''
        print(f"Starting Camera, {self.camera}")
        self.static_ih.set_active(False)
        self.camera.settings.set_active(True)
        self.camera.start_req.emit()
        self.hist.setHistogramRange(0, 65545) # Max value using RAW16
        # Adjust UI Elements for camera mode.
        try:
            self.view.centroid_button.setCheckable(True)
            self.view.centroid_button.setChecked(False)
        except:
            print("Main Application has not been linked.")
            return

        

    def process_new_frame(self, frame):
        '''
        Destination for all new frames to be displayed. Displays new image and runs an EE calculation.
        '''
        self.view.main_imi.setNewImage(frame)
        self.calculate_ee()


    def calculate_ee(self):
        '''
        Runs most recent frame update through ee_worker.
        '''
        if self.view.main_imi.image is None:
            return
        if(not self.ee_worker.is_busy):
            self.calculate_ee_req.emit()
        else:
            self.frame_queued = True


    def ee_finished(self):
        '''
        Re-runs EE_Worker if not up-to-date
        '''
        if(self.frame_queued):
            self.calculate_ee()

    def closeEvent(self, event):
        '''
        Runs at application exit, closes thread so we don't get errors.
        '''
        self.ee_worker.deleteLater()
        self.ee_thread.quit()
        self.ee_thread.wait()
        event.accept()

    def _setup_view(self):
        '''
        Runs at startup: Assigns variables and makes connections for the main view.
        '''
        self.hist = pg.HistogramLUTItem(self.view.main_imi)

        self.im_view = pg.GraphicsLayoutWidget()
        self.im_view.addItem(self.view)
        self.im_view.addItem(self.hist)

        self.grid_layout.addWidget(self.im_view, 0, 0, 1, 2)

        self.view.ee_roi.sigRegionChanged.connect(self.view.set_half_roi_pos)
        self.view.ee_roi.sigRegionChanged.connect(self.calculate_ee)

        


        

    def _setup_data_display(self):
        '''
        Runs at startup: Assigns variables and makes connections for the main view.
        '''
        self.data_display = Data_Display_Widget()
        self.grid_layout.addWidget(self.data_display, 0, 2, 1, 1)
        self.data_display.set_up_ee_roi(self.view.ee_roi)
        self.ee_worker.ee_ready.connect(self.data_display.form.set_ee_label)
        self.ee_worker.half_ready.connect(self.data_display.form.set_half_label)

    def _setup_ee_worker(self):
        '''
        Runs at startup: Assigns variables and makes connections for the ee worker.
        '''
        self.ee_thread = QtCore.QThread()
        self.ee_worker.moveToThread(self.ee_thread)
        self.calculate_ee_req.connect(self.ee_worker.calculate_ee)
        self.ee_thread.start()
        self.ee_worker.set_ee_roi(self.view.ee_roi)
        self.ee_worker.set_image_item(self.view.main_imi)
        self.ee_worker.completed.connect(self.ee_finished)
        self.ee_worker.half_ready.connect(self.view.set_half_roi_size)

    def _setup_static_ih(self):
        '''
        Runs at startup: Assigns variables and makes connections for the static view handler.
        '''
        self.static_ih.set_bg_roi(self.view.bg_roi)
        self.static_ih.set_imi(self.view.main_imi)
        self.static_ih.static_frame_ready.connect(self.process_new_frame)
        self.start_static_im_show()

    def _setup_camera(self, camera: CameraController):
        '''
        Runs at startup: Assigns variables and makes connections for the camera.
        '''
        self.camera = camera
        self.camera.set_bg_roi(self.view.bg_roi)
        self.camera.set_imi(self.view.main_imi)
        self.camera.settings.set_active(False)
        self.camera.frame_ready.connect(self.process_new_frame)
        self.camera.com_ready.connect(self.view.centroid)
        self.camera.first_frame.connect(self.view.center_rois)
        self.diff_gui.diff_tools.set_up_camera(self.camera)

    
    def _setup_diff_gui(self, gui: dt_window):
        self.diff_gui = gui
        self.grid_layout.addWidget(self.diff_gui, 1, 0, 1, 3)
        self.view.crosshairs.set_diff_tools(self.diff_gui.diff_tools)
        




    


if __name__ == "__main__":
    app = pg.mkQApp()
    #camera = Camera()
    widget = EE_GUI_Central_Widget()
    #widget._setup_camera(camera=camera)
    widget.show()

    app.exec()


    