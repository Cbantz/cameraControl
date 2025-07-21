from pyqtgraph.Qt import QtWidgets
from main_win_gui_oat import MainWindow
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_gui import Diffractometer_GUI

class GUI_OAT(QtWidgets.QApplication):
    def __init__(self):
        super().__init__(parent = None)
        
        self.roi_manager = ROI_Manager()
        self.camera = None
        try:
            self.camera = CameraController(roi_manager=self.roi_manager)
        except Exception as e:
            print(e)


        self.diff_gui = Diffractometer_GUI(camera=self.camera, roi_manager=self.roi_manager)
        self.main_win = MainWindow()
        self.main_win.show()
        self.main_win.setCentralWidget(self.diff_gui)


if __name__ == "__main__":
    GUI_OAT().exec()


