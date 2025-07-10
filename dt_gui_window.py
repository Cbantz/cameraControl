import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from signals import signals as sig
from motor_controller import Motor_Controller as mc


class dt_window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__(parent=None)
        
        camera_movement_panel = movement_control_panel()
        

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(camera_movement_panel, 0, 0, 1, 1)





class movement_control_panel(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__(parent=None)
        neg_fast = camera_move_button("\u21C7", -2)
        neg_slow = camera_move_button("\u2190", -1)
        pos_slow = camera_move_button("\u2192", 1)
        pos_fast = camera_move_button("\u21C9", 2)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(neg_fast)
        layout.addWidget(neg_slow)
        layout.addWidget(pos_slow)
        layout.addWidget(pos_fast)

        self.setLayout(layout)
        



class camera_move_button(QtWidgets.QPushButton):

    def __init__(self, text:str, velocity: float):
        super().__init__(parent=None)
        self.velocity = velocity
        self.setText(text)
        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

    def _button_pressed(self):
        print("pressed")
        sig.motor_move_camera_indef_req.emit(self.velocity)

    def _button_released(self):
        print("released")
        sig.motor_stop_camera_req.emit()



if __name__ == '__main__':

    
    test_app = pg.mkQApp()
    motors = mc("COM6")
    
    window = dt_window()
    window.show()

    test_app.exec()



