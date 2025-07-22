from pyqtgraph.Qt import QtWidgets
from main_win_gui_oat import MainWindow
from roi_manager import ROI_Manager
from camera import CameraController
from diffractometer_gui import Diffractometer_GUI
import tracemalloc

class GUI_OAT(QtWidgets.QApplication):
    '''
    Main application for the GUI OAT Viewer.
    '''
    def __init__(self):
        super().__init__(parent = None)
        tracemalloc.start()
        print("Instantiating ROI Manager")
        self.roi_manager = ROI_Manager()
        print("Instantiating Camera")
        self.camera = None
        # Try to instantiate a CameraController.
        try:
            self.camera = CameraController(roi_manager=self.roi_manager)
        except Exception as e:
            print(e)

        print("Starting diff GUI")
        self.diff_gui = Diffractometer_GUI(camera=self.camera, roi_manager=self.roi_manager)
        print("Starting MainWindow")
        self.main_win = MainWindow()
        self.main_win.show()
        self.main_win.setCentralWidget(self.diff_gui)

        self.trace_button = QtWidgets.QPushButton("Trace")
        self.trace_button.clicked.connect(self.take_memory_snapshot)
        self.trace_button.show()

    
    def take_memory_snapshot(self):

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print("\n[ Top memory usage lines ]")
        for stat in top_stats[:10]:
            print(stat)

if __name__ == "__main__":
    GUI_OAT().exec()


