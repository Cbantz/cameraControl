import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

class Exposure_Setting_Widget(QtWidgets.QWidget):
    def __init__(self, range: tuple):
        super().__init__(parent = None)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.exposure_range: tuple = range

        self.slider = Exposure_Slider(self.exposure_range)
        self.slider.valueChanged.connect(self.update_edit_text)
        self.slider_edit = Exposure_Text(self.exposure_range)
        self.slider_edit.editingFinished.connect(self.update_slider_value)
        self.label = Exposure_Label()

        self.grid_layout.addWidget(self.slider, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.slider_edit, 1, 2, 1, 1)
        self.grid_layout.addWidget(self.label, 0, 0, 1, 1)

        self.grid_layout.setColumnStretch(0, 3)



    def update_slider_value(self):
        print(int(self.slider_edit.text()))
        self.slider.setValue(int(self.slider_edit.text()))

    def update_edit_text(self):
        self.slider_edit.setText(str(self.slider.value()))


class Exposure_Slider(QtWidgets.QSlider):
    def __init__(self, range: tuple):
        super().__init__(parent=None)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setRange(range[0], range[1])
        print(range)
        self.setTickInterval(50)
        self.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)
        self.setMinimumWidth(200)
        self.setTracking(True)
        

class Exposure_Text(QtWidgets.QLineEdit):
    def __init__(self, range):
        super().__init__(parent=None)
        validator = QtGui.QIntValidator(range[0], range[1])
        self.setValidator(validator)

class Exposure_Label(QtWidgets.QLabel):
    def __init__(self):
        super().__init__(parent=None)
        self.setText(f"Exposure (\u03bcs)")
        self.setMinimumSize(40, 40)


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Exposure_Setting_Widget((100, 1000))
    widget.show()
    app.exec()