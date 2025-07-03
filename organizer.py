import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
from camera_controller import Camera_Controller
from motor_controller import Motor_Controller
from EEGUI import MainWindow as main_win
from signals import signals as sig

class Organizer(QtCore.QObject):
    threads = []
    
    def __init__(self):
        sig.connect_to_camera.connect(self.connect_to_camera)

    def connect_to_window(self):
        self.window = main_win()


        


    def connect_to_camera(self):
        
        self.camera = Camera_Controller()
        self.cam_thread = QtCore.QThread()
        self.camera.moveToThread(self.cam_thread)
        self.cam_thread.start()
        self.threads.append(self.cam_thread)

        print(f"Connected to camera: {self.camera}")
    

    def connect_to_motor(self):
        self.motor = Motor_Controller()

    def get_camera_instance(self):
        return self.camera
    
    def get_motor_instance(self):
        return self.motor
    
    def get_window_instance(self):
        return self.window
    
    def get_signals_instance(self):
        return self.signals
    
