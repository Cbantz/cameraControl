import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np

class Data_Display_Widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        title = QtWidgets.QLabel("DATA")
        layout.addWidget(title, 0, 0, 1, 1)
        self.form = Data_Form()
        self.form.setMinimumWidth(400)
        layout.addWidget(self.form, 1, 0, 1, 1)


    def set_up_ee_roi(self, roi: pg.ROI):
        self.ee_roi = roi
        self.form.set_ee_roi(roi)




    

class Data_Form(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.layout = QtWidgets.QFormLayout()
        self.setLayout(self.layout)

        self._add_position_rows()
        self._add_radius_row()
        self._add_energy_stats()


    def _add_position_rows(self):
        
        self.roi_pos_x = QtWidgets.QLineEdit()
        self.roi_pos_y = QtWidgets.QLineEdit()

        self.layout.addRow("ROI Pos X: ", self.roi_pos_x)
        self.layout.addRow("ROI Pos Y: ", self.roi_pos_y)

    def _add_radius_row(self):
        self.roi_radius = QtWidgets.QLineEdit()
        self.layout.addRow("ROI Radius: ", self.roi_radius)

    def _add_energy_stats(self):
        self.pc_enc_label = QtWidgets.QLabel()
        self.half_label = QtWidgets.QLabel()

        self.layout.addRow("% Enclosed: ", self.pc_enc_label)
        self.layout.addRow("50% Enclosed Radius: ", self.half_label)

    def set_ee_roi(self, roi: pg.ROI):
        self.ee_roi = roi
        self.ee_roi.sigRegionChanged.connect(self._on_ee_roi_changed)

    def _on_ee_roi_changed(self):
        x, y = self.ee_roi.pos()
        radius = self.ee_roi.size()[0]/2
        self.roi_pos_x.setText(str(np.round(x+radius)))
        self.roi_pos_y.setText(str(np.round(y+radius)))

        
        self.roi_radius.setText(str(np.round(radius)))

    def set_half_label(self, radius):
        self.half_label.setText(str(radius))

    def set_ee_label(self, ee: float, pc_enc: float, total_sum : float):
        self.pc_enc_label.setText(f"{np.round(pc_enc * 100, 4)}%: {int(np.round(ee))}/{int(np.round(total_sum))}")




if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Data_Display_Widget()
    widget.show()
    app.exec()