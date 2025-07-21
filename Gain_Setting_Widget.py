import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui

class Gain_Setting_Widget(QtWidgets.QWidget):
    def __init__(self, range):
        super().__init__(parent = None)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.gain_range: tuple = range

        self.slider = Gain_Slider(self.gain_range)
        self.slider.valueChanged.connect(self.update_edit_text)
        self.slider_edit = Gain_Text(self.gain_range)
        self.slider_edit.editingFinished.connect(self.update_slider_value)
        self.label = Gain_Label()

        self.grid_layout.addWidget(self.slider, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.slider_edit, 1, 2, 1, 1)
        self.grid_layout.addWidget(self.label, 0, 0, 1, 1)

        self.grid_layout.setColumnStretch(0, 3)



    def update_slider_value(self):
        print(int(self.slider_edit.text()))
        self.slider.setValue(int(self.slider_edit.text()))

    def update_edit_text(self):
        self.slider_edit.setText(str(self.slider.value()))


class Gain_Slider(QtWidgets.QSlider):
    def __init__(self, range: tuple):
        super().__init__(parent=None)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setRange(range[0], range[1])
        print(range)
        self.setTickInterval(50)
        self.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)
        self.setMinimumWidth(200)
        self.setTracking(True)
        

class Gain_Text(QtWidgets.QLineEdit):
    def __init__(self, range):
        super().__init__(parent=None)
        validator = QtGui.QIntValidator(range[0], range[1])
        self.setValidator(validator)

class Gain_Label(QtWidgets.QLabel):
    def __init__(self):
        super().__init__(parent=None)
        self.setText("Gain")
        self.setMinimumSize(40, 40)


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Gain_Setting_Widget((100, 1000))
    widget.show()
    app.exec()