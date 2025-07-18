import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):



    def __init__(self):
        super().__init__(parent=None)

        self.setWindowTitle("OAT VIEWER (University of Iowa OAT Lab)")





if __name__ == '__main__':
    app = pg.mkQApp()
    window = MainWindow()
    window.show()
    app.exec()