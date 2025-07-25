import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

class Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent = None)
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.vboxlayout)
        self.back_ref_button = QtWidgets.QPushButton("Set Back Reflection Angle")
        self.zeroth_order_button = QtWidgets.QPushButton("Set Zeroth Order Angle")
        self.vboxlayout.addWidget(self.back_ref_button)
        self.vboxlayout.addWidget(self.zeroth_order_button)


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Widget()
    widget.show()
    app.exec()
