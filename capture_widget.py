import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from folder_selector import Folder_Selector

class Capture_Widget(QtWidgets.QWidget):
    num_frames : int = 1
    def __init__(self):
        super().__init__(parent=None)
        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)
        self.button = Capture_Button()
        self.num = Num_Capture_Line()
        self.folder_select = Folder_Selector()
        self.gridlayout.addWidget(self.button, 0, 0, 1, 1)
        self.gridlayout.addWidget(self.num, 0, 1, 1, 1)
        self.gridlayout.addWidget(self.folder_select, 1, 0, 1, 2)

        self.num.edit.editingFinished.connect(self.num_updated)
        self.num.edit.setText(str(self.num_frames))

    def num_updated(self):
        self.num_frames = int(self.num.edit.text())
        self.button.update_num_frames(self.num_frames)

class Capture_Button(QtWidgets.QPushButton):
    def __init__(self):
        super().__init__(parent=None)
        
    
    def update_num_frames(self, count : int = None):
        self.setText(f"Capture {count} frames.")

class Num_Capture_Line(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hboxlayout)
        self.label = QtWidgets.QLabel("# Of Frames: ")
        self.edit = QtWidgets.QLineEdit()
        self.hboxlayout.addWidget(self.label)
        self.hboxlayout.addWidget(self.edit)


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Capture_Widget()
    widget.show()
    app.exec()




