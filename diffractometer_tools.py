import numpy as np
from pyqtgraph.Qt import QtCore
from signals import signals as sig

class Diffractometer_Tools():
    def __init__(self, motor, camera):
        self.motor = motor
        self.cam = camera
        sig.cam_com_ready.connect(self._com_received)
        
        

    def _com_received(self, com):
        self._set_spot_pos(com)

    def _set_spot_pos(self, pos):
        self.spot_pos = pos

