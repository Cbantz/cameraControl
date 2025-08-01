import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from motor_controller import Motor_Controller
from camera import CameraController
import numpy as np

class Distance_Scanner(QtCore.QObject):
    ready_for_frame: bool = False
    waiting_for_move_fin = False
    def __init__(self, camera : CameraController = None, motor: Motor_Controller = None):
        super().__init__(parent = None)
        self.camera = camera
        self.motor = motor
        if self.motor:
            self.motor.grating_move_finished.connect(self.motor_move_finished)
        else:
            print("No Motor connected to Distance Calibration")
        if self.camera:
            self.camera.worker.spot_tracker.focused_com_update.connect(self.spot_received)
        self.button = QtWidgets.QPushButton("Calibrate Distance")
        self.button.clicked.connect(lambda: self.calibrate())
        self.manual_button = QtWidgets.QPushButton("Ready For Measurement")
        self.manual_button.clicked.connect(self.manual_button_pressed)
        self.rel_positions = []
        self.est_ds = []

    def calibrate(self, range_angles: float = 4.5, datapoints_per_side: int = 10, automatic: bool = False):
        starting_angle = self.motor.grating_axis.position.magnitude
        self.center_x_val = self.camera.worker.spot_tracker.current_com[0]
        print(f"Starting calibration at {starting_angle}")
        self.abs_angles = []
        step_size = range_angles / datapoints_per_side
        print(f"step size: {step_size}")
        for i in range(datapoints_per_side):
            self.abs_angles.append(starting_angle - range_angles + (i * step_size))
        for i in range (datapoints_per_side):
            self.abs_angles.append(starting_angle + (i + 1)*step_size)


        print(f"Absolute Positions: {self.abs_angles}")
        self.rel_angles = [starting_angle - abs_angle for abs_angle in self.abs_angles]
        print(f"Relative Positions: {self.rel_angles}")
        self.results_widget = pg.PlotWidget()
        self.results_plot : pg.PlotDataItem = self.results_widget.plot([], [], symbol='o')
        self.results_widget.show()

        self.auto = automatic
        self.move_to_next_pos()
            
    def move_to_next_pos(self):
        self.motor.abs_move_grating(self.abs_angles[len(self.rel_positions)])
        self.waiting_for_move_fin = True


    def motor_move_finished(self):
        if self.waiting_for_move_fin:
            self.waiting_for_move_fin = False
            if self.auto:
                self.ready_for_frame = True
            else:
                self.manual_button.show()

    def spot_received(self, com : tuple):
        if self.ready_for_frame:
            rel_spot_pos = self.center_x_val - com[0]
            print(f"Set Relative Spot Position at {rel_spot_pos} ({self.center_x_val}-{com[0]})")
            self.est_ds.append(self.estimate_d(rel_spot_pos, self.rel_angles[len(self.rel_positions)] * 2))
            self.rel_positions.append(rel_spot_pos)
            
            self.ready_for_frame = False
            self.update_plot()
            if len(self.rel_positions) == len(self.abs_angles):
                combined_arrays = np.column_stack((self.abs_angles, self.rel_angles, self.rel_positions, self.est_ds))
                np.savetxt("Distance_calibration_stats_no_max.csv", combined_arrays, delimiter=',')
                return
            else:
                self.move_to_next_pos()

    def manual_button_pressed(self):
        if self.waiting_for_move_fin == False:
            self.ready_for_frame = True
            self.manual_button.hide()

    def update_plot(self):

        self.results_plot.setData(self.rel_positions, self.est_ds)

    def estimate_d(self, x: float, theta: float):
        print(f"Estimating D with x={np.abs(x)}, theta={np.abs(theta)}")
        d = np.abs(x)/(np.tan(np.radians(np.abs(theta))))
        print(f"Estimated distance: {d*4*3.67*10e-6}m")
        return d

    


            
            

        
