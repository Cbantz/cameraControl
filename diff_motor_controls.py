import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from motor_controller import Motor_Controller


class motor_control_widget(QtWidgets.QWidget):

    def __init__(self, motor: Motor_Controller = None):
        super().__init__(parent=None)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        
        if(motor):
            self.motor = motor
        else:
            print("No Motor connected to Motor Control Widget")
        self.movement_panel = movement_control_panel()

        try:
            self.set_up_motor_control_buttons()
        except AttributeError as e:
            print(e)
        
        



        layout.addWidget(self.movement_panel, 0, 0, 1, 1)

    def set_up_motor_control_buttons(self):
        '''
        Sets motor to be used and connects signals to it.
        '''

        for button in self.movement_panel.cam_indef_move_buttons:
            button.start.connect(self.motor.start_move_cam_indef)
            button.stop.connect(self.motor.end_move_cam)

        for button in self.movement_panel.grating_indef_move_buttons:
            button.start.connect(self.motor.start_move_grating)
            button.stop.connect(self.motor.end_move_grating)

        for button in self.movement_panel.cam_rel_move_buttons:
            button.rel_move.connect(self.motor.rel_move_cam)

        for button in self.movement_panel.grating_rel_buttons:
            button.rel_move.connect(self.motor.rel_move_grating)



        self.movement_panel.rel_move_cam.connect(self.motor.rel_move_cam)
        self.movement_panel.rel_move_grating.connect(self.motor.rel_move_grating)

        self.movement_panel.abort_button.clicked.connect(self.motor.abort_movement)


class movement_control_panel(QtWidgets.QGroupBox):
    '''
    Panel of simple control buttons for motors.
    '''
    rel_move_cam = QtCore.Signal(float)
    rel_move_grating = QtCore.Signal(float)
    def __init__(self):
        super().__init__(parent=None)
        self.setMinimumWidth(500)

        # Label for camera section of controls.
        section_header_font = QtGui.QFont()
        section_header_font.setPointSize(14)
        camera_section_label = QtWidgets.QLabel("Camera Motor Controls")
        camera_section_label.setMinimumHeight(14)
        camera_section_label.setFont(section_header_font)
   

        # Custom relative move widget.

        self.cam_custom_rel_widget = QtWidgets.QWidget()
        self.cam_custom_rel_layout = QtWidgets.QHBoxLayout()
        self.cam_custom_rel_widget.setLayout(self.cam_custom_rel_layout)
        self.cam_custom_rel_label = QtWidgets.QLabel("Relative Move: ")
        self.cam_custom_rel_edit = QtWidgets.QLineEdit("0")
        self.cam_custom_rel_button = QtWidgets.QPushButton("Send Move")
        self.cam_custom_rel_layout.addWidget(self.cam_custom_rel_label)
        self.cam_custom_rel_layout.addWidget(self.cam_custom_rel_edit)
        self.cam_custom_rel_layout.addWidget(self.cam_custom_rel_button)
        self.cam_custom_rel_button.clicked.connect(self.cam_rel_move_button_pressed)



        # Create Camera Button Panel.
        camera_move_buttons = QtWidgets.QWidget()
        camera_move_buttons_layout = QtWidgets.QHBoxLayout()
        camera_move_buttons.setLayout(camera_move_buttons_layout)
        c_plus_p05 = motor_rel_move_button(0.05)
        c_plus_p5 = motor_rel_move_button(0.5)
        c_plus_5 = motor_rel_move_button(5)
        positive_cam_rel_buttons = [c_plus_p05, c_plus_p5, c_plus_5]
        c_minus_p05 = motor_rel_move_button(-0.05)
        c_minus_p5 = motor_rel_move_button(-0.5)
        c_minus_5 = motor_rel_move_button(-5)
        negative_cam_rel_buttons = [c_minus_5, c_minus_p5, c_minus_p05]
        c_neg_fast = motor_move_button("<<", -2)
        c_neg_slow = motor_move_button("<", -1)
        c_pos_slow = motor_move_button(">", 1)
        c_pos_fast = motor_move_button(">>", 2)
        self.cam_indef_move_buttons = [c_neg_fast, c_neg_slow, c_pos_slow, c_pos_fast]
        self.cam_rel_move_buttons = negative_cam_rel_buttons + positive_cam_rel_buttons

        # Arrange Layout
        cam_buttons = negative_cam_rel_buttons + self.cam_indef_move_buttons + positive_cam_rel_buttons
        for button in cam_buttons:
            camera_move_buttons_layout.addWidget(button)

        grating_section_label = QtWidgets.QLabel("Grating Motor Controls")
        grating_section_label.setMinimumHeight(14)
        grating_section_label.setFont(section_header_font)


        # Custom relative move widget

        self.grating_custom_rel_widget = QtWidgets.QWidget()
        self.grating_custom_rel_layout = QtWidgets.QHBoxLayout()
        self.grating_custom_rel_widget.setLayout(self.grating_custom_rel_layout)
        self.grating_custom_rel_label = QtWidgets.QLabel("Relative Move: ")
        self.grating_custom_rel_edit = QtWidgets.QLineEdit("0")
        self.grating_custom_rel_button = QtWidgets.QPushButton("Send Move")
        self.grating_custom_rel_layout.addWidget(self.grating_custom_rel_label)
        self.grating_custom_rel_layout.addWidget(self.grating_custom_rel_edit)
        self.grating_custom_rel_layout.addWidget(self.grating_custom_rel_button)
        self.grating_custom_rel_button.clicked.connect(self.grating_rel_move_button_pressed)


        # Create Grating Button Panel
        grating_move_buttons = QtWidgets.QWidget()
        grating_move_buttons_layout = QtWidgets.QHBoxLayout()
        grating_move_buttons.setLayout(grating_move_buttons_layout)
        g_plus_p05 = motor_rel_move_button(0.05)
        g_plus_p5 = motor_rel_move_button(0.5)
        g_plus_5 = motor_rel_move_button(5)
        positive_grating_rel_buttons = [g_plus_p05, g_plus_p5, g_plus_5]
        g_minus_p05 = motor_rel_move_button(-0.05)
        g_minus_p5 = motor_rel_move_button(-0.5)
        g_minus_5 = motor_rel_move_button(-5)
        negative_grating_rel_buttons = [g_minus_5, g_minus_p5, g_minus_p05]
        g_neg_fast = motor_move_button("<<", -4)
        g_neg_slow = motor_move_button("<", -1)
        g_pos_slow = motor_move_button(">", 1)
        g_pos_fast = motor_move_button(">>", 4)
        self.grating_indef_move_buttons = [g_neg_fast, g_neg_slow, g_pos_slow, g_pos_fast]
        self.grating_rel_buttons = positive_grating_rel_buttons + negative_grating_rel_buttons
        for button in negative_grating_rel_buttons + self.grating_indef_move_buttons + positive_grating_rel_buttons:
            grating_move_buttons_layout.addWidget(button, stretch=1)
        

        # Abort Button
        self.abort_button = QtWidgets.QPushButton("ABORT")
        self.abort_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)


        layout = QtWidgets.QGridLayout()
        layout.addWidget(camera_section_label, 0, 0)
        layout.addWidget(self.cam_custom_rel_widget, 1, 0)
        layout.addWidget(camera_move_buttons, 2, 0)
        layout.addWidget(grating_section_label, 3, 0)
        layout.addWidget(self.grating_custom_rel_widget, 4, 0)
        layout.addWidget(grating_move_buttons, 5, 0)
        layout.addWidget(self.abort_button, 0, 1, 6, 1)

        
        


        self.setLayout(layout)

    def cam_rel_move_button_pressed(self):
        try:
            axis = "camera"
            distance = float(self.cam_custom_rel_edit.text())
            print(axis, distance)
            self.rel_move_cam.emit(distance)
        except Exception as e:
            print(e)

    def grating_rel_move_button_pressed(self):
        try: 
            axis = "grating"
            distance = float()
            print(axis, distance)
            self.rel_move_grating.emit(distance)
        except Exception as e:
            print(e)

        



class motor_move_button(QtWidgets.QPushButton):

    start = QtCore.Signal(float)
    stop = QtCore.Signal()

    def __init__(self, text:str, velocity: float):
        super().__init__(parent=None)
        self.setFixedHeight(55)
        self.velocity = velocity
        self.setText(text)
        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

    def _button_pressed(self):
        print("pressed")
        self.start.emit(self.velocity)

    def _button_released(self):
        print("released")
        self.stop.emit()

class motor_rel_move_button(QtWidgets.QPushButton):
    rel_move = QtCore.Signal(float)
    def __init__(self, distance: float, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        sign = "+" if distance > 0 else ""
        self.setText(f"{sign}{distance}")
        self.distance = distance
        self.clicked.connect(self.button_pressed)
    
    def button_pressed(self):
        self.rel_move.emit(self.distance)
    





if __name__ == '__main__':

    
    test_app = pg.mkQApp()
    
    window = motor_control_widget()
    window.show()

    test_app.exec()



