import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from astropy.io import fits
import numpy as np
from scipy.ndimage import center_of_mass
from photutils.aperture import CircularAperture
import zwoasi as asi
import time



# Start Qt app
app = pg.mkQApp("Image Display")

# Create main graphics window
class MainWindow(QtWidgets.QMainWindow):

    #Create Signals
    calculate_ee_req = QtCore.Signal(object, object, object) # Signal used when you need to calculate the EE in ee_roi
    start_live_view_sig = QtCore.Signal() # Signal to start live view from camera
    request_frame = QtCore.Signal(pg.ROI, pg.ImageItem) # Signal to request a frame after previous has finished displaying

    def __init__(self):
        super().__init__()


        # Create Threads and workers 
        #EE
        self.ee_worker = EE_Worker()
        self.ee_thread = QtCore.QThread()
        self.is_ee_thread_busy = False # Flag for when ee thread is processing
        self.ee_worker.moveToThread(self.ee_thread)
        self.is_ee_queued = False # Flag if there is a position that has not been updated for ee_roi
        self.ee_worker.ee_ready.connect(self.ee_result_received) # Determine if a new position should be calculated and start it, display results, ask for next frame if applicable
        self.calculate_ee_req.connect(self.ee_worker.calculate_ee) # Runs calculate_ee() whenever the ee_req signal is sent
        self.ee_thread.start()

            # Half Encircled
        self.ee_worker.half_ready.connect(self.display_half) # Display half-encircled when done

        self.setWindowTitle("EE GUI (University of Iowa OAT Lab)")
        
        #Camera
        self.camera_worker = Camera_Worker()
        self.camera_thread = QtCore.QThread()
        self.camera_worker.moveToThread(self.camera_thread)
        self.camera_worker.frame_ready.connect(self.frame_received)
        self.camera_worker.first_frame.connect(self.first_frame_received)
        self.request_frame.connect(self.camera_worker.send_frame)
        self.start_live_view_sig.connect(self.camera_worker.start_live)
        



        # Create Main Grid
        self.win1 = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.win1)

        # Create Image Widget 
        self.main_plot = pg.GraphicsLayoutWidget()

        # Create Main Image
        self.main_imi = pg.ImageItem(image=np.array([[0]]), axisOrder='row-major')
        self.main_imi.sigImageChanged.connect(self.main_image_changed)

        # Create Original Image Data
        self.og_im_data = self.main_imi.image
        self.total_counts = 0

        # Create View
        self.view = self.main_plot.addViewBox(row = 0, col = 0, invertY = True)
        self.view.setAspectLocked(True)

        # Create EE ROI
        self.ee_roi = pg.CircleROI((0,0), size=100, scaleSnap = True, snapSize = 1, translateSnap=True)
        self.ee_roi.removeHandle(0)
        self.ee_roi.addScaleHandle((0, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((0, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.sigRegionChanged.connect(self.ee_region_changed)
        self.ee_roi.setVisible(False)

        # Create Half ROI
        self.half_roi = pg.CircleROI((0,0), size=1, movable = False)
        self.half_roi.removeHandle(0)


        # Create Background ROI
        self.bg_roi = pg.RectROI((0,0), size=300)
        self.bg_roi.sigRegionChanged.connect(self.bg_reg_changed)
        self.bg_roi.setVisible(False)
        self.background_average = 0

        # Create Centroid Button
        self.centroid_button = pg.QtWidgets.QPushButton("Centroid")
        self.centroid_button.pressed.connect(self.centroid)


        # Create Camera button
        self.live_cam_button = QtWidgets.QPushButton("Live Camera View")
        self.live_cam_button.setCheckable(True)
        self.live_cam_button.clicked.connect(self.live_button_clicked)



        # Add Items to View
        self.view.addItem(self.main_imi)
        self.view.addItem(self.ee_roi)
        self.view.addItem(self.half_roi)
        self.view.addItem(self.bg_roi)

        # Create HistogramLUTItem
        print("hello")
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.main_imi)
        print("hello")

        # Add Items to main_plot
        self.main_plot.addItem(self.hist, row = 0, col = 1)
        
        # Create File Picker
        file_button = QtWidgets.QPushButton("Open File")
        file_button.clicked.connect(self.pick_file)

        # Create Data Panel
        self.dp = pg.GraphicsLayoutWidget()
        self.dpgrid=QtWidgets.QVBoxLayout(self.dp)

        # Create Data Panel Form
        dp_form = QtWidgets.QWidget()
        dp_form_layout = QtWidgets.QFormLayout(dp_form)

        # Data Panel Data
        # Title Label
        dp_text = pg.QtWidgets.QLabel("Data Panel")

        # EE ROI Position
        self.dp_roi_pos_x = pg.QtWidgets.QLineEdit(f"{self.ee_roi.pos().x()}")
        self.dp_roi_pos_y = pg.QtWidgets.QLineEdit(f"{self.ee_roi.pos().y()}")

        # EE ROI Size Line Edit
        self.dp_roi_size = pg.QtWidgets.QLineEdit(f"{self.ee_roi.size().x()}")
        self.dp_roi_size.editingFinished.connect(self.dp_roi_size_editing_finished)
        dp_roi_size_validator = QtGui.QIntValidator(bottom=0, top=1000)
        self.dp_roi_size.setValidator(dp_roi_size_validator)

        # Percent Enclosed
        self.pc_enc_label = pg.QtWidgets.QLabel()

        #50% Radius
        self.half_label = QtWidgets.QLabel()

        # Add Rows to Data Panel Form
        dp_form_layout.addRow("ROI X Position: ", self.dp_roi_pos_x)
        dp_form_layout.addRow("ROI Y Position: ", self.dp_roi_pos_y)
        dp_form_layout.addRow("ROI Size: ", self.dp_roi_size)
        dp_form_layout.addRow("Energy Enclosed: ", self.pc_enc_label)
        dp_form_layout.addRow("50% Enclosed Radius: ", self.half_label)

        # Arrange Widgets in Data Panel
        self.dpgrid.addWidget(dp_text, 1)
        self.dpgrid.addWidget(dp_form, 10)
        

        # Arrange Widgets in Master Widget
        self.grid.addWidget(self.main_plot, 0, 0, 1, 2)
        self.grid.addWidget(self.dp, 0, 2, 1, 1)
        # Set the central widget of the Window and add toolbar
        self.setCentralWidget(self.win1)

        #Create Toolbar, Add items
        self.toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addWidget(file_button)
        self.toolbar.addWidget(self.centroid_button)
        self.toolbar.addWidget(self.live_cam_button)

        self.load_image(filepath="oat_lab_logo.fits")

    
    def load_image(self, filepath):
        '''
        Loads a new image after file is chosen. Arranges image and ROIs to match.
        '''

        # Open Selected Image
        hdul = fits.open(filepath)
        print()
        header, data = hdul[0].header, hdul[0].data

        self.main_imi.setImage(data) # Set as Main Image
        self.og_im_data = data #Set as OG Image
        self.hist.setImageItem(self.main_imi) # Set as Hist Image

        self.prep_rois()

    def frame_received(self, frame):
        if(self.live_cam_button.isChecked()):
            self.load_new_frame(frame)

        else:
            return

    def load_new_frame(self, frame):
        '''
        Subtracts background region from received frame, sets frame as main imi image, moves to centroid if necessary, runs calculate_ee
        '''
        self.main_imi.setImage(frame)
        if(self.centroid_button.isChecked()):
            self.centroid()
        self.calculate_ee()

    def live_button_clicked(self):
        '''
        Runs whenever live button is clicked. Either starts or ends the live camera feed.
        '''
        if(self.live_cam_button.isChecked()): # Button pressed down
            self.start_live_cam()
        else: # Button released
            self.end_live_cam()

    def start_live_cam(self):
        '''
        Starts live camera feed
        '''
        self.camera_thread.start()
        self.centroid_button.setCheckable(True) # Allows for live centering
        self.hist.disableAutoHistogramRange()
        self.hist.setHistogramRange(0, 65535) # Max value of 16 bit
        self.start_live_view_sig.emit()

    def end_live_cam(self):
        '''
        Ends live camera feed, reverts to last loaded image
        '''
        self.centroid_button.setCheckable(False)
        self.camera_thread.quit()
        self.camera_thread.wait()
        self.main_imi.setImage(self.og_im_data)
        self.prep_rois()

    def first_frame_received(self):
        '''
        Runs when the first live camera frame is received. Prepares ROIs
        '''
        self.prep_rois()

        

        
    def prep_rois(self):
        '''
        Will organize and show ROIs according to content being shown. Useful when changing main image focus or type.
        '''

        x,y = np.shape(self.main_imi.image) 

        # ROI parameters
        roi_size = self.ee_roi.size()[0]
        roi_pos = ((y - roi_size) / 2, (x - roi_size) / 2)  # Centered position

        roi_bounds = pg.QtCore.QRectF(pg.QtCore.QPoint(0, 0), pg.QtCore.QPoint(y, x)) #ROI bounded to the image size.
        
        # ROI centered in image
        self.ee_roi.setPos(roi_pos)
        self.bg_roi.setPos((y - self.bg_roi.size().y(), x-self.bg_roi.size().y()))

        # Set ROI Bounds
        self.ee_roi.maxBounds = roi_bounds
        self.bg_roi.maxBounds = roi_bounds

        #Show ROIs
        self.ee_roi.setVisible(True)
        self.bg_roi.setVisible(True)


    def main_image_changed(self):
        '''
        Runs any time the main image changes.
        Updates total count measurement
        '''
        self.total_counts = np.sum(self.main_imi.image)


    def centroid(self):
        '''
        Moves the EE ROI to the scipy center of mass of the current displayed image
        '''
        com = center_of_mass(self.main_imi.image)
        offset = self.ee_roi.size().x() / 2 #Adjust for 'pos' controlling the top left corner of the ROI
        centered_pos = (com[1]-offset, com[0] - offset)
        self.ee_roi.setPos(centered_pos) # Centers ROI because position is based on top right


        ### This changes centroid to only use area inside ROI and repeats until it has found a good center. Useful for stars but maybe not for this.
        # current_pos = self.ee_roi.pos()
        # com_int = center_of_mass(self.ee_roi.getArrayRegion(self.main_imi.image, self.main_imi))
        # new_pos = (current_pos[0] + com_int[1] - offset, current_pos[1] + com_int[0] - offset)
        # dist = np.sqrt(np.square(new_pos[0] - current_pos[0]) + np.square(new_pos[1] - current_pos[1]))

        # print(f"dist {dist}")
        # if(dist >= 0.25):
        #     self.ee_roi.setPos(new_pos)
        #     self.centroid()
        
    
    def set_background(self):
        '''
        Set the background count when set_background button is pressed.
        '''
        bg_region = self.bg_roi.getArrayRegion(self.og_im_data, self.main_imi) # Get background region from bg_roi
        avg_bg_count = np.average(bg_region)
        # Adjust image data and display operational data
        bg_rem_data = self.og_im_data - avg_bg_count
        bg_rem_data[bg_rem_data<0] = 0 # Sets negative values to 0
        self.main_imi.setImage(bg_rem_data) # Remove average background count
        self.calculate_ee()

    def ee_region_changed(self):
        '''
        Runs every time the ee_roi region changes. Calculates EE and half, repositions half_roi to center
        '''
        if(self.dp_roi_size.text() != f"{int(self.ee_roi.size().x())}"):
            self.dp_roi_size.setText(f"{int(self.ee_roi.size().x())}")

        
        
        self.calculate_ee()
        ee_x, ee_y = self.ee_roi.pos()
        #Update position text
        ee_size = self.ee_roi.size()[0]
        self.dp_roi_pos_x.setText(str(ee_x + (ee_size/2)))
        self.dp_roi_pos_y.setText(str(ee_y+(ee_size/2)))

        # Update half_roi position
        half_size = self.half_roi.size()[0]
        self.half_roi.setPos(ee_x + (ee_size-half_size)/2, ee_y + (ee_size-half_size)/2)

    def bg_reg_changed(self):
        '''
        Runs whenever the background region changes, updates main image to subtract new background average
        '''

        if self.live_cam_button.isChecked() == False:
            self.set_background()


    def pick_file(self):
        '''
        Loads File Dialog. Sends selected image to load_image()
        '''
        file_name = pg.FileDialog.getOpenFileName(self, "Select Image", "", "FITS Files (*.fits *.fit);;CSV Files (*.csv)")[0]
        self.load_image(file_name)


    
    def calculate_ee(self):
        '''
        Asks ee thread to calculate encircled energy or sets is_ee_queued flag to True if thread is busy.
        '''
        if self.is_ee_thread_busy:
            self.is_ee_queued = True
            return
        
        self.calculate_ee_req.emit(self.ee_roi, self.main_imi.image, self.main_imi)
        self.is_ee_thread_busy = True

        
        
    def ee_thread_next_process(self):
        '''
        Runs after each result from EE Thread. Determines if a new position needs to be run or not. Sets flags accordingly
        '''
        if self.is_ee_queued == True:
            self.calculate_ee_req.emit(self.ee_roi, self.main_imi.image, self.main_imi)
            self.is_ee_queued = False
            return
        else:
            self.is_ee_thread_busy = False
            return

    def ee_result_received(self, ee):

        self.display_ee(ee)
        self.ee_thread_next_process()


        # If live feed is on, calls another frame, as this should be the last thing to process per frame
        if(self.live_cam_button.isChecked()):
            self.request_frame.emit(self.bg_roi, self.main_imi)

        

    def display_ee(self, ee):
        '''
        Updates display of EE after each calculation by EE Thread
        '''
        

        if self.total_counts != 0:
            self.pc_enc_label.setText(f"{np.round(ee / self.total_counts, 4)} ({int(ee)}/{int(self.total_counts)})")
        else:
            self.pc_enc_label.setText(f"0 ({ee}/{self.total_counts})")

    def display_half(self, radius):
        '''
        Updates display of half-encircled radius after each calculation by EE Thread. Draws a circle around that region.
        '''
        self.half_label.setText(str(radius))
        self.half_roi.setSize(radius * 2, center=(0.5, 0.5))



        
        
        

    def dp_roi_size_editing_finished(self):
        '''
        Updates dp_roi_size row of Data Panel
        '''
        self.ee_roi.setSize(float(self.dp_roi_size.text()), center=(0.5, 0.5))


    def closeEvent(self, event):
        '''
        Runs at application exit, closes thread so we don't get errors.
        '''
        self.ee_thread.quit()
        self.ee_thread.wait()
        self.camera_thread.quit()
        event.accept()





class EE_Worker(QtCore.QObject):
    '''
    Thread to manage encircled energy calculations
    '''
    ee_ready = QtCore.Signal(float)
    half_ready = QtCore.Signal(int)

    def __init__(self, parent = None):
        super().__init__(parent)

    @QtCore.Slot(object, object, object)
    def calculate_ee(self, ee_roi, image, image_item):
        '''
        Calculates EE in the ee_roi, returns total count
        '''
        roi_region = ee_roi.getArrayRegion(image, image_item)
        ee = np.sum(roi_region)
        self.half_energy(ee, roi_region)
        self.ee_ready.emit(ee)
        

    def half_energy(self, ee, roi_region):
        '''
        Returns the radius from center of ee_roi necessary to encircle 50% energy of the ee_roi
        '''
        r_min = 1
        r_max = np.shape(roi_region)[0]/2 # Max radius to be searched (half of size(diameter))

        # Calculate half by splitting radius search in half until possible is only one pixel
        while r_max-r_min > 1:
            r_mid = (r_max+r_min)/2
            aperture = CircularAperture((np.shape(roi_region)[0]/2,np.shape(roi_region)[1]/2), r = r_mid)
            aperture_counts = aperture.do_photometry(roi_region, method='center')[0]
            pc_enc = aperture_counts / ee
            if(pc_enc > 0.5):
                r_max = r_mid
            else:
                r_min = r_mid
        
        self.half_ready.emit(round(r_mid))
    
class Camera_Worker(QtCore.QObject):
    frame_ready = QtCore.Signal(np.ndarray)
    first_frame = QtCore.Signal()
    
    def __init__(self, parent = None):
        super().__init__(parent)
        asi.init(r"C:\Program Files\ASIStudio\ASICamera2.dll")

    def update_camera_settings(self):
        '''
        Sets camera settings.
        '''
        try:
            self.camera = asi.Camera(asi.list_cameras()[0])
            self.camera.set_roi(bins=4)
            self.camera.set_image_type(asi.ASI_IMG_RAW16)
        except Exception as e:
            print("No Camera is Connected")

    def start_live(self):
        '''
        Starts the camera live feed.
        '''
        self.update_camera_settings()
        self.timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 100000 + 500
        
        self.camera.start_video_capture()
        frame = self.camera.capture_video_frame(timeout=self.timeout)
        self.frame_ready.emit(frame)

        QtCore.QThread.msleep(250)
        self.first_frame.emit()


        
        
    def send_frame(self, bg_roi, main_imi):
        '''
        Takes and processes a frame before sending it to be displayed in the main window.
        '''
        frame = self.camera.capture_video_frame(timeout=self.timeout)
        background = np.average(bg_roi.getArrayRegion(frame, main_imi))
        bg_subbed_frame = frame - background
        bg_subbed_frame[bg_subbed_frame < 0] = 0
        self.frame_ready.emit(bg_subbed_frame)


        

    

    
        
        


    

    
        










# Display Widget as new Window
win = MainWindow()


win.show()

app.exec()
