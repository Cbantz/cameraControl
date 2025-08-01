import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from camera import CameraController

class ViewfinderButtons(QtWidgets.QWidget):
    """
    Collection of buttons to be used with a viewfinder class.

    Includes:
        - Centroid
        - Reset ROIs
        - Show/Hide Crosshair
    """
    def __init__(self, camera: CameraController = None):
        super().__init__(parent=None)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hlayout)

        self.reset_roi_button = QtWidgets.QPushButton("Reset ROIs")
        self.show_hide_crosshairs_button = QtWidgets.QPushButton("Show/hide Crosshair")


        if camera:
            self.centroid_button = camera.worker.spot_tracker.centroid_button
            self.hlayout.addWidget(self.centroid_button)
            self.hlayout.addWidget(camera.worker.spot_tracker.inner_com_check)
        else:
            print("No Camera connected to Viewfinder Buttons")
        self.hlayout.addWidget(self.reset_roi_button)
        self.hlayout.addWidget(self.show_hide_crosshairs_button)


            



if __name__ == "__main__":
    app = pg.mkQApp()
    widget = ViewfinderButtons()
    widget.show()
    app.exec()