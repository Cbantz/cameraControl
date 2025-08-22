import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from folder_selector import Folder_Selector

class Capture_Widget(QtWidgets.QWidget):
    num_frames : int = 1
    def __init__(self):
        super().__init__(parent=None)
        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)
        self.button = QtWidgets.QPushButton("Capture")
        self.name_edit = QtWidgets.QLineEdit()
        self.folder_select = Folder_Selector()
        self.gridlayout.addWidget(self.button, 1, 2, 1, 1)
        self.gridlayout.addWidget(self.folder_select, 1, 0, 1, 2)
        self.gridlayout.addWidget(self.name_edit, 0, 0, 1, 2)



if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Capture_Widget()
    widget.show()
    app.exec()




