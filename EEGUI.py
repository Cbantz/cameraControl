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

    def pick_file(self):
        '''
        Loads File Dialog. Sends selected image to load_image()
        '''
        print("Open File Picker")
        file_name = pg.FileDialog.getOpenFileName(None, "Select Image", "", "FITS Files (*.fits *.fit);;CSV Files (*.csv)")[0]
        self.central_widget.start_static_im_show(file_name)
    


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


    

    
        
        


    

    
        











