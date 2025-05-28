from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from pyqt_advanced_slider import Slider


class FloatSlider(QWidget):
    def __init__(self, minimum, maximum, decimals=2, parent=None):
        super().__init__(parent)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(minimum * 10**decimals))
        self.slider.setMaximum(int(maximum * 10**decimals))
        self.slider.valueChanged.connect(self.update_label)

        self.label = QLabel()
        self.update_label(self.slider.value())

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"{value / 10**2:.2f}")


class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimal=3, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        print(f"Type of decimals: {type(decimal)}")
        self._multi = 10**3

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))


class Window(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        slider = Slider(self)  # Add slider
        slider.setRange(0, 10)  # Set min and max
        slider.setValue(0.05)  # Set value
        slider.setMaximumWidth(512)  # Set width
        slider.setMinimumWidth(512)  # Set width
        slider.setFloat(True)
        slider.setDecimals(2)
        slider.valueChanged.connect(self.slider_value_changed)  # Connect change event

        floatSlider = DoubleSlider(self)
        floatSlider.setMinimum(0)
        floatSlider.setMaximum(10)
        floatSlider.setValue(0.53)

        floatSlider2 = FloatSlider(0, 10)

    # Called every time the slider value changes
    def slider_value_changed(self, value):
        print(value)


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
