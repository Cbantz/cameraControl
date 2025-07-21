import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

class ViewfinderButtons(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hlayout)


        self.centroid_button = QtWidgets.QPushButton("Centroid")
        self.centroid_button.setCheckable(True)
        self.reset_roi_button = QtWidgets.QPushButton("Reset ROIs")
        self.show_hide_crosshairs_button = QtWidgets.QPushButton("Show/hide Crosshair")

        self.hlayout.addWidget(self.centroid_button)
        self.hlayout.addWidget(self.reset_roi_button)
        self.hlayout.addWidget(self.show_hide_crosshairs_button)



if __name__ == "__main__":
    app = pg.mkQApp()
    widget = ViewfinderButtons()
    widget.show()
    app.exec()