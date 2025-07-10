import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from camera import Camera
from motor_controller import Motor_Controller
from EEGUI import EEGUI_Manager
from signals import signals as sig
from diffractometer_tools import Diffractometer_Tools as dt

class Organizer(QtCore.QObject):
    threads = []
    
    def __init__(self):
        self.camera = Camera()
        self.gui = EEGUI_Manager()
        # self.motor = Motor_Controller()
        # self.dt = dt()
        self.setup_camera()
        self.setup_gui()



    def setup_gui(self):
        self.gui_thread = QtCore.QThread()
        self.gui.moveToThread(self.gui_thread)
        self.gui_thread.start()
        self.threads.append(self.gui_thread)
        self.camera.settings.moveToThread(self.gui_thread)
        self.gui.set_camera(self.camera)
        
        

    def setup_camera(self):
        self.camera_thread = QtCore.QThread()
        self.camera.moveToThread(self.camera_thread)
        self.camera_thread.start()
        self.threads.append(self.camera_thread)
        



        


    def connect_to_camera(self):
        
        self.camera = Camera()
        self.cam_thread = QtCore.QThread()
        self.camera.moveToThread(self.cam_thread)
        self.cam_thread.start()
        self.threads.append(self.cam_thread)

        print(f"Connected to camera: {self.camera}")
    

    def connect_to_motor(self):
        self.motor = Motor_Controller()

    def connect_to_diffractometer_tools(self):
        self.dt = dt(self.motor, self.camera)

    def get_camera_instance(self):
        return self.camera
    
    def get_motor_instance(self):
        return self.motor
    
    def get_window_instance(self):
        return self.window
    
    def get_signals_instance(self):
        return self.signals
    

    def closeEvent(self, event):
        for thread in self.threads:
            thread.quit()
            thread.wait()

            event.accept()
