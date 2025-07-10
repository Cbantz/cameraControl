import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from astropy.io import fits
from scipy.ndimage import center_of_mass
import numpy as np
from signals import signals as sig
import ee_gui_main_win, ee_gui_central_widget
from camera import Camera


class EEGUI_Manager(QtCore.QObject):
    def __init__(self):
        super().__init__(parent = None)
        self.main_win = ee_gui_main_win.MainWindow()
        print("Main Window Initialized")
        self.central_widget = ee_gui_central_widget.EE_GUI_Central_Widget()
        print("Central Widget Initialized")
        
        self._setup_main_win()
        self._setup_central_widget()

        self.main_win.show()



    def _setup_main_win(self):
        self.main_win.setCentralWidget(self.central_widget)
        self.main_win.file_button.clicked.connect(self.pick_file)
        self.main_win.centroid_button.clicked.connect(self.centroid_button_clicked)
        self.main_win.live_button_pressed.connect(self.central_widget.start_camera)
        self.main_win.live_button_released.connect(self.central_widget.start_static_im_show)
        

    def _setup_central_widget(self):
        self.central_widget.view._set_centroid_button(self.main_win.centroid_button)


    def set_camera(self, camera: Camera):
        self.camera = camera
        self.central_widget._setup_camera(camera)

    def centroid_button_clicked(self):
        self.central_widget.view.centroid()



        




    
    # def load_new_frame(self, frame):
    #     '''
    #     Subtracts background region from received frame, sets frame as main imi image, moves to centroid if necessary, runs calculate_ee
    #     '''
    #     self.win1.main_imi.setImage(frame)
    #     self.calculate_ee()

    # def load_image(self, filepath):
    #     '''
    #     Loads a new image after file is chosen. Arranges image and ROIs to match.
    #     '''

    #     # Open Selected Image
    #     hdul = fits.open(filepath)
    #     print()
    #     header, data = hdul[0].header, hdul[0].data

    #     self.main_imi.setImage(data) # Set as Main Image
    #     self.og_im_data = data #Set as OG Image
    #     self.hist.setImageItem(self.main_imi) # Set as Hist Image

    #     self.prep_rois()

    # def frame_received(self, frame):
    #     if(self.live_cam_button.isChecked()):
    #         self.load_new_frame(frame)

    #     else:
    #         return



    # def live_button_clicked(self):
    #     '''
    #     Runs whenever live button is clicked. Either starts or ends the live camera feed.
    #     '''
    #     if(self.live_cam_button.isChecked()): # Button pressed down
    #         if(not self.camera_activated):
    #         sig.connect_to_camera.emit()
    #         self.camera_activated = True
    #         self.start_live_cam()
    #     else: # Button released
    #         self.end_live_cam()

    # def start_live_cam(self):
    #     '''
    #     Starts live camera feed
    #     '''
    #     self.centroid_button.setCheckable(True) # Allows for live centering
    #     self.hist.disableAutoHistogramRange()
    #     self.hist.setHistogramRange(0, 65535) # Max value of 16 bit
    #     sig.main_win_start_live_view.emit()

    # def end_live_cam(self):
    #     '''
    #     Ends live camera feed, reverts to last loaded image
    #     '''
    #     sig.main_win_end_live_view.emit()
    #     self.centroid_button.setChecked(False)
    #     self.centroid_button.setCheckable(False)
    #     self.main_imi.setImage(self.og_im_data)
    #     self.prep_rois()

    # def first_frame_received(self):
    #     '''
    #     Runs when the first live camera frame is received. Prepares ROIs
    #     '''
    #     print("Feed Initialized")
    #     self.prep_rois()


    # def main_image_changed(self):
    #     '''
    #     Runs any time the main image changes.
    #     Updates total count measurement
    #     '''
    #     self.total_counts = np.sum(self.main_imi.image)


    # def centroid(self, com = None):
    #     '''

    

    # def ee_region_changed(self):
    #     '''
    #     Runs every time the ee_roi region changes. Calculates EE and half, repositions half_roi to center
    #     '''
    #     if(self.dp_roi_size.text() != f"{int(self.ee_roi.size().x())}"):
    #         self.dp_roi_size.setText(f"{int(self.ee_roi.size().x())}")

        
        
    #     self.calculate_ee()
    #     ee_x, ee_y = self.ee_roi.pos()
    #     #Update position text
    #     ee_size = self.ee_roi.size()[0]
    #     self.dp_roi_pos_x.setText(str(np.round(ee_x + (ee_size/2), 4)))
    #     self.dp_roi_pos_y.setText(str(np.round(ee_y+(ee_size/2), 4)))

    #     # Update half_roi position
    #     half_size = self.half_roi.size()[0]
    #     self.half_roi.setPos(ee_x + (ee_size-half_size)/2, ee_y + (ee_size-half_size)/2)

    # def bg_reg_changed(self):
    #     '''
    #     Runs whenever the background region changes, updates main image to subtract new background average
    #     '''

    #     if self.live_cam_button.isChecked() == False:
    #         self.set_background()


    def pick_file(self):
        '''
        Loads File Dialog. Sends selected image to load_image()
        '''
        print("Open File Picker")
        file_name = pg.FileDialog.getOpenFileName(None, "Select Image", "", "FITS Files (*.fits *.fit);;CSV Files (*.csv)")[0]
        self.central_widget.start_static_im_show(file_name)




    
    # def calculate_ee(self):
    #     '''
    #     Asks ee thread to calculate encircled energy or sets is_ee_queued flag to True if thread is busy.
    #     '''
    #     if self.is_ee_thread_busy:
    #         self.is_ee_queued = True
    #         return
        
    #     self.calculate_ee_req.emit(self.ee_roi, self.main_imi.image, self.main_imi)
    #     self.is_ee_thread_busy = True

        
        
    # def ee_thread_next_process(self):
    #     '''
    #     Runs after each result from EE Thread. Determines if a new position needs to be run or not. Sets flags accordingly
    #     '''
    #     if self.is_ee_queued == True:
    #         self.calculate_ee_req.emit(self.ee_roi, self.main_imi.image, self.main_imi)
    #         self.is_ee_queued = False
    #         return
    #     else:
    #         self.is_ee_thread_busy = False
    #         return

    # def ee_result_received(self, ee):

    #     self.display_ee(ee)
    #     self.ee_thread_next_process()


    #     # If live feed is on, calls another frame, as this should be the last thing to process per frame
    #     if(self.live_cam_button.isChecked()):
    #         sig.main_win_req_frame.emit(self.bg_roi, self.main_imi)



    # def dp_roi_size_editing_finished(self):
    #     '''
    #     Updates dp_roi_size row of Data Panel
    #     '''
    #     self.ee_roi.setSize(float(self.dp_roi_size.text()), center=(0.5, 0.5))

    


if __name__ == "__main__":
    app = pg.mkQApp()
    object = EEGUI_Manager()
    another_thread = QtCore.QThread()
    camera = Camera()
    camera_thread = QtCore.QThread()
    camera.moveToThread(camera_thread)
    camera_thread.start()
    camera.settings.moveToThread(another_thread)
    object.set_camera(camera=camera)
    app.exec()


    

    
        
        


    

    
        











