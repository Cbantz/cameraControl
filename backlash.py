import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from spot_averager import Spot_Averager
from camera import CameraController
from motor_controller import Motor_Controller
import numpy as np

class Backlash_Calibration(QtCore.QObject):

    
    def __init__(self, camera: CameraController = None, motor : Motor_Controller = None):
        super().__init__(parent=None)
        self.camera = camera
        self.motor = motor
        self.waiting_for_stage = False
        self.button = QtWidgets.QPushButton("Measure Backlash")
        self.button.clicked.connect(self.start_calibration)
        self.manual_button = QtWidgets.QPushButton("Ready For Measurement")
        self.manual_button.setMinimumSize(100,100)
        self.manual_button.clicked.connect(self.manual_button_pressed)
        
        if motor:
            self.selected_stage = self.motor.camera_axis
            self.motor.camera_move_finished.connect(self.step_move_fin)

        else:
            print("No Motor connected to Backlash Calibration")

    def start_calibration(self):
        self.generate_steps()
        self.current_step = 0
        self.positions_px = []
        self.selected_stage.move(self.movements[0], False)
        self.waiting_for_stage = True


    def generate_steps(self, num_steps_side : int = 15, range_deg : float = 10):
        self.movements = [-1, 1]
        step_size = range_deg/num_steps_side
        for step in range(num_steps_side):
            total_step = step_size * (1+step)
            self.movements.append(total_step)
            self.movements.append(-total_step)
            self.movements.append(-total_step)
            self.movements.append(total_step)


        print(self.movements)

    def move_next_step(self):
        self.current_step += 1
        print(f"Moving to Step: {self.current_step}, which is {self.movements[self.current_step]}")
        self.selected_stage.move(self.movements[self.current_step], absolute=False)
        self.waiting_for_stage = True

    def step_move_fin(self):
        if not self.waiting_for_stage:
            return
        
        print("Step Finished.")
        if self.current_step % 2 == 1:
            print("Saving Position")
            spot_avg = Spot_Averager(num_frames=5, camera=self.camera)
            spot_avg.done.connect(self.new_position_rec)
        else:
            self.move_next_step()

    def manual_button_pressed(self):
        
        self.manual_button.hide()
    
    def new_position_rec(self, pos):
        print(f"Average position saved: {pos}")
        self.positions_px.append(pos[0])
        if self.current_step == len(self.movements) - 1:
            self.save_out_results()
            return
        else:
            self.move_next_step()

    def save_out_results(self):
        movements = [self.movements[i] for i in range(len(self.movements)) if i%2==1]
        column_stack = np.column_stack((movements, self.positions_px))
        print(f"saving data. Movements: {movements}, Positions: {self.positions_px}")
        np.savetxt("backlash_data_lights_off_camera_2.csv", column_stack, delimiter=',')





    



if __name__ == "__main__":
    app = pg.mkQApp()
    bc = Backlash_Calibration()
    bc.generate_steps(num_steps_side=4, range_deg=1)
    app.exec()