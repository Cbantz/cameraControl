from camera import Camera
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import zwoasi as asi
from Exposure_Setting_Widget import Exposure_Setting_Widget
from Gain_Setting_Widget import Gain_Setting_Widget


class Cam_GUI(QtWidgets.QWidget):
    def __init__(self, camera : Camera = None):
        super().__init__(parent = None)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        try:
            self.set_up_camera(camera)
            self.set_up_exposure()
            self.set_up_gain()
        except AttributeError as e:
            print(f"Camera not connected to GUI error: {e}")
        
    
    def set_up_camera(self, camera: Camera):
        self.camera = camera
        self.settings = self.camera.settings

    def set_up_exposure(self):
        self.exposure_widget = Exposure_Setting_Widget((100, 1000))
        self.grid_layout.addWidget(self.exposure_widget, 1, 0, 1, 2)
        self.exposure_widget.slider.valueChanged.connect(self.settings.set_exposure(self.exposure_widget.slider.value()))


    def set_up_gain(self):
        self.gain_widget = Gain_Setting_Widget((0, 200))
        self.grid_layout.addWidget(self.gain_widget, 2, 0, 1, 2)
        self.gain_widget.slider.valueChanged.connect(self.settings.set_gain(self.gain_widget.slider.value()))



if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Cam_GUI()
    widget.show()
    app.exec()


