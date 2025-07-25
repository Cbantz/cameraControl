import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

class Folder_Selector(QtWidgets.QWidget):
    folder_selected : str
    def __init__(self):
        super().__init__(parent=None)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hboxlayout)
        self.select_button = QtWidgets.QPushButton("Select Folder")
        self.filepath_label = QtWidgets.QLabel("No Folder Selected")
        self.hboxlayout.addWidget(self.select_button)
        self.hboxlayout.addWidget(self.filepath_label)

        self.select_button.clicked.connect(self.button_pressed)


    def button_pressed(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")

        if path:
            self.folder_selected = path
            self.filepath_label.setText(str(path))
            print(F"Photos will save to {path}")
        else:
            print("No Folder Selected")


if __name__ == "__main__":
    app = pg.mkQApp()
    widget = Folder_Selector()
    widget.show()
    app.exec()
