import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from spot_averager import Spot_Averager
from camera import CameraController
from motor_controller import Motor_Controller
import numpy as np
from datetime import datetime
import json
import enum, pint
import random


class Backlash_Calibration(QtCore.QObject):
    is_active : bool = False
    
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
        self.is_active = True
        self.generate_steps()
        self.current_step = 0
        self.positions_px = []
        # Save initial controller parameters
        # setup_dict = self.selected_stage.read_setup()
        # converted_dict = self.make_serializable(setup_dict)
        # with open('init_params.json', 'w') as file:
        #     json.dump(converted_dict, file)
        self.selected_stage.move(self.movements[0], False)
 
        self.waiting_for_stage = True


    def generate_steps(self, num_steps_side : int = 15, range_deg : float = 4):
        init_moves = [-0.5, 0.5]
        calculated_movements = []
        step_size = range_deg/num_steps_side
        for step in range(num_steps_side):
            # if step%2 == 0:
            #     total_step = round(random.uniform(0.05, 0.5), 3)
            # else:
            #     total_step = round(random.uniform(-0.5, -0.05), 3)
            total_step = 0.5
            calculated_movements.append(total_step)
            calculated_movements.append(-total_step)
            calculated_movements.append(-total_step)
            calculated_movements.append(total_step)



        self.movements = init_moves + calculated_movements

        print(self.movements)

    def move_next_step(self):
        self.current_step += 1
        try:
            print(f"Moving to Step: {self.current_step}, which is {self.movements[self.current_step]}")
            self.selected_stage.move(self.movements[self.current_step], absolute=False)
            self.waiting_for_stage = True
        except:
            print(f"Moving to Step: {self.current_step}, which is {self.movements[self.current_step]}")
            self.selected_stage.move(self.movements[self.current_step], absolute=False)
            self.waiting_for_stage = True
            

    def step_move_fin(self):
        if not self.waiting_for_stage or not self.is_active:
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
            self.is_active = False
            return
        else:
            self.move_next_step()

    def save_out_results(self):
        # Save final controller parameters
        # setup_dict = self.selected_stage.read_setup()
        # converted_dict = self.make_serializable(setup_dict)
        # with open('final_params.json', 'w') as file:
        #     json.dump(converted_dict, file)
        movements = [self.movements[i] for i in range(len(self.movements)) if i%2 == 1]
        column_stack = np.column_stack((movements, self.positions_px))
        print(f"saving data. Movements: {movements}, Positions: {self.positions_px}")
        selected_stage = "camera" if self.selected_stage == self.motor.camera_axis else "grating"
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        np.savetxt(f"{selected_stage}_{datetime_str}_repeatability_HeNe_zero_centroid.csv", column_stack, delimiter=',')


    def make_serializable(self, data: dict) -> dict:
        """Converts a dictionary with custom objects into a JSON-serializable dictionary."""
        serialized_data = {}
        for key, value in data.items():
            if isinstance(value, pint.Quantity):
                # Save pint.Quantity as a dictionary
                serialized_data[key] = {
                    'magnitude': value.magnitude,
                    'units': str(value.units)
                }
            elif isinstance(value, pint.Unit):
                # Save pint.Unit as a string
                serialized_data[key] = str(value)
            elif isinstance(value, enum.Enum):
                # Save Enum as its name (string)
                serialized_data[key] = value.name
            else:
                # For all other serializable types (int, float, etc.), just copy the value
                serialized_data[key] = value
        return serialized_data





    



if __name__ == "__main__":
    app = pg.mkQApp()
    bc = Backlash_Calibration()
    bc.generate_steps(num_steps_side=4, range_deg=1)
    app.exec()