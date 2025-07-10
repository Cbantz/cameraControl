import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):

    ee_roi_created = QtCore.Signal(pg.ROI)
    live_button_pressed = QtCore.Signal()
    live_button_released = QtCore.Signal()

    def __init__(self):
        super().__init__(parent=None)

        self.setWindowTitle("EE GUI (University of Iowa OAT Lab)")

        # Create Centroid Button
        self.centroid_button = pg.QtWidgets.QPushButton("Centroid")


        # Create Camera button
        self.live_cam_button = QtWidgets.QPushButton("Live Camera View")
        self.live_cam_button.setCheckable(True)
        self.live_cam_button.clicked.connect(self.live_button_clicked)

        # Create File Picker
        self.file_button = QtWidgets.QPushButton("Open File")

        #Create Toolbar, Add items
        self.toolbar = QtWidgets.QToolBar("Main Toolbar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addWidget(self.file_button)
        self.toolbar.addWidget(self.centroid_button)
        self.toolbar.addWidget(self.live_cam_button)


    def live_button_clicked(self):
        if(self.live_cam_button.isChecked()):
            self.live_button_pressed.emit()

        else:
            self.live_button_released.emit()



if __name__ == '__main__':
    app = pg.mkQApp()
    window = MainWindow()
    window.show()
    app.exec()