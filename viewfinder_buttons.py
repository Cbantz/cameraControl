import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from diffractometer_tools import Diffractometer_Tools

class ViewfinderButtons(QtWidgets.QWidget):
    """
    Collection of buttons to be used with a viewfinder class.

    Includes:
        - Centroid
        - Reset ROIs
        - Show/Hide Crosshair
    """
    def __init__(self, diff_tools : Diffractometer_Tools = None):
        super().__init__(parent=None)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hlayout)

        self.reset_roi_button = QtWidgets.QPushButton("Reset ROIs")
        self.show_hide_crosshairs_button = QtWidgets.QPushButton("Show/hide Crosshair")


        if diff_tools:
            self.centroid_button = diff_tools.centering_monitor.centroid_button
            self.hlayout.addWidget(self.centroid_button)
            self.hlayout.addWidget(diff_tools.centering_monitor.inner_com_check)
        else:
            print("No Diffractometer Tools connected to Viewfinder Buttons")
        self.hlayout.addWidget(self.reset_roi_button)
        self.hlayout.addWidget(self.show_hide_crosshairs_button)


            



if __name__ == "__main__":
    app = pg.mkQApp()
    widget = ViewfinderButtons()
    widget.show()
    app.exec()