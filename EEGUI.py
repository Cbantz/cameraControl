import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from astropy.io import fits
import numpy as np


# Start Qt app
app = pg.mkQApp("Image Display")

# Create main graphics window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        

        self.setWindowTitle("FITS File Viewer")

        # Create Main Grid
        self.win1 = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.win1)

        # Create Image Widget 
        self.p1 = pg.GraphicsLayoutWidget()

        # Create Main Image
        self.main_imi = pg.ImageItem(image=np.array([[0]]), axisOrder='row-major')
        self.main_imi.sigImageChanged.connect(self.main_image_changed)

        # Create Original Image Data
        self.og_im_data = self.main_imi.image
        self.total_counts = 0

        # Create HistogramLUTItem
        self.hist = pg.HistogramLUTItem()
        self.hist.autoHistogramRange()
        

        # Create View
        self.view = self.p1.addViewBox(invertY = True)
        self.view.setAspectLocked(True)

        # Create EE ROI
        self.ee_roi = pg.CircleROI((0,0), size=100, scaleSnap = True, snapSize = 1)
        self.ee_roi.removeHandle(0)
        self.ee_roi.addScaleHandle((0, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 0), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((0, 1), (0.5, 0.5), lockAspect=True)
        self.ee_roi.addScaleHandle((1, 1), (0.5, 0.5), lockAspect=True)
        
        self.ee_roi.sigRegionChanged.connect(self.calculate_ee)
        self.ee_roi.setVisible(False)

        # Create Background ROI
        self.bg_roi = pg.RectROI((0,0), size=300)
        self.bg_roi.sigRegionChanged.connect(self.bg_reg_changed)
        self.bg_roi.setVisible(False)

        # Create Background Select Button
        self.bg_set_button = pg.QtWidgets.QPushButton("Set Background")
        self.bg_set_button.pressed.connect(self.set_background)


        # Add Items to p1
        self.p1.addItem(self.hist)

        # Add Items to View
        self.view.addItem(self.main_imi)
        self.view.addItem(self.ee_roi)
        self.view.addItem(self.bg_roi)
        
        # Create File Picker
        file_button = QtWidgets.QPushButton("Open File")
        file_button.clicked.connect(self.pick_file)

        # Create Data Panel
        self.dp1 = pg.GraphicsLayoutWidget()
        self.dp1grid=QtWidgets.QVBoxLayout(self.dp1)

        # Create Data Panel Form
        dp_form = QtWidgets.QWidget()
        dp_form_layout = QtWidgets.QFormLayout(dp_form)

        # Data Panel Data
        # Title Label
        dp_text = pg.QtWidgets.QLabel("Data Panel")

        # EE ROI Size Line Edit
        self.dp_roi_size = pg.QtWidgets.QLineEdit(f"{self.ee_roi.size().x()}")
        self.dp_roi_size.editingFinished.connect(self.dp_roi_size_editing_finished)
        dp_roi_size_validator = QtGui.QIntValidator(bottom=0, top=400)
        self.dp_roi_size.setValidator(dp_roi_size_validator)

        # Percent Enclosed
        self.pc_enc_label = pg.QtWidgets.QLabel()


        # Add Rows to Data Panel Form
        dp_form_layout.addRow("ROI Radius: ", self.dp_roi_size)
        dp_form_layout.addRow("Energy Enclosed: ", self.pc_enc_label)

        # Arrange Widgets in Data Panel
        self.dp1grid.addWidget(dp_text, 1)
        self.dp1grid.addWidget(dp_form, 10)



        

        # Arrange Widgets in Master Widget
        self.grid.addWidget(self.p1, 0, 0, 2, 2)
        self.grid.addWidget(self.dp1, 0, 3)

        # Set the central widget of the Window and add toolbar
        self.setCentralWidget(self.win1)

        #Create Toolbar, Add items
        self.toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addWidget(file_button)
        self.toolbar.addWidget(self.bg_set_button)


    
    def load_image(self, filepath):
        # Open Selected Image
        hdul = fits.open(filepath)
        header, data = hdul[0].header, hdul[0].data

        self.main_imi.setImage(data) # Set as Main Image
        self.og_im_data = data #Set as OG Image
        self.hist.setImageItem(self.main_imi) # Set as Hist Image

        x,y = np.shape(data) 



        # ROI parameters
        roi_size = 100
        roi_pos = ((y - roi_size) / 2, (x - roi_size) / 2)  # Centered position
        roi_bounds = pg.QtCore.QRectF(pg.QtCore.QPoint(0, 0), pg.QtCore.QPoint(y, x))
        

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
        print("change")
        self.total_counts = np.sum(self.main_imi.image)
    
    def set_background(self):
        '''
        Set the background count when button is pressed, remove button.
        '''
        bg_region = self.bg_roi.getArrayRegion(self.main_imi.image, self.main_imi) # Get background region from bg_roi
        avg_bg_count = np.average(bg_region)
        # Adjust image data and display operational data
        bg_rem_data = self.og_im_data - avg_bg_count
        bg_rem_data[bg_rem_data<0] = 0
        self.main_imi.setImage(bg_rem_data) # Remove average background count
        self.hist.autoHistogramRange()
        self.calculate_ee()
        self.bg_set_button.setVisible(False)


    def bg_reg_changed(self):
        '''
        Show 'set background' button and revert to original image
        '''
        if np.array_equal(self.main_imi.image, self.og_im_data) == False:
            self.main_imi.setImage(self.og_im_data)
            self.bg_set_button.setVisible(True)
            self.calculate_ee()


        

    def pick_file(self):
        '''
        Loads File Dialog. Sends selected image to load_image()
        '''
        file_name = pg.FileDialog.getOpenFileName(self, "Select Image", "", "FITS Files (*.fits *.fit);;CSV Files (*.csv)")[0]
        self.load_image(file_name)

    def calculate_ee(self):
        '''
        Subtracts average background from image, calculates percent of energy enclosed in EE_ROI
        '''
        roi_region = self.ee_roi.getArrayRegion(self.main_imi.image, self.main_imi)
        ee = np.sum(roi_region)
        self.dp_roi_size.setText(f"{int(self.ee_roi.size().x())}")
        if self.total_counts != 0:
            self.pc_enc_label.setText(f"{np.round(ee / self.total_counts, 4)} ({int(ee)}/{int(self.total_counts)})")
        else:
            self.pc_enc_label.setText(f"0 ({ee}/{self.total_counts})")
        

    def dp_roi_size_editing_finished(self):
        '''
        Updates dp_roi_size row of Data Panel
        '''
        print("edited")
        self.ee_roi.setSize(float(self.dp_roi_size.text()), center=(0.5, 0.5))
        










# Display Widget as new Window
win = MainWindow()


win.show()

app.exec()


#BUG NOTES
'''
* Background toggles on and off effectively because it removes from og
* 
'''