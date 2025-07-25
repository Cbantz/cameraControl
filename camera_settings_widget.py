import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from Exposure_Setting_Widget import Exposure_Setting_Widget
from Gain_Setting_Widget import Gain_Setting_Widget


class Camera_Settings_Widget(QtWidgets.QWidget):
    """
    Widget for adjusting camera settings in a GUI.
    """
    def __init__(self):
        super().__init__(parent = None)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.set_up_exposure()
        self.set_up_gain()

    def set_up_exposure(self):
        self.exposure_widget = Exposure_Setting_Widget((0, 100000))
        self.grid_layout.addWidget(self.exposure_widget, 1, 0, 1, 2)


    def set_up_gain(self):
        self.gain_widget = Gain_Setting_Widget((0, 800))
        self.grid_layout.addWidget(self.gain_widget, 2, 0, 1, 2)




if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Camera_Settings_Widget()
    widget.show()
    app.exec()


