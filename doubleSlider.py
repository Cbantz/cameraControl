from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QSlider


class DoubleSlider(QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decimals = 4
        self._max_int = 10**self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        self._min_value = 0.0
        self._max_value = 1.0

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        return (
            float(super().value()) / self._max_int * self._value_range + self._min_value
        )

    def setValue(self, value):
        super().setValue(
            int((value - self._min_value) / self._value_range * self._max_int)
        )

    def setMinimum(self, value):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._min_value = value
        self.setValue(self.value())

    def setMaximum(self, value):
        if value < self._min_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._max_value = value
        self.setValue(self.value())

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value


class Window(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        slider = DoubleSlider(self)  # Add slider
        slider.setMinimum(0.0)
        slider.setMaximum(10.0)
        slider.setValue(1.0)
        # slider.maximumHeight = 100
        # slider.minimumHeight = 100
        slider.setMaximumWidth(500)
        slider.setMinimumWidth(500)
        slider.setOrientation(1)
        slider.valueChanged.connect(self.slider_value_changed)  # Connect change event
        print(slider.value())

        # Add text label with the current exposure time
        self.label = QLabel(self)
        self.label.setText("0.000")
        self.label.move(100, 100)
        self.update_label(slider.value())

    # Called every time the slider value changes
    def slider_value_changed(self, value):
        value = self.sender().value()
        print(f"{value:.3f}")
        self.update_label(value)

    def update_label(self, value):
        self.label.setText(f"{value:.3f}")
        self.label.move(100, 100)


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
