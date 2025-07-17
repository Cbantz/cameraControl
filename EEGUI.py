import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from astropy.io import fits
from scipy.ndimage import center_of_mass
import numpy as np
import main_win_gui_oat, ee_gui_central_widget
from camera import Camera


class EEGUI_Manager(QtCore.QObject):
    def __init__(self):
        super().__init__(parent = None)
        
        # Initialize main components
        self.main_win = main_win_gui_oat.MainWindow()
        print("Main Window Initialized")
        self.central_widget = ee_gui_central_widget.EE_GUI_Central_Widget()
        print("Central Widget Initialized")
        
        # Run setup scripts
        self._setup_main_win()
        self._setup_central_widget()

        self.main_win.show()



    def _setup_main_win(self):
        '''
        Runs once at the start, passes variables and makes connections with the Main Window.
        '''
        self.main_win.setCentralWidget(self.central_widget)
        self.main_win.file_button.clicked.connect(self.pick_file)
        self.main_win.centroid_button.clicked.connect(self.central_widget.view.centroid)
        self.main_win.live_button_pressed.connect(self.central_widget.start_camera)
        self.main_win.live_button_released.connect(self.central_widget.start_static_im_show)
        

    def _setup_central_widget(self):
        '''
        Runs once at the start, passes variables and makes connections with central widget.
        '''
        self.central_widget.view._set_centroid_button(self.main_win.centroid_button)


    def set_camera(self, camera: Camera):
        '''
        Sets camera for self and children.
        '''
        self.camera = camera
        self.central_widget._setup_camera(camera)

    def pick_file(self):
        '''
        Loads File Dialog. Sends selected image to load_image()
        '''
        print("Open File Picker")
        file_name = pg.FileDialog.getOpenFileName(None, "Select Image", "", "FITS Files (*.fits *.fit);;CSV Files (*.csv)")[0]
        self.central_widget.start_static_im_show(file_name) # Displays selected image in central widget using static image handler.
    


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


    

    
        
        


    

    
        











