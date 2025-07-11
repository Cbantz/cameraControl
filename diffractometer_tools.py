import numpy as np
from pyqtgraph.Qt import QtCore
from signals import signals as sig

class Diffractometer_Tools():
    '''
    Collection of utilities to make use of the diffractometer motors and, optionally, a camera.
    '''
    def __init__(self, motor, camera):
        self.motor = motor
        self.cam = camera
        sig.cam_com_ready.connect(self._com_received)
        
        

    def _com_received(self, com):
        '''
        Runs whenever the camera gets a new center of mass processed.
        '''
        self._set_spot_pos(com)

    def _set_spot_pos(self, pos):
        '''
        Saves the last center of mass as the spot position.
        '''
        self.spot_pos = pos

