import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets
import numpy as np
from roi_manager import ROI_Manager
from ee_processor import EE_Processor
from camera import CameraController

class Data_Display_Widget(QtWidgets.QWidget):
    '''
    Widget that displays stats on things visible in viewbox
    '''
    def __init__(self, parent = None, roi_manager: ROI_Manager = None, ee_processor: EE_Processor =None, camera: CameraController = None):
        super().__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        #Instantiate Children
        title = Stats_Title()
        self.form = Data_Form(roi_manager=roi_manager, ee_processor=ee_processor, camera=camera)



        #Arrange Layout
        layout.addWidget(title, 0, 0, 1, 1)
        layout.addWidget(self.form, 1, 0, 1, 1)
        self.form.setMinimumWidth(400)


class Data_Form(QtWidgets.QWidget):
    '''
    Form style widget, can display basic lines of text, both editable and not.
    '''
    def __init__(self, parent = None, roi_manager: ROI_Manager = None, ee_processor: EE_Processor = None, camera: CameraController = None):
        super().__init__(parent)
        self.layout = QtWidgets.QFormLayout()
        self.setLayout(self.layout)

        #Instantiate Children
        self.add_position_rows()
        self.add_radius_row()
        self.add_energy_stats()
        self.add_raw_frame_stats()

        if roi_manager:
            self.ee_roi = roi_manager.ee_roi
            self.ee_roi.sigRegionChanged.connect(self.ee_roi_changed)
        else:
            print("No ROI Manager connected to Data Form")

        if ee_processor:
            ee_processor.worker.ee_ready.connect(self.set_ee_label)
            ee_processor.worker.half_ready.connect(self.set_half_label)
        else:
            print("EE Processor not connected to Data Form")

        if camera:
            camera.worker.frame_raw_stats.connect(self.set_frame_stats)
        else:
            print("No Camera connected to Data Form")


    def add_position_rows(self):
        
        self.roi_pos_x = QtWidgets.QLineEdit()
        self.roi_pos_y = QtWidgets.QLineEdit()

        self.layout.addRow("ROI Pos X: ", self.roi_pos_x)
        self.layout.addRow("ROI Pos Y: ", self.roi_pos_y)

    def add_radius_row(self):
        self.roi_radius = QtWidgets.QLineEdit()
        self.layout.addRow("ROI Radius: ", self.roi_radius)

    def add_energy_stats(self):
        self.pc_enc_label = QtWidgets.QLabel()
        self.half_label = QtWidgets.QLabel()

        self.layout.addRow("% Enclosed: ", self.pc_enc_label)
        self.layout.addRow("50% Enclosed Radius: ", self.half_label)

    def add_raw_frame_stats(self):
        self.min_count_label = QtWidgets.QLabel()
        self.max_count_label = QtWidgets.QLabel()

        self.layout.addRow("Min Pixel Value (raw): ", self.min_count_label)
        self.layout.addRow("Max Pixel Value (raw): ", self.max_count_label)

    def ee_roi_changed(self):
        x, y = self.ee_roi.pos()
        radius = self.ee_roi.size()[0]/2
        self.roi_pos_x.setText(str(np.round(x+radius)))
        self.roi_pos_y.setText(str(np.round(y+radius)))

        
        self.roi_radius.setText(str(np.round(radius)))

    def set_half_label(self, radius):
        self.half_label.setText(str(round(radius, 3)))

    def set_ee_label(self, ee: float, pc_enc: float, total_sum : float):
        self.pc_enc_label.setText(f"{np.round(pc_enc * 100, 4)}%: {int(np.round(ee))}/{int(np.round(total_sum))}")

    def set_frame_stats(self, stats: dict):
        self.min_count_label.setText(str(stats["Min"]))
        self.max_count_label.setText(str(stats["Max"]))

class Stats_Title(QtWidgets.QLabel):
    def __init__(self):
        super().__init__(parent=None)
        self.setText("STATS")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.setFont(font)




if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Data_Display_Widget()
    widget.show()
    app.exec()